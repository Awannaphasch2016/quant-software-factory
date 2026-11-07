import { createHash } from "node:crypto";
import { appendFile, readFile, writeFile } from "node:fs/promises";
import path from "node:path";
import { fileURLToPath, pathToFileURL } from "node:url";

const RUN_ID = /^[1-9][0-9]{0,19}$/;
export const FIXED_REPOSITORY = "Awannaphasch2016/quant-software-factory";

const here = path.dirname(fileURLToPath(import.meta.url));

export function sha256(bytes) {
  return createHash("sha256").update(bytes).digest("hex");
}

export function executionBlobPath(repository, runId, attempt) {
  if (repository !== FIXED_REPOSITORY) {
    return null;
  }
  if (!RUN_ID.test(runId) || !RUN_ID.test(attempt)) {
    return null;
  }
  return `executions/v1/${repository}/${runId}/${attempt}/execution.json`;
}

export function isPrivateBlobUrl(value) {
  if (typeof value !== "string") {
    return false;
  }
  try {
    const url = new URL(value);
    return (
      url.protocol === "https:" &&
      url.hostname.endsWith(".private.blob.vercel-storage.com")
    );
  } catch {
    return false;
  }
}

export function computationFromRecord(record) {
  const prepareStatus = record?.prepare?.status;
  const executionStatus = record?.execution?.status;
  if (prepareStatus === "preparation_failed") {
    return {
      status: "failed",
      exit_code: null,
      result: null,
      error: record.prepare.error ?? null,
    };
  }
  if (executionStatus === "succeeded") {
    return {
      status: "succeeded",
      exit_code: record.execution.exit_code ?? null,
      result: record.execution.result ?? null,
      error: null,
    };
  }
  return {
    status: "failed",
    exit_code: record?.execution?.exit_code ?? null,
    result: null,
    error: record?.execution?.error ?? record?.prepare?.error ?? null,
  };
}

function errorBody(category, message, details) {
  const body = { category, message };
  if (details && Object.keys(details).length > 0) {
    body.details = details;
  }
  return body;
}

function redact(text, token) {
  let output = String(text ?? "");
  if (token) {
    output = output.split(token).join("[redacted]");
  }
  return output.slice(0, 500);
}

async function readAll(stream) {
  const reader = stream.getReader();
  const chunks = [];
  while (true) {
    const next = await reader.read();
    if (next.done) {
      break;
    }
    chunks.push(Buffer.from(next.value));
  }
  return Buffer.concat(chunks);
}

