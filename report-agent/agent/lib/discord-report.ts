/**
 * Posts a generated report to a Discord channel without passing it through
 * the model.
 *
 * @remarks
 * Pure code: no figure is computed or reworded here. The only change to the
 * report text is display formatting, because Discord does not render Markdown
 * tables: each run of table lines is wrapped in a code block so the columns
 * stay aligned. The unchanged `report.md` is attached as a file.
 */

const API_BASE = "https://discord.com/api/v10";

/** Discord's message limit is 2,000 characters; keep a margin. */
const CHUNK_LIMIT = 1900;

const FENCE = "```";
const NO_MENTIONS = { parse: [] as string[] };

const SEPARATOR_CELL = /^:?-+:?$/;

function cells(line: string): string[] {
  return line.trim().replace(/^\|/, "").replace(/\|$/, "").split("|").map((c) => c.trim());
}

/**
 * Pads the cells of one Markdown table so its columns line up in a
 * monospaced code block. Only spaces and separator dashes change; every cell
 * value is kept as written. Columns marked `---:` are right-aligned.
 */
export function alignTable(lines: readonly string[]): string[] {
  const rows = lines.map(cells);
  const isSeparator = rows.map((row) => row.every((c) => SEPARATOR_CELL.test(c)));
  const columns = Math.max(...rows.map((row) => row.length));
  const separator = rows.find((_, i) => isSeparator[i]);
  const right = Array.from({ length: columns }, (_, i) => separator?.[i]?.endsWith(":") ?? false);
  const widths = Array.from({ length: columns }, (_, i) =>
    Math.max(3, ...rows.filter((_, r) => !isSeparator[r]).map((row) => (row[i] ?? "").length))
  );
  return rows.map((row, r) => {
    const padded = widths.map((width, i) => {
      if (isSeparator[r]) return "-".repeat(width);
      const value = row[i] ?? "";
      return right[i] ? value.padStart(width) : value.padEnd(width);
    });
    return `| ${padded.join(" | ")} |`;
  });
}

/**
 * Wraps each run of Markdown table lines (`| ... |`) in a code block, with
 * the columns padded by {@link alignTable}.
 */
export function fenceTables(markdown: string): string {
  const out: string[] = [];
  let table: string[] = [];
  const flush = () => {
    if (table.length > 0) out.push(FENCE, ...alignTable(table), FENCE);
    table = [];
  };
  for (const line of markdown.split("\n")) {
    if (line.startsWith("|")) {
      table.push(line);
    } else {
      flush();
      out.push(line);
    }
  }
  flush();
  return out.join("\n");
}

/**
 * Splits formatted text into messages of at most `limit` characters, at blank
 * lines. A fenced table from {@link fenceTables} has no blank lines, so it is
 * never cut. A single block longer than `limit` is an error: the caller
 * reports it, and `report.md` has already been attached by then.
 */
export function splitForDiscord(text: string, limit = CHUNK_LIMIT): string[] {
  const messages: string[] = [];
  let current = "";
  for (const block of text.split(/\n\s*\n/).map((b) => b.trim()).filter(Boolean)) {
    if (block.length > limit) {
      throw new Error(`A report block is ${block.length} characters, over the ${limit}-character Discord limit`);
    }
    if (current && current.length + 2 + block.length > limit) {
      messages.push(current);
      current = block;
    } else {
      current = current ? `${current}\n\n${block}` : block;
    }
  }
  if (current) messages.push(current);
  return messages;
}

export interface PostReportOptions {
  readonly botToken: string;
  readonly channelId: string;
  /** First message, sent with `report.md` attached. */
  readonly summary: string;
  readonly markdown: string;
  readonly filename: string;
  /** For tests; defaults to the global `fetch`. */
  readonly fetchImpl?: typeof fetch;
}

export interface PostFileOptions {
  readonly botToken: string;
  readonly channelId: string;
  /** Message text sent with the file. */
  readonly summary: string;
  readonly filename: string;
  readonly content: Uint8Array | string;
  readonly contentType: string;
  /** For tests; defaults to the global `fetch`. */
  readonly fetchImpl?: typeof fetch;
}

async function send(
  fetchImpl: typeof fetch,
  url: string,
  init: () => RequestInit
): Promise<void> {
  for (let attempt = 0; attempt < 3; attempt += 1) {
    const response = await fetchImpl(url, init());
    if (response.ok) return;
    if (response.status === 429) {
      const body = (await response.json().catch(() => ({}))) as { retry_after?: number };
      const waitMs = Math.min(Math.ceil((body.retry_after ?? 1) * 1000), 5000);
      await new Promise((resolve) => setTimeout(resolve, waitMs));
      continue;
    }
    throw new Error(`Discord returned HTTP ${response.status}`);
  }
  throw new Error("Discord kept rate-limiting the report messages");
}

function messagesUrl(channelId: string): string {
  return `${API_BASE}/channels/${encodeURIComponent(channelId)}/messages`;
}

/** Posts one message with one file attached, byte for byte. */
export async function postFile(options: PostFileOptions): Promise<void> {
  const fetchImpl = options.fetchImpl ?? fetch;
  await send(fetchImpl, messagesUrl(options.channelId), () => {
    const form = new FormData();
    form.append(
      "payload_json",
      JSON.stringify({
        allowed_mentions: NO_MENTIONS,
        attachments: [{ filename: options.filename, id: 0 }],
        content: options.summary,
      })
    );
    const part = typeof options.content === "string" ? options.content : new Uint8Array(options.content);
    form.append("files[0]", new Blob([part], { type: options.contentType }), options.filename);
    return { body: form, headers: { authorization: `Bot ${options.botToken}` }, method: "POST" };
  });
}

/**
 * Posts the summary with `report.md` attached, then the report text with
 * tables fenced, split into as many messages as needed.
 */
export async function postReport(options: PostReportOptions): Promise<void> {
  const fetchImpl = options.fetchImpl ?? fetch;
  const url = messagesUrl(options.channelId);
  const auth = { authorization: `Bot ${options.botToken}` };

  await postFile({
    botToken: options.botToken,
    channelId: options.channelId,
    content: options.markdown,
    contentType: "text/markdown",
    fetchImpl,
    filename: options.filename,
    summary: options.summary,
  });

  const chunks = splitForDiscord(fenceTables(options.markdown));
  for (const content of chunks) {
    await send(fetchImpl, url, () => ({
      body: JSON.stringify({ allowed_mentions: NO_MENTIONS, content }),
      headers: { ...auth, "content-type": "application/json" },
      method: "POST",
    }));
  }
}
