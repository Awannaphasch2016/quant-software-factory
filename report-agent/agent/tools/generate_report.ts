import { defineTool } from "eve/tools";
import { z } from "zod";
import { discordCredentials } from "../discord-credentials.js";
import { postReport } from "../lib/discord-report.js";
import { environment, REPO_DIR } from "../sandbox.js";

/**
 * Mock datasets the tool may read. Each name is a folder under
 * `data/fixtures/` in the pinned checkout. Only listed names are accepted, so
 * a Spec cannot point the command at an arbitrary path.
 */
const DATASETS = ["demo_coop_rg_2026_10_v2"] as const;

const ISO_DATE = /^\d{4}-\d{2}-\d{2}$/;
const ACCOUNT = /^[A-Za-z0-9-]{1,32}$/;

const outputSchema = z.object({
  checks_failed: z.array(z.string()),
  checks_total: z.number(),
  /** Whether the tool posted the report to the Discord channel itself. */
  delivered_to_chat: z.boolean(),
  delivery_error: z.string().nullable(),
  error: z.string().nullable(),
  exit_code: z.number(),
  /**
   * The report, only when it was not posted to Discord (the dev channel).
   * Never shown to the model: see `toModelOutput`.
   */
  report_markdown: z.string().nullable(),
  status: z.enum(["passed", "failed", "error"]),
});

type Output = z.infer<typeof outputSchema>;

const checksSchema = z.array(z.object({ name: z.string(), passed: z.boolean() }).passthrough());

/** Resolves the bot token from the connector; it may be a value or a getter. */
async function botToken(): Promise<string> {
  const token = discordCredentials.botToken;
  const value = typeof token === "function" ? await token() : token;
  if (!value) throw new Error("No Discord bot token is configured");
  return value;
}

/** The Discord channel id of the calling session, when it came from Discord. */
function discordChannelId(channel: { kind: string; metadata: Readonly<Record<string, unknown>> }) {
  const id = channel.metadata.channelId;
  return channel.kind.endsWith("discord") && typeof id === "string" ? id : null;
}

/**
 * Builds the Returns & Transactions report from mock data in the sandbox.
 *
 * @remarks
 * Runs the existing `returns_transactions` command from the pinned checkout,
 * so every figure comes from tested Python code. The model never sees the
 * report: when the request came from Discord, this tool posts the report to
 * the channel itself (with `report.md` attached), and `toModelOutput` gives
 * the model only the status and the check names. This is the same boundary
 * `private_run` keeps for private data (Software Design section 2), applied
 * here to the chat path. The tool still reads mock fixtures only.
 */
export default defineTool({
  description:
    "Build the Returns & Transactions report from a mock dataset and run every number and writing check. When the request came from Discord, the tool posts the report to the channel itself; you only get the status and check names. Use it for every report request; never write report figures yourself.",
  inputSchema: z.object({
    account: z.string().regex(ACCOUNT).describe("Account number from the Spec, e.g. DEMO-0001"),
    as_of: z.string().regex(ISO_DATE).describe("As-of date from the Spec, YYYY-MM-DD, e.g. 2026-10-30"),
    dataset: z.enum(DATASETS).describe("Mock dataset named in the Spec's Data Sources"),
    opening: z
      .string()
      .regex(ISO_DATE)
      .describe("Opening date from the Spec, YYYY-MM-DD, e.g. 2026-09-30"),
  }),
  label: {
    complete: (input, output) =>
      `Report for ${input.account}: ${output.status}, ${output.checks_failed.length} of ${output.checks_total} checks failed`,
    start: (input) => `Building the report for ${input.account}`,
  },
  outputSchema,
  toModelOutput: (output: Output) => ({
    type: "json",
    value: {
      checks_failed: output.checks_failed,
      checks_total: output.checks_total,
      delivered_to_chat: output.delivered_to_chat,
      delivery_error: output.delivery_error,
      error: output.error,
      exit_code: output.exit_code,
      status: output.status,
    },
  }),
  async execute(input, ctx): Promise<Output> {
    const sandbox = await ctx.getSandbox(environment);
    // The report code uses the output folder's name as the Report ID, so the
    // folder is named after the dataset, inside a unique work folder.
    const work = `/tmp/report-${crypto.randomUUID()}`;
    const out = `${work}/${input.dataset}`;
    let report: string | null = null;
    let result: Output;
    try {
      const run = await sandbox.run({
        command: [
          `cd ${REPO_DIR}`,
          `PYTHONPATH=src python3 -m quant_software_factory.reporting.returns_transactions data/fixtures/${input.dataset} ${out} --account '${input.account}' --opening ${input.opening} --as-of ${input.as_of}`,
        ].join(" && "),
      });

      const checksFile = await sandbox.run({ command: `cat ${out}/checks.json` });
      if (checksFile.exitCode !== 0) {
        return {
          checks_failed: [],
          checks_total: 0,
          delivered_to_chat: false,
          delivery_error: null,
          error: String(run.stderr || run.stdout).trim().slice(0, 2000),
          exit_code: run.exitCode,
          report_markdown: null,
          status: "error",
        };
      }
      const checks = checksSchema.parse(JSON.parse(String(checksFile.stdout)));
      const failed = checks.filter((c) => !c.passed).map((c) => c.name);

      if (run.exitCode === 0) {
        const reportFile = await sandbox.run({ command: `cat ${out}/report.md` });
        report = reportFile.exitCode === 0 ? String(reportFile.stdout) : null;
      }
      result = {
        checks_failed: failed,
        checks_total: checks.length,
        delivered_to_chat: false,
        delivery_error: null,
        error: null,
        exit_code: run.exitCode,
        report_markdown: null,
        status: run.exitCode === 0 && report !== null ? "passed" : "failed",
      };
    } finally {
      await sandbox.run({ command: `rm -rf ${work}` });
    }

    if (result.status !== "passed" || report === null) return result;

    const channelId = discordChannelId(ctx.channel);
    if (channelId === null) {
      // Dev channel (eve TUI or remote): no chat to post to, so the report
      // stays in the tool output, which the model does not see.
      return { ...result, report_markdown: report };
    }
    try {
      const passed = result.checks_total - result.checks_failed.length;
      await postReport({
        botToken: await botToken(),
        channelId,
        filename: `${input.dataset}.md`,
        markdown: report,
        summary: `Report for ${input.account}, ${input.opening} to ${input.as_of}: ${passed} of ${result.checks_total} checks passed. The full report is attached and follows below.`,
      });
      return { ...result, delivered_to_chat: true };
    } catch (error) {
      const message = error instanceof Error ? error.message : String(error);
      return { ...result, delivery_error: message.slice(0, 500) };
    }
  },
});
