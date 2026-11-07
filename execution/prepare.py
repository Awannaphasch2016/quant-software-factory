"""Stage 1: validate the request and build the prepare manifest."""

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from execution.constants import (
    DEFAULT_BRANCH,
    GITHUB_RUN_URL,
    REPOSITORY,
    REQUEST_ID_PATTERN,
    RUN_NUMBER_PATTERN,
    SCHEMA_VERSION,
    SHA_PATTERN,
)
from execution.errors import Failure
from execution.gitutil import resolve_commit, worktree_dirty
from execution.jsonutil import parse_single_json, sha256_bytes
from execution.paths import (
    load_allowlist,
    normalize_script_path,
    resolve_script,
    resolve_src,
)
from execution.provenance import (
    dependency_provenance,
    file_set_sha256,
    interpreter_provenance,
    load_trust_config,
    workflow_file_sha256,
)
from execution.scrub import scrub_repository

_REQUEST_ID = re.compile(REQUEST_ID_PATTERN)
_SHA = re.compile(SHA_PATTERN)
_RUN = re.compile(RUN_NUMBER_PATTERN)


@dataclass(frozen=True)
class Request:
    schema_version: int
    request_id: str
    repository: str
    code_sha: str
    script_path: str
    input_raw: str


@dataclass
class PrepareResult:
    manifest: dict[str, Any]
    ok: bool
    script: Path | None = None
    src: Path | None = None


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ")


def execution_id(run_id: str, run_attempt: str) -> str:
    if _RUN.fullmatch(run_id) is None or _RUN.fullmatch(run_attempt) is None:
        raise Failure(
            "invalid_request",
            "GitHub run id and attempt must be positive decimal integers.",
        )
    return f"{run_id}-{run_attempt}"


def github_run_url(run_id: str) -> str:
    if _RUN.fullmatch(run_id) is None:
        raise Failure("invalid_request", "GitHub run id is not a positive integer.")
    return GITHUB_RUN_URL.format(run_id=run_id)


def parse_schema_version(value: object) -> int:
    if type(value) is int and value == SCHEMA_VERSION or value == "1":
        return SCHEMA_VERSION
    raise Failure(
        "invalid_request",
        "schema_version must be the integer 1.",
    )


def validate_request_fields(request: Request) -> None:
    parse_schema_version(request.schema_version)
    if _REQUEST_ID.fullmatch(request.request_id) is None:
        raise Failure(
            "invalid_request",
            "request_id must be 1-128 characters of letters, digits, or . _ : -.",
        )
    if request.repository != REPOSITORY:
        raise Failure(
            "repository_mismatch",
            "repository is fixed for this runner.",
            {"repository": REPOSITORY},
        )
    if _SHA.fullmatch(request.code_sha) is None:
        raise Failure(
            "invalid_sha",
            "code_sha must be the full 40-character lowercase commit SHA.",
        )


def check_dispatch_ref(*, in_github_actions: bool, github_ref: str | None) -> None:
    if not in_github_actions:
        return
    expected = f"refs/heads/{DEFAULT_BRANCH}"
    if github_ref != expected:
        raise Failure(
            "dispatch_ref_rejected",
            "workflow_dispatch must run from the default branch workflow.",
            {"expected_ref": expected},
        )


def prepare(
    request: Request,
    *,
    candidate_root: Path,
    trusted_root: Path,
    run_id: str,
    run_attempt: str,
    workflow_sha: str,
    github_ref: str | None,
    in_github_actions: bool,
    require_clean: bool,
    scrub_credentials: bool,
    allowlist: tuple[str, ...] | None,
    max_input_bytes: int,
) -> PrepareResult:
    """Build a prepare manifest. Expected failures are recorded, not raised."""
    exec_id = _optional_execution_id(run_id, run_attempt)
    try:
        if _SHA.fullmatch(workflow_sha) is None:
            raise Failure(
                "invalid_request",
                "workflow SHA must be a full 40-character lowercase SHA.",
            )
        check_dispatch_ref(in_github_actions=in_github_actions, github_ref=github_ref)
        validate_request_fields(request)
        parsed_input, input_raw, input_sha = _parse_input(
            request.input_raw,
            max_input_bytes=max_input_bytes,
        )
        chosen_allowlist = (
            allowlist if allowlist is not None else load_allowlist(trusted_root)
        )
        for entry in chosen_allowlist:
            normalize_script_path(entry)
        trust = load_trust_config(trusted_root)
        resolved = resolve_commit(candidate_root, request.code_sha)
        script = resolve_script(candidate_root, request.script_path, chosen_allowlist)
        src = resolve_src(candidate_root)
        candidate_dirty = worktree_dirty(candidate_root)
        trusted_dirty = worktree_dirty(trusted_root)
        if require_clean and candidate_dirty:
            raise Failure(
                "dirty_worktree",
                "Candidate checkout is dirty, so the SHA does not identify the files.",
            )
        if in_github_actions and trusted_dirty:
            raise Failure(
                "dirty_worktree",
                "Trusted runner checkout is dirty.",
            )
        scrub = None
        if scrub_credentials:
            scrub = {
                "candidate": scrub_repository(candidate_root),
                "trusted": scrub_repository(trusted_root),
            }
        dependencies = dependency_provenance(candidate_root)
        runtime = {
            **interpreter_provenance(),
            **dependencies,
            "runner": {
                "workflow_sha": workflow_sha,
                "workflow_ref": github_ref,
                "workflow_path": ".github/workflows/execute-script.yml",
                "workflow_file_sha256": workflow_file_sha256(trusted_root),
                "runner_files_sha256": file_set_sha256(trusted_root),
                "trusted_worktree_dirty": trusted_dirty,
            },
        }
        manifest = _manifest(
            request=request,
            execution_id_value=exec_id,
            resolved_sha=resolved,
            script_path=request.script_path,
            input_raw=input_raw,
            input_value=parsed_input,
            input_sha=input_sha,
            runtime=runtime,
            status="prepared",
            error=None,
            scrub=scrub,
            candidate_dirty=candidate_dirty,
            expected_store=trust.get("blob"),
        )
        return PrepareResult(manifest=manifest, ok=True, script=script, src=src)
    except Failure as exc:
        manifest = _failure_manifest(
            request=request,
            execution_id_value=exec_id,
            error=exc,
            max_input_bytes=max_input_bytes,
        )
        return PrepareResult(manifest=manifest, ok=False)


