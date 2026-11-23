import { defineSandbox } from "eve/sandbox";
import { VercelSandbox } from "eve/sandbox/vercel";

/** Public repository that holds the report code and the mock fixtures. */
const REPO_URL =
  "https://github.com/Awannaphasch2016/quant-software-factory.git";

/**
 * Commit of the report code the sandbox runs.
 *
 * @remarks
 * Pinned so a report is reproducible: changing the report code needs a new
 * commit here and a redeploy.
 */
export const REPO_REF = "6e31548cea40aa6f779ef44dc47bb2dd5cd89690";

/**
 * Python with the report package's one runtime dependency (`fpdf2`, used only
 * to draw the Grid report PDF). eve's default image has Python 3 but no pip,
 * so `prepare` builds this virtual environment, as eve's sandbox docs advise.
 */
export const PYTHON = "/workspace/.venv/bin/python";

/** Installed in `prepare`; pinned to the version in `pyproject.toml`. */
const PREPARE_COMMANDS = [
  "sudo apt-get update -qq && sudo DEBIAN_FRONTEND=noninteractive apt-get install -y -qq python3-venv",
  "python3 -m venv /workspace/.venv",
  `${PYTHON} -m pip install --quiet fpdf2==2.8.9`,
];

/** Where the build-time snapshot keeps the checkout. */
export const REPO_DIR = "/workspace/qsf";

/**
 * Vercel Sandbox with the report code cloned once at build time.
 *
 * @remarks
 * The install and the clone run in `prepare`, so they are captured in the
 * snapshot every session starts from. Sessions then open with all outbound
 * network denied: the report needs only the files already in the snapshot.
 */
export const environment = VercelSandbox.environment({
  prepare: async (sandbox) => {
    const commands = [
      ...PREPARE_COMMANDS,
      `git clone --quiet ${REPO_URL} ${REPO_DIR} && git -C ${REPO_DIR} checkout --quiet ${REPO_REF}`,
    ];
    for (const command of commands) {
      const result = await sandbox.run({ command });
      if (result.exitCode !== 0) {
        throw new Error(
          `Sandbox setup failed at "${command}" (exit ${result.exitCode}): ${String(
            result.stderr || result.stdout
          ).trim()}`
        );
      }
    }
  },
});

export default defineSandbox(() =>
  environment.open({ networkPolicy: "deny-all" })
);
