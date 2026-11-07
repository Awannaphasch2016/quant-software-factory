# Remote script execution

This is the operator guide for running one approved Python script on a
temporary GitHub-hosted Linux runner and storing the execution record in the
private Vercel Blob store. It is an execution path. It does not compare the
script output with an expected value, and it does not produce a correctness
verdict.

## What is already true

- Maximum drawdown is implemented by `calculate_max_drawdown` in
  `src/quant_software_factory/risk.py`. That function returns a float. This
  work does not change it. It comes from draft pull request #2
  (`feat/max-drawdown-issue-1`), which is not merged. `main` is still the
  initial README commit.
- The allowlisted entry point is `scripts/calculate_max_drawdown.py`. It reads
  one JSON object from stdin and writes one JSON object to stdout, for example
  `{"max_drawdown": 0.25}` for `{"equity_curve": [100, 120, 90, 110]}`. `0.25`
  is the function's mathematical result for that input. The remote runner
  records the script's actual JSON. It does not check that number.
- The private Blob store exists: name `quant-execution-results`, id
  `store_CEauyrab8003cHZO`, team `anak2` (`team_HH56QrlGNZZs3DWHlokF5NlZ`),
  region `iad1`, access `private`. Creating the store did not return a
  read-write token.

## What is not done

Dispatch and storage have not been run. Do not treat a green local test as an
upload. Storage stays failed until a GitHub Actions run actually puts the
record and reads it back.

1. This workflow is not on the default branch `main`. GitHub only accepts
   `workflow_dispatch` for a workflow file that exists on the default branch.
   Merging requires a person. This pull request is stacked on the unmerged
   drawdown branch so the entry point can call the existing function. Merging
   it into that branch does not publish the workflow and does not merge pull
   request #2.
2. `BLOB_READ_WRITE_TOKEN` is not configured. The cloud agent integration
   cannot list or write Actions secrets (the secrets API returns HTTP 403),
   and it has no dispatch tool. Do not assume Vercel OIDC works on a
   GitHub-hosted runner. OIDC tokens are for code running on Vercel. This
   uploader passes the static store token explicitly and removes
   `VERCEL_OIDC_TOKEN` and `BLOB_STORE_ID` from the upload process before it
   calls the SDK.

## Request

`schema_version` is the integer `1`. From the workflow it is the string `1`,
which the runner accepts only in that exact form.

| Field | Required value |
| --- | --- |
| `request_id` | Caller-chosen id, 1–128 characters: letters, digits, `.`, `_`, `:`, `-` |
| `repository` | `Awannaphasch2016/quant-software-factory` |
| `code_sha` | Full 40-character lowercase SHA of the approved commit |
| `script_path` | An allowlisted repo-relative `.py` path |
| `input` | One finite JSON value. The drawdown script requires `{"equity_curve": [...]}` |

The first intended input is:

```json
{"equity_curve": [100, 120, 90, 110]}
```

The checked-in allowlist has one path: `scripts/calculate_max_drawdown.py`.
The runner rejects every other path, including shell text, absolute paths,
`..`, and any symlink on the way to the file. It does not install the
candidate project and it does not run candidate dependency commands. Imports
come from that commit's `src` directory through a trusted launcher and
`python -I`.

## Trust boundaries

- The dispatch ref must be `refs/heads/main`. That check lives in the approved
  workflow. A different branch can still contain a different workflow file, so
  the real protection for the token is the GitHub Environment below.
- The execute job checks out the trusted workflow SHA and the approved
  `code_sha` into separate directories. It drops persisted git credentials
  before the script starts. Its child process gets a fresh environment with no
  `BLOB_READ_WRITE_TOKEN`, `GITHUB_TOKEN`, or OIDC token.
- The upload job is a new virtual machine. It checks out only the trusted
  workflow SHA, never `code_sha`, and it does not run the candidate script.
  `BLOB_READ_WRITE_TOKEN` is an environment secret on that job only.
- The record path is `executions/v1/Awannaphasch2016/quant-software-factory/<run_id>/<attempt>/execution.json`.
  Uploads set `access: "private"`, `addRandomSuffix: false`, and
  `allowOverwrite: false`. The job then reads the object back with
  `get(..., { access: "private", useCache: false })` and compares bytes.
  `storage.status` is `stored` only when that read-back matches.
- A missing token is `storage.status: storage_failed` with category
  `missing_credentials`. The computation section still reports the script
  outcome. The Actions artifact `execution-record` is a recovery copy when the
  execute job was able to upload it. Cancellation or a lost VM can leave
  neither an artifact nor a blob. The receipt says the artifact is not
  guaranteed.
