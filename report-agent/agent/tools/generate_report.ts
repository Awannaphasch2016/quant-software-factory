import { defineTool } from "eve/tools";
import { z } from "zod";
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
  exit_code: z.number(),
  report_markdown: z.string().nullable(),
  status: z.enum(["passed", "failed", "error"]),
  error: z.string().nullable(),
});

const checksSchema = z.array(
  z.object({ name: z.string(), passed: z.boolean() }).passthrough()
);

/**
 * Builds the Returns & Transactions report from mock data in the sandbox.
 *
 * @remarks
 * Runs the existing `returns_transactions` command from the pinned checkout,
 * so every figure comes from tested Python code, not from the model. This
 * tool is for mock fixtures only: it returns the full report to the model.
 * Private data goes through `private_run` in the trusted zone instead, which
 * returns check names and pass/fail only (Software Design section 2).
 */
export default defineTool({
  description:
    "Build the Returns & Transactions report from a mock dataset and return the report Markdown with the result of every number and writing check. Use it for every report request; never write report figures yourself.",
  inputSchema: z.object({
    account: z
      .string()
      .regex(ACCOUNT)
      .describe("Account number from the Spec, e.g. DEMO-0001"),
    as_of: z
      .string()
      .regex(ISO_DATE)
      .describe("As-of date from the Spec, YYYY-MM-DD, e.g. 2026-10-30"),
    dataset: z
      .enum(DATASETS)
      .describe("Mock dataset named in the Spec's Data Sources"),
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
  async execute(input, ctx) {
    const sandbox = await ctx.getSandbox(environment);
    // The report code uses the output folder's name as the Report ID, so the
    // folder is named after the dataset, inside a unique work folder.
    const work = `/tmp/report-${crypto.randomUUID()}`;
    const out = `${work}/${input.dataset}`;
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
          error: String(run.stderr || run.stdout).trim().slice(0, 2000),
          exit_code: run.exitCode,
          report_markdown: null,
          status: "error" as const,
        };
      }
      const checks = checksSchema.parse(JSON.parse(String(checksFile.stdout)));
      const failed = checks.filter((c) => !c.passed).map((c) => c.name);

      let report: string | null = null;
      if (run.exitCode === 0) {
        const reportFile = await sandbox.run({ command: `cat ${out}/report.md` });
        report = reportFile.exitCode === 0 ? String(reportFile.stdout) : null;
      }

      return {
        checks_failed: failed,
        checks_total: checks.length,
        error: null,
        exit_code: run.exitCode,
        report_markdown: report,
        status:
          run.exitCode === 0 && report !== null ? ("passed" as const) : ("failed" as const),
      };
    } finally {
      await sandbox.run({ command: `rm -rf ${work}` });
    }
  },
});