def _optional_execution_id(run_id: str, run_attempt: str) -> str:
    try:
        return execution_id(run_id, run_attempt)
    except Failure as exc:
        raise Failure(exc.category, exc.message, exc.details) from None


def _parse_input(raw: str, *, max_input_bytes: int) -> tuple[object, str, str]:
    encoded = raw.encode("utf-8")
    digest = sha256_bytes(encoded)
    if len(encoded) > max_input_bytes:
        raise Failure(
            "input_too_large",
            "Input JSON exceeds the byte cap.",
            {
                "input_bytes": len(encoded),
                "max_input_bytes": max_input_bytes,
                "input_sha256": digest,
            },
        )
    value = parse_single_json(raw, depth_category="input_rejected")
    return value, raw, digest


def _failure_manifest(
    *,
    request: Request,
    execution_id_value: str | None,
    error: Failure,
    max_input_bytes: int,
) -> dict[str, Any]:
    input_sha = sha256_bytes(request.input_raw.encode("utf-8"))
    input_bytes = len(request.input_raw.encode("utf-8"))
    store_raw = input_bytes <= max_input_bytes
    request_id: str | None = (
        request.request_id if _REQUEST_ID.fullmatch(request.request_id or "") else None
    )
    requested = (
        request.code_sha
        if isinstance(request.code_sha, str) and len(request.code_sha) <= 64
        else None
    )
    script_path = (
        request.script_path
        if isinstance(request.script_path, str) and len(request.script_path) <= 256
        else None
    )
    return _manifest(
        request=request,
        execution_id_value=execution_id_value,
        resolved_sha=None,
        script_path=script_path,
        input_raw=request.input_raw if store_raw else None,
        input_value=None,
        input_sha=input_sha,
        runtime=None,
        status="preparation_failed",
        error=error.as_dict(),
        scrub=None,
        candidate_dirty=None,
        expected_store=None,
        request_id=request_id,
        requested_sha=requested,
        input_bytes=input_bytes,
        input_omitted=not store_raw,
    )


def _manifest(
    *,
    request: Request,
    execution_id_value: str | None,
    resolved_sha: str | None,
    script_path: str | None,
    input_raw: str | None,
    input_value: object,
    input_sha: str,
    runtime: dict[str, Any] | None,
    status: str,
    error: dict[str, Any] | None,
    scrub: dict[str, Any] | None,
    candidate_dirty: bool | None,
    expected_store: object,
    request_id: str | None | object = ...,
    requested_sha: str | None | object = ...,
    input_bytes: int | None = None,
    input_omitted: bool = False,
) -> dict[str, Any]:
    stored_request_id = request.request_id if request_id is ... else request_id
    stored_sha = request.code_sha if requested_sha is ... else requested_sha
    body: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "record_type": "prepare_manifest",
        "status": status,
        "request_id": stored_request_id,
        "execution_id": execution_id_value,
        "repository": REPOSITORY,
        "requested_code_sha": stored_sha,
        "resolved_code_sha": resolved_sha,
        "script_path": script_path,
        "input_raw": input_raw,
        "input_sha256": input_sha,
        "input": input_value,
        "input_omitted": input_omitted,
        "runtime": runtime,
        "candidate_worktree_dirty": candidate_dirty,
        "credential_scrub": scrub,
        "expected_store": expected_store,
        "error": error,
        "prepared_at": utc_now(),
    }
    if input_bytes is not None:
        body["input_bytes"] = input_bytes
    return body
