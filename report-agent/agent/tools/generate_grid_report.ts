import { defineTool } from "eve/tools";
import { z } from "zod";
import { postFile } from "../lib/discord-report.js";
import { ACCOUNT, botToken, checksSchema, discordChannelId, ISO_DATE } from "../lib/report-tool.js";
import { environment, PYTHON, REPO_DIR } from "../sandbox.js";

/** Mock Reverse Grid datasets under `data/fixtures/` in the pinned checkout. */
const DATASETS = ["demo_grid_2026_11"] as const;

const outputSchema = z.object({
  checks_failed: z.array(z.string()),
  checks_total: z.number(),
  /** Whether the tool posted `report.pdf` to the Discord channel itself. */
  delivered_to_chat: z.boolean(),
  delivery_error: z.string().nullable(),
  error: z.string().nullable(),
  exit_code: z.number(),
  /** PDF size in bytes when it was built; the PDF itself never reaches the model. */
  pdf_bytes: z.number().nullable(),
  status: z.enum(["passed", "failed", "error"]),
});

type Output = z.infer<typeof outputSchema>;

/** The generation time printed in the report footer, to the second, UTC. */
function nowUtc(): string {
  return `${new Date().toISOString().slice(0, 19)}Z`;
}

/**
 * Builds the Grid Trade Performance report (5-page PDF) from mock data.
 *
 * @remarks
 * Runs `grid_performance` from the pinned checkout with the sandbox's virtual
 * environment, which holds `fpdf2`. Every figure comes from that tested code.
 * In Discord the tool posts `report.pdf` itself; the model gets only the
 * status, the check names and the file size.
 */
export default defineTool({
  description:
    "Build the Grid Trade Performance report (a 5-page PDF for a Reverse Grid account) from a mock dataset and run every check. When the request came from Discord, the tool posts the PDF to the channel itself; you only get the status and check names. Never write report figures yourself.",
  inputSchema: z.object({
    account: z.string().regex(ACCOUNT).describe("Account number from the Spec, e.g. DEMO-0001"),
    as_of: z.string().regex(ISO_DATE).describe("As-of date from the Spec, YYYY-MM-DD, e.g. 2026-11-06"),
    dataset: z.enum(DATASETS).describe("Mock dataset named in the Spec, e.g. demo_grid_2026_11"),
  }),
  label: {
    complete: (input, output) =>
      `Grid report for ${input.account}: ${output.status}, ${output.checks_failed.length} of ${output.checks_total} checks failed`,
    start: (input) => `Building the Grid report for ${input.account}`,
  },
  outputSchema,
  toModelOutput: (output: Output) => ({ type: "json", value: output }),
  async execute(input, ctx): Promise<Output> {
    const sandbox = await ctx.getSandbox(environment);
    const work = `/tmp/report-${crypto.randomUUID()}`;
    const out = `${work}/${input.dataset}`;
    const base = { checks_failed: [], checks_total: 0, delivered_to_chat: false, delivery_error: null, error: null, pdf_bytes: null };
    try {
      const run = await sandbox.run({
        command: `${PYTHON} -m quant_software_factory.reporting.grid_performance data/fixtures/${input.dataset} ${out} --account '${input.account}' --as-of ${input.as_of} --generated-at ${nowUtc()}`,
        env: { PYTHONPATH: "src" },
        workingDirectory: REPO_DIR,
      });
      const [checksText, pdf] = await Promise.all([
        sandbox.readTextFile({ path: `${out}/checks.json` }),
        sandbox.readBinaryFile({ path: `${out}/report.pdf` }),
      ]);
      if (checksText === null) {
        const error = (run.stderr || run.stdout).trim().slice(0, 2000);
        return { ...base, error, exit_code: run.exitCode, status: "error" };
      }
      const checks = checksSchema.parse(JSON.parse(checksText));
      const result: Output = {
        ...base,
        checks_failed: checks.filter((c) => !c.passed).map((c) => c.name),
        checks_total: checks.length,
        exit_code: run.exitCode,
        status: run.exitCode === 0 && pdf !== null ? "passed" : "failed",
      };
      if (result.status !== "passed" || pdf === null) return result;
      result.pdf_bytes = pdf.byteLength;

      const channelId = discordChannelId(ctx.channel);
      if (channelId === null) return result;
      try {
        const passed = result.checks_total - result.checks_failed.length;
        await postFile({
          botToken: await botToken(),
          channelId,
          content: pdf,
          contentType: "application/pdf",
          filename: `${input.dataset}.pdf`,
          summary: `Grid Trade Performance for ${input.account}, as of ${input.as_of}: ${passed} of ${result.checks_total} checks passed. The 5-page PDF is attached.`,
        });
        return { ...result, delivered_to_chat: true };
      } catch (error) {
        const message = error instanceof Error ? error.message : String(error);
        return { ...result, delivery_error: message.slice(0, 500) };
      }
    } finally {
      await sandbox.removePath({ force: true, path: work, recursive: true });
    }
  },
});