export async function uploadRecord(options) {
  const repository = options.repository;
  const runId = options.runId;
  const runAttempt = options.runAttempt;
  const token = options.token || "";
  const pathname = executionBlobPath(repository, runId, runAttempt);
  const githubRunUrl = `https://github.com/${FIXED_REPOSITORY}/actions/runs/${runId}`;
  const expectedStore = options.expectedStore ?? null;
  const base = {
    schema_version: 1,
    record_type: "execution_receipt",
    request_id: null,
    execution_id: pathname ? `${runId}-${runAttempt}` : null,
    computation: {
      status: "failed",
      exit_code: null,
      result: null,
      error: null,
    },
    storage: {
      status: "storage_failed",
      provider: "vercel_blob",
      access: "private",
      expected_store: expectedStore,
      pathname,
      url: null,
      download_url: null,
      sha256: null,
      etag: null,
      read_back: "not_performed",
      error: null,
    },
    github_run_url: RUN_ID.test(String(runId)) ? githubRunUrl : null,
    recovery: {
      actions_artifact: "execution-record",
      guaranteed: false,
      note: "The Actions artifact is a recovery copy when the job uploaded it. Cancellation or loss of the runner VM can leave no artifact and no blob.",
    },
  };

  if (!options.recordReady || !options.recordBytes) {
    base.computation.error = errorBody(
      "record_missing",
      "No execution record was produced to upload.",
    );
    base.storage.error = errorBody(
      "record_missing",
      "No execution record was produced to upload.",
    );
    return base;
  }

  const bytes = Buffer.from(options.recordBytes);
  const actualSha = sha256(bytes);
  base.storage.sha256 = actualSha;
  if (!/^[0-9a-f]{64}$/.test(options.expectedSha256 || "") || options.expectedSha256 !== actualSha) {
    base.computation.error = errorBody(
      "record_unreadable",
      "The execution record failed the integrity check before upload.",
    );
    base.storage.error = errorBody(
      "integrity_mismatch",
      "Record bytes do not match the execute job SHA-256.",
    );
    return base;
  }
  if (!pathname) {
    base.storage.error = errorBody(
      "invalid_request",
      "Blob pathname could not be built from the repository, run id, and attempt.",
    );
    return base;
  }

  let record;
  try {
    record = JSON.parse(bytes.toString("utf8"));
  } catch {
    record = null;
  }
  const executionId = `${runId}-${runAttempt}`;
  if (
    !record ||
    record.schema_version !== 1 ||
    record.record_type !== "execution_record" ||
    record.repository !== FIXED_REPOSITORY ||
    record.execution_id !== executionId
  ) {
    base.computation.error = errorBody(
      "record_unreadable",
      "Execution record did not match the trusted run identity.",
    );
    base.storage.error = errorBody(
      "record_unreadable",
      "Execution record did not match the trusted run identity.",
    );
    return base;
  }

  base.request_id = typeof record.request_id === "string" ? record.request_id : null;
  base.execution_id = executionId;
  base.computation = computationFromRecord(record);

  if (!token) {
    base.storage.error = errorBody(
      "missing_credentials",
      "BLOB_READ_WRITE_TOKEN is not set. The execution record was not uploaded.",
    );
    return base;
  }
  if (typeof options.put !== "function" || typeof options.get !== "function") {
    base.storage.error = errorBody(
      "uploader_misconfigured",
      "The trusted uploader has no Blob client.",
    );
    return base;
  }

  let blob;
  try {
    blob = await options.put(pathname, new Uint8Array(bytes), {
      access: "private",
      token,
      contentType: "application/json",
      addRandomSuffix: false,
      allowOverwrite: false,
      cacheControlMaxAge: 60,
    });
  } catch (err) {
    base.storage.error = errorBody(
      "blob_rejected",
      redact(err instanceof Error ? err.message : err, token),
    );
    return base;
  }

  const url = blob?.url ?? null;
  const returnedPath = blob?.pathname ?? null;
  base.storage.url = url;
  base.storage.download_url = blob?.downloadUrl ?? null;
  base.storage.etag = blob?.etag ?? null;
  if (!isPrivateBlobUrl(url)) {
    let deleted = false;
    if (typeof options.del === "function" && url) {
      try {
        await options.del(url, { token });
        deleted = true;
      } catch {
        deleted = false;
      }
    }
    base.storage.error = errorBody(
      "unexpected_public_url",
      "Blob URL is not on the private blob host.",
      { deleted },
    );
    return base;
  }
  if (returnedPath !== pathname) {
    base.storage.pathname = returnedPath;
    base.storage.error = errorBody(
      "unexpected_pathname",
      "Blob pathname did not match the no-overwrite contract path.",
      { expected_pathname: pathname, actual_pathname: returnedPath },
    );
    return base;
  }

  try {
    const loaded = await options.get(pathname, {
      access: "private",
      token,
      useCache: false,
    });
    if (!loaded || loaded.statusCode !== 200 || !loaded.stream) {
      base.storage.read_back = "failed";
      base.storage.error = errorBody(
        "read_back_failed",
        "Private read-back did not return the uploaded record.",
      );
      return base;
    }
    const roundTrip = await readAll(loaded.stream);
    if (!roundTrip.equals(bytes) || sha256(roundTrip) !== actualSha) {
      base.storage.read_back = "mismatch";
      base.storage.error = errorBody(
        "integrity_mismatch",
        "Private read-back bytes did not match the uploaded record.",
      );
      return base;
    }
  } catch (err) {
    base.storage.read_back = "failed";
    base.storage.error = errorBody(
      "read_back_failed",
      redact(err instanceof Error ? err.message : err, token),
    );
    return base;
  }

  base.storage.status = "stored";
  base.storage.read_back = "confirmed";
  base.storage.error = null;
  return base;
}

