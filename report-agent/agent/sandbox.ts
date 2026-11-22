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
 * commit here and a redeploy. The code is standard-library Python, so the
 * default eve image (Python 3, no pip) runs it without installing anything.
 */
export const REPO_REF = "a1e147a7629753e8d354706831039b44967b9782";

/** Where the build-time snapshot keeps the checkout. */
export const REPO_DIR = "/workspace/qsf";

/**
 * Vercel Sandbox with the report code cloned once at build time.
 *
 * @remarks
 * The clone runs in `prepare`, so it is captured in the snapshot every
 * session starts from. Sessions then open with all outbound network denied:
 * the report needs only the files already in the snapshot.
 */
export const environment = VercelSandbox.environment({
  prepare: async (sandbox) => {
    const result = await sandbox.run({
      command: `git clone --quiet ${REPO_URL} ${REPO_DIR} && git -C ${REPO_DIR} checkout --quiet ${REPO_REF}`,
    });
    if (result.exitCode !== 0) {
      throw new Error(
        `Cloning the report code failed (exit ${result.exitCode}): ${String(
          result.stderr || result.stdout
        ).trim()}`
      );
    }
  },
});

export default defineSandbox(() =>
  environment.open({ networkPolicy: "deny-all" })
);
