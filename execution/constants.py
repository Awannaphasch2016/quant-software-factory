"""Fixed limits and identifiers for schema version 1."""

from __future__ import annotations

SCHEMA_VERSION = 1
REPOSITORY = "Awannaphasch2016/quant-software-factory"
DEFAULT_BRANCH = "main"
GITHUB_RUN_URL = (
    "https://github.com/Awannaphasch2016/quant-software-factory/actions/runs/{run_id}"
)
TIMEOUT_SECONDS = 30
MAX_INPUT_BYTES = 256 * 1024
MAX_STDOUT_BYTES = 256 * 1024
MAX_STDERR_BYTES = 256 * 1024
MAX_JSON_DEPTH = 64
MAX_STORED_PATH_CHARS = 256
WORKFLOW_PATH = ".github/workflows/execute-script.yml"
BLOB_SECRET_NAME = "BLOB_READ_WRITE_TOKEN"
GITHUB_ENVIRONMENT = "execution-upload"
RUN_NUMBER_PATTERN = r"^[1-9][0-9]{0,19}$"
SHA_PATTERN = r"^[0-9a-f]{40}$"
REQUEST_ID_PATTERN = r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,127}$"

RUNTIME_FILES: tuple[str, ...] = (
    "execution/__init__.py",
    "execution/allowlist.json",
    "execution/bootstrap.py",
    "execution/constants.py",
    "execution/errors.py",
    "execution/execute.py",
    "execution/gitutil.py",
    "execution/jsonutil.py",
    "execution/paths.py",
    "execution/prepare.py",
    "execution/provenance.py",
    "execution/runner.py",
    "execution/scrub.py",
    "execution/service.py",
    "execution/trust_config.json",
    "execution/uploader/package-lock.json",
    "execution/uploader/package.json",
    "execution/uploader/upload_record.mjs",
    WORKFLOW_PATH,
)

LOCKFILES: tuple[str, ...] = (
    "uv.lock",
    "poetry.lock",
    "Pipfile.lock",
    "pdm.lock",
    "requirements.lock",
)