function canonical(value) {
  return `${JSON.stringify(sortKeys(value))}\n`;
}

function sortKeys(value) {
  if (Array.isArray(value)) {
    return value.map(sortKeys);
  }
  if (value && typeof value === "object") {
    return Object.fromEntries(
      Object.keys(value)
        .sort()
        .map((key) => [key, sortKeys(value[key])]),
    );
  }
  return value;
}

function summary(receipt) {
  const result = JSON.stringify(receipt.computation.result ?? null);
  const shown = result.length > 2000 ? `${result.slice(0, 2000)}…` : result;
  return [
    "## Remote script execution receipt",
    "",
    `- Request ID: ${receipt.request_id ?? ""}`,
    `- Execution ID: ${receipt.execution_id ?? ""}`,
    `- Computation: ${receipt.computation.status}`,
    `- Storage: ${receipt.storage.status}`,
    `- Read-back: ${receipt.storage.read_back}`,
    `- Result: \`${shown.replaceAll("`", "'")}\``,
    `- Blob pathname: ${receipt.storage.pathname ?? ""}`,
    `- Blob URL (private; not anonymously readable): ${receipt.storage.url ?? ""}`,
    `- SHA-256: ${receipt.storage.sha256 ?? ""}`,
    `- GitHub run: ${receipt.github_run_url ?? ""}`,
    "",
    "The private URL requires an authenticated Blob read. It is not publicly accessible.",
    receipt.storage.error
      ? `- Storage error: ${receipt.storage.error.category}: ${receipt.storage.error.message}`
      : "",
  ]
    .filter((line) => line !== "")
    .join("\n");
}

async function loadTrust(trustedRoot) {
  const file = path.join(trustedRoot, "execution", "trust_config.json");
  const parsed = JSON.parse(await readFile(file, "utf8"));
  return parsed.blob ?? null;
}

export async function main() {
  const runId = process.env.GITHUB_RUN_ID || "";
  const runAttempt = process.env.GITHUB_RUN_ATTEMPT || "";
  const token = process.env.BLOB_READ_WRITE_TOKEN || "";
  delete process.env.BLOB_READ_WRITE_TOKEN;
  delete process.env.VERCEL_OIDC_TOKEN;
  delete process.env.BLOB_STORE_ID;
  const recordReady = process.env.EXECUTION_RECORD_READY === "true";
  const recordPath = process.env.EXECUTION_RECORD_PATH || "";
  const receiptPath = process.env.EXECUTION_RECEIPT_PATH || "";
  const trustedRoot = process.env.EXECUTION_TRUSTED_ROOT || path.join(here, "..", "..");
  let recordBytes = null;
  if (recordReady && recordPath) {
    try {
      recordBytes = await readFile(recordPath);
    } catch {
      recordBytes = null;
    }
  }
  let expectedStore = null;
  try {
    expectedStore = await loadTrust(trustedRoot);
  } catch {
    expectedStore = null;
  }
  let put;
  let get;
  let del;
  if (token) {
    const sdk = await import("@vercel/blob");
    put = sdk.put;
    get = sdk.get;
    del = sdk.del;
  }
  const receipt = await uploadRecord({
    recordBytes,
    recordReady: recordReady && recordBytes !== null,
    expectedSha256: process.env.EXPECTED_RECORD_SHA256 || "",
    repository: FIXED_REPOSITORY,
    runId,
    runAttempt,
    token,
    expectedStore,
    put,
    get,
    del,
  });
  if (receiptPath) {
    await writeFile(receiptPath, canonical(receipt));
  }
  if (process.env.GITHUB_STEP_SUMMARY) {
    await appendFile(process.env.GITHUB_STEP_SUMMARY, `${summary(receipt)}\n`);
  }
  return receipt.storage.status === "stored" ? 0 : 1;
}

const invokedDirectly =
  Boolean(process.argv[1]) && import.meta.url === pathToFileURL(process.argv[1]).href;

if (invokedDirectly) {
  main()
    .then((code) => {
      process.exitCode = code;
    })
    .catch((err) => {
      console.error(err instanceof Error ? err.message : String(err));
      process.exitCode = 1;
    });
}