- Records are not committed back to the repository.

Candidate limits, enforced by the trusted runner: 256 KiB of input, 256 KiB of
stdout, 256 KiB of stderr, and 30 seconds. Non-finite JSON is rejected. A
nonzero exit is recorded as `script_failed` with the exit code. The runner
does not invent a Python exception type from that code. Stdout must be exactly
one finite JSON value or the result is null and the error says the output was
malformed.

## Configure the secret

Do this only after the workflow file is on `main`, and before the first
dispatch. Create the environment first and restrict it to `main`, then put the
token on that environment. Do not also create a repository-level secret of the
same name. A repository secret can be read by any workflow that names it,
including a workflow file that was dispatched from another branch.

The token has to be a read-write token for store `quant-execution-results`
(`store_CEauyrab8003cHZO`) only. The dashboard path that issues it is to open
that store in team `anak2` and connect it to a Vercel project, which adds
`BLOB_READ_WRITE_TOKEN` to the project. Copy that value from the project
environment screen. Do not run `vercel env pull` in an agent workspace, and do
not paste the token into a shell argument, a commit, or a log.

A person with permission to administer this private repository then creates
the environment and the secret. The GitHub CLI reads the secret from stdin:

```bash
gh api --method PUT \
  repos/Awannaphasch2016/quant-software-factory/environments/execution-upload \
  --input - <<'EOF'
{"deployment_branch_policy":{"protected_branches":false,"custom_branch_policies":true}}
EOF

gh api --method POST \
  repos/Awannaphasch2016/quant-software-factory/environments/execution-upload/deployment-branch-policies \
  -f name=main -f type=branch

gh secret set BLOB_READ_WRITE_TOKEN \
  --env execution-upload \
  --repo Awannaphasch2016/quant-software-factory
```

The last command prompts for the value. Confirm the environment's deployment
branch policy lists only `main` before you enter it.

This cloud agent's `gh` credential cannot perform those writes.

## Dispatch

After the workflow is on `main` and the environment secret exists, dispatch
from `main` with `gh`. `--ref` must be `main`. `code_sha` must be the full SHA
of a commit that contains both `src/quant_software_factory/risk.py` and
`scripts/calculate_max_drawdown.py`. That commit is not on `main` until the
drawdown work and this entry point have been merged there. The current `main`
SHA `528dcdc99f76899a2bb1421f9300a8f3c93918e5` does not contain the function.
The drawdown branch tip `6614532018194a15b35eee9809416acf1dcd6495` contains the
function and not this entry point.

```bash
gh workflow run execute-script.yml \
  --ref main \
  --repo Awannaphasch2016/quant-software-factory \
  -f schema_version=1 \
  -f request_id="mdd-first-run-1" \
  -f repository="Awannaphasch2016/quant-software-factory" \
  -f code_sha="<40-lowercase-hex-sha>" \
  -f script_path="scripts/calculate_max_drawdown.py" \
  -f input_json='{"equity_curve":[100,120,90,110]}'
```

Watch the run:

```bash
gh run list --workflow execute-script.yml --repo Awannaphasch2016/quant-software-factory --limit 1
gh run watch --repo Awannaphasch2016/quant-software-factory
```

The upload job summary is the receipt. Computation and storage are separate
fields. The run link is
`https://github.com/Awannaphasch2016/quant-software-factory/actions/runs/<run_id>`.

The returned blob URL uses a `*.private.blob.vercel-storage.com` host. It is
not anonymously readable. An operator who already has the store token can
prove the bytes with the SDK (this is not run from the candidate script):

```javascript
import { get } from "@vercel/blob";

const result = await get(pathname, {
  access: "private",
  token: process.env.BLOB_READ_WRITE_TOKEN,
  useCache: false,
});
```

`pathname` is the receipt's pathname. Compare the SHA-256 of the bytes with
the receipt.

An optional short-lived URL uses the documented SDK methods `issueSignedToken`
and `presignUrl` from `@vercel/blob`. Scope `operations` to `["get"]`, set
`pathname` to that same object, and keep `validUntil` within the SDK's maximum
of seven days. `presignUrl` needs `operation: "get"`, the same pathname, and
`access: "private"`. The signing token's `clientSigningToken` is a secret.
The workflow does not mint these URLs, because they would land in the job log.

## Local checks

The execution tests are ordinary unit and integration tests of the runner,
the entry point, the workflow file, and the uploader. They do not contact
GitHub Actions or Vercel Blob.

```bash
pip install -e ".[dev]"
ruff check .
ruff format --check .
mypy
pytest
node --test execution/uploader/upload_record.test.mjs
```

`pytest` also runs the Node tests.
