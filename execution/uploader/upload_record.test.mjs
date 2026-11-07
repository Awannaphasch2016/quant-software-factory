import assert from "node:assert/strict";
import test from "node:test";

import {
  computationFromRecord,
  executionBlobPath,
  isPrivateBlobUrl,
  sha256,
  uploadRecord,
} from "./upload_record.mjs";

const repository = "Awannaphasch2016/quant-software-factory";

function recordBytes(overrides = {}) {
  const record = {
    schema_version: 1,
    record_type: "execution_record",
    request_id: "req-1",
    execution_id: "42-1",
    repository,
    status: "succeeded",
    prepare: { status: "prepared", error: null },
    execution: {
      status: "succeeded",
      exit_code: 0,
      result: { max_drawdown: 0.25 },
      error: null,
    },
    ...overrides,
  };
  return Buffer.from(`${JSON.stringify(record)}\n`);
}

function privateUrl(pathname) {
  return `https://example.private.blob.vercel-storage.com/${pathname}`;
}

test("pathname is the no-overwrite contract path", () => {
  assert.equal(
    executionBlobPath(repository, "42", "1"),
    "executions/v1/Awannaphasch2016/quant-software-factory/42/1/execution.json",
  );
  assert.equal(executionBlobPath("other/repo", "42", "1"), null);
  assert.equal(executionBlobPath(repository, "01", "1"), null);
  assert.equal(isPrivateBlobUrl(privateUrl("executions/v1/record.json")), true);
  assert.equal(
    isPrivateBlobUrl("https://example.public.blob.vercel-storage.com/executions/v1/record.json"),
    false,
  );
});

test("missing token is a storage failure and does not upload", async () => {
  let called = false;
  const bytes = recordBytes();
  const receipt = await uploadRecord({
    recordReady: true,
    recordBytes: bytes,
    expectedSha256: sha256(bytes),
    repository,
    runId: "42",
    runAttempt: "1",
    token: "",
    put: async () => {
      called = true;
    },
  });
  assert.equal(called, false);
  assert.equal(receipt.computation.status, "succeeded");
  assert.deepEqual(receipt.computation.result, { max_drawdown: 0.25 });
  assert.equal(receipt.storage.status, "storage_failed");
  assert.equal(receipt.storage.error.category, "missing_credentials");
  assert.equal(receipt.storage.read_back, "not_performed");
  assert.equal(receipt.recovery.guaranteed, false);
});

test("put uses private no-overwrite options and read-back confirms bytes", async () => {
  const bytes = recordBytes();
  const calls = [];
  const receipt = await uploadRecord({
    recordReady: true,
    recordBytes: bytes,
    expectedSha256: sha256(bytes),
    repository,
    runId: "42",
    runAttempt: "1",
    token: "test-token-value",
    expectedStore: { store_id: "store_CEauyrab8003cHZO", access: "private" },
    put: async (pathname, body, opts) => {
      calls.push({ pathname, body, opts });
      return {
        pathname,
        url: privateUrl(pathname),
        downloadUrl: `${privateUrl(pathname)}?download=1`,
        contentType: "application/json",
        etag: '"abc"',
      };
    },
    get: async () => ({
      statusCode: 200,
      stream: new Blob([bytes]).stream(),
    }),
  });
  assert.equal(calls.length, 1);
  assert.equal(calls[0].opts.access, "private");
  assert.equal(calls[0].opts.allowOverwrite, false);
  assert.equal(calls[0].opts.addRandomSuffix, false);
  assert.equal(calls[0].opts.token, "test-token-value");
  assert.equal(calls[0].opts.oidcToken, undefined);
  assert.equal(calls[0].opts.storeId, undefined);
  assert.equal(Buffer.compare(Buffer.from(calls[0].body), bytes), 0);
  assert.equal(receipt.storage.status, "stored");
  assert.equal(receipt.storage.read_back, "confirmed");
  assert.equal(receipt.storage.sha256, sha256(bytes));
  assert.equal(receipt.storage.url, privateUrl(calls[0].pathname));
  assert.equal(receipt.computation.status, "succeeded");
  assert.equal(receipt.storage.expected_store.store_id, "store_CEauyrab8003cHZO");
});

test("public url is not reported as stored", async () => {
  const bytes = recordBytes();
  const deleted = [];
  const receipt = await uploadRecord({
    recordReady: true,
    recordBytes: bytes,
    expectedSha256: sha256(bytes),
    repository,
    runId: "42",
    runAttempt: "1",
    token: "test-token-value",
    put: async (pathname) => ({
      pathname,
      url: `https://example.public.blob.vercel-storage.com/${pathname}`,
    }),
    get: async () => {
      throw new Error("read should not run");
    },
    del: async (url) => {
      deleted.push(url);
    },
  });
  assert.equal(deleted.length, 1);
  assert.equal(receipt.storage.status, "storage_failed");
  assert.equal(receipt.storage.error.category, "unexpected_public_url");
  assert.equal(receipt.storage.read_back, "not_performed");
});

test("blob errors redact the token", async () => {
  const bytes = recordBytes();
  const receipt = await uploadRecord({
    recordReady: true,
    recordBytes: bytes,
    expectedSha256: sha256(bytes),
    repository,
    runId: "42",
    runAttempt: "1",
    token: "test-token-value",
    put: async () => {
      throw new Error("upload failed for test-token-value");
    },
    get: async () => {
      throw new Error("unused");
    },
  });
  assert.equal(receipt.storage.status, "storage_failed");
  assert.equal(receipt.storage.error.message.includes("test-token-value"), false);
  assert.match(receipt.storage.error.message, /\[redacted\]/);
});

test("failed computation can still be stored", async () => {
  const bytes = recordBytes({
    status: "failed",
    prepare: {
      status: "prepared",
      error: null,
    },
    execution: {
      status: "failed",
      exit_code: 1,
      result: null,
      error: { category: "script_failed", message: "Approved script exited with a nonzero status." },
    },
  });
  const receipt = await uploadRecord({
    recordReady: true,
    recordBytes: bytes,
    expectedSha256: sha256(bytes),
    repository,
    runId: "42",
    runAttempt: "1",
    token: "test-token-value",
    put: async (pathname) => ({ pathname, url: privateUrl(pathname) }),
    get: async () => ({ statusCode: 200, stream: new Blob([bytes]).stream() }),
  });
  assert.equal(receipt.computation.status, "failed");
  assert.equal(receipt.computation.result, null);
  assert.equal(receipt.computation.error.category, "script_failed");
  assert.equal(receipt.storage.status, "stored");
  assert.equal(computationFromRecord(JSON.parse(bytes.toString())).status, "failed");
});

test("hash mismatch does not upload", async () => {
  const bytes = recordBytes();
  let called = false;
  const receipt = await uploadRecord({
    recordReady: true,
    recordBytes: bytes,
    expectedSha256: "a".repeat(64),
    repository,
    runId: "42",
    runAttempt: "1",
    token: "test-token-value",
    put: async () => {
      called = true;
    },
  });
  assert.equal(called, false);
  assert.equal(receipt.storage.error.category, "integrity_mismatch");
});
