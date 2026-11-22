import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { join } from "node:path";
import { test } from "node:test";
import { alignTable, fenceTables, postReport, splitForDiscord } from "../agent/lib/discord-report.ts";

const REPORT = readFileSync(
  join(import.meta.dirname, "../../reports/demo_coop_rg_2026_10_v2/report.md"),
  "utf8"
);

/** Table cells and plain lines, ignoring padding, separator width and fences. */
function content(text: string): string[] {
  return text
    .split("\n")
    .filter((line) => line.trim() !== "" && line !== "```")
    .map((line) =>
      line.startsWith("|")
        ? line
            .split("|")
            .map((cell) => cell.trim().replace(/^:?-+:?$/, "---"))
            .join("|")
        : line
    );
}

test("alignTable pads columns and right-aligns ---: columns", () => {
  const rows = alignTable(["| KPI | Value |", "| --- | ---: |", "| Cash | 267,398.00 |", "| Total P/L | 9.00 |"]);
  assert.deepEqual(rows, [
    "| KPI       |      Value |",
    "| --------- | ---------- |",
    "| Cash      | 267,398.00 |",
    "| Total P/L |       9.00 |",
  ]);
});

test("the Discord messages keep every line and cell of report.md", () => {
  const messages = splitForDiscord(fenceTables(REPORT));
  assert.deepEqual(content(messages.join("\n")), content(REPORT));
});

test("every message fits Discord and has balanced code fences", () => {
  const messages = splitForDiscord(fenceTables(REPORT));
  assert.ok(messages.length >= 1);
  for (const message of messages) {
    assert.ok(message.length <= 2000, `message is ${message.length} characters`);
    assert.equal((message.match(/^```$/gm) ?? []).length % 2, 0);
  }
});

test("a block over the limit is an error, not a cut table", () => {
  const big = `## T\n\n${Array.from({ length: 200 }, (_, i) => `| row ${i} | value |`).join("\n")}`;
  assert.throws(() => splitForDiscord(fenceTables(big)), /Discord limit/);
});

test("postReport attaches report.md first, then posts the text, retrying on 429", async () => {
  const calls: { url: string; form: boolean; content?: string }[] = [];
  let rateLimited = false;
  const fakeFetch = (async (url: string | URL | Request, init?: RequestInit) => {
    if (!rateLimited && calls.length === 1) {
      rateLimited = true;
      return new Response(JSON.stringify({ retry_after: 0.01 }), { status: 429 });
    }
    const form = init?.body instanceof FormData;
    const content = form ? undefined : (JSON.parse(String(init?.body)) as { content: string }).content;
    calls.push({ content, form, url: String(url) });
    return new Response("{}", { status: 200 });
  }) as typeof fetch;

  await postReport({
    botToken: "test-token",
    channelId: "123",
    fetchImpl: fakeFetch,
    filename: "report.md",
    markdown: REPORT,
    summary: "summary",
  });

  const texts = splitForDiscord(fenceTables(REPORT));
  assert.equal(calls.length, 1 + texts.length);
  assert.ok(calls[0]?.form);
  assert.ok(calls.every((c) => c.url === "https://discord.com/api/v10/channels/123/messages"));
  assert.deepEqual(
    calls.slice(1).map((c) => c.content),
    texts
  );
});

test("postReport fails on a non-429 error", async () => {
  const fakeFetch = (async () => new Response("{}", { status: 403 })) as typeof fetch;
  await assert.rejects(
    postReport({
      botToken: "t",
      channelId: "1",
      fetchImpl: fakeFetch,
      filename: "r.md",
      markdown: REPORT,
      summary: "s",
    }),
    /HTTP 403/
  );
});
