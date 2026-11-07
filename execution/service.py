"""Orchestrate prepare and execute, then write the execution record."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from execution.constants import (
    MAX_INPUT_BYTES,
    MAX_STDERR_BYTES,
    MAX_STDOUT_BYTES,
    REPOSITORY,
    SCHEMA_VERSION,
    TIMEOUT_SECONDS,
)
from execution.errors import Failure
from execution.execute import execute_script, not_started_execution
from execution.jsonutil import canonical_bytes, sha256_bytes
from execution.prepare import PrepareResult, Request, github_run_url, prepare


@dataclass
class Outcome:
    record: dict[str, Any]
    record_bytes: bytes
    record_sha256: str
    computation_status: str
    exit_code: int
    execution_id: str | None


def run_request(
    request: Request,
    *,
    candidate_root: Path,
    trusted_root: Path,
    output_dir: Path,
    run_id: str,
    run_attempt: str,
    workflow_sha: str,
    github_ref: str | None = None,
    in_github_actions: bool = False,
    timeout_seconds: int = TIMEOUT_SECONDS,
    max_input_bytes: int = MAX_INPUT_BYTES,
    max_stdout_bytes: int = MAX_STDOUT_BYTES,
    max_stderr_bytes: int = MAX_STDERR_BYTES,
    allowlist: tuple[str, ...] | None = None,
    scrub_credentials: bool = False,
    require_clean: bool | None = None,
) -> Outcome:
    output_dir.mkdir(parents=True, exist_ok=True)
    clean = in_github_actions if require_clean is None else require_clean
    try:
        prepared = prepare(
            request,
            candidate_root=candidate_root,
            trusted_root=trusted_root,
            run_id=run_id,
            run_attempt=run_attempt,
            workflow_sha=workflow_sha,
            github_ref=github_ref,
            in_github_actions=in_github_actions,
            require_clean=clean,
            scrub_credentials=scrub_credentials,
            allowlist=allowlist,
            max_input_bytes=max_input_bytes,
        )
    except Failure as exc:
        prepared = PrepareResult(
            manifest={
                "schema_version": SCHEMA_VERSION,
                "record_type": "prepare_manifest",
                "status": "preparation_failed",
                "request_id": None,
                "execution_id": None,
                "repository": REPOSITORY,
                "requested_code_sha": None,
                "resolved_code_sha": None,
                "script_path": None,
                "input_raw": None,
                "input_sha256": None,
                "input": None,
                "runtime": None,
                "candidate_worktree_dirty": None,
                "credential_scrub": None,
                "expected_store": None,
                "error": exc.as_dict(),
                "prepared_at": None,
            },
            ok=False,
        )
    if prepared.ok and prepared.script is not None and prepared.src is not None:
        try:
            execution = execute_script(
                trusted_root=trusted_root,
                candidate_root=candidate_root,
                script=prepared.script,
                src=prepared.src,
                input_raw=request.input_raw,
                timeout_seconds=timeout_seconds,
                max_stdout_bytes=max_stdout_bytes,
                max_stderr_bytes=max_stderr_bytes,
            )
        except Failure as exc:
            execution = not_started_execution(timeout_seconds=timeout_seconds)
            execution["status"] = "failed"
            execution["error"] = exc.as_dict()
    else:
        execution = not_started_execution(timeout_seconds=timeout_seconds)
    record = _record(
        prepared,
        execution,
        run_id=run_id,
        limits=_limits(
            timeout_seconds, max_input_bytes, max_stdout_bytes, max_stderr_bytes
        ),
    )
    return _write(output_dir, prepared.manifest, record)


def preflight_request(
    request: Request,
    *,
    trusted_root: Path,
    output_dir: Path,
    run_id: str,
    run_attempt: str,
    workflow_sha: str,
    github_ref: str | None,
    in_github_actions: bool,
    max_input_bytes: int = MAX_INPUT_BYTES,
) -> tuple[bool, Outcome | None]:
    """Reject a dispatch before checkout. Success writes no record."""
    from execution.jsonutil import parse_single_json
    from execution.prepare import (
        check_dispatch_ref,
        execution_id,
        validate_request_fields,
    )

    try:
        if len(workflow_sha) != 40:
            raise Failure(
                "invalid_request", "workflow SHA must be 40 lowercase hex characters."
            )
        check_dispatch_ref(in_github_actions=in_github_actions, github_ref=github_ref)
        validate_request_fields(request)
        execution_id(run_id, run_attempt)
        encoded = request.input_raw.encode("utf-8")
        if len(encoded) > max_input_bytes:
            raise Failure("input_too_large", "Input JSON exceeds the byte cap.")
        parse_single_json(request.input_raw, depth_category="input_rejected")
    except Failure:
        outcome = run_request(
            request,
            candidate_root=trusted_root,
            trusted_root=trusted_root,
            output_dir=output_dir,
            run_id=run_id,
            run_attempt=run_attempt,
            workflow_sha=workflow_sha,
            github_ref=github_ref,
            in_github_actions=in_github_actions,
            allowlist=(),
            scrub_credentials=False,
            require_clean=False,
            max_input_bytes=max_input_bytes,
        )
        return False, outcome
    return True, None


def _limits(
    timeout_seconds: int,
    max_input_bytes: int,
    max_stdout_bytes: int,
    max_stderr_bytes: int,
) -> dict[str, int]:
    return {
        "max_input_bytes": max_input_bytes,
        "max_output_bytes": max_stdout_bytes,
        "max_stderr_bytes": max_stderr_bytes,
        "timeout_seconds": timeout_seconds,
    }


def _record(
    prepared: PrepareResult,
    execution: dict[str, Any],
    *,
    run_id: str,
    limits: dict[str, int],
) -> dict[str, Any]:
    status = "succeeded" if execution.get("status") == "succeeded" else "failed"
    try:
        run_url = github_run_url(run_id)
    except Failure:
        run_url = None
    return {
        "schema_version": SCHEMA_VERSION,
        "record_type": "execution_record",
        "request_id": prepared.manifest.get("request_id"),
        "execution_id": prepared.manifest.get("execution_id"),
        "repository": REPOSITORY,
        "status": status,
        "prepare": prepared.manifest,
        "execution": execution,
        "limits": limits,
        "github_run_url": run_url,
    }


def _write(
    output_dir: Path, manifest: dict[str, Any], record: dict[str, Any]
) -> Outcome:
    record_bytes = canonical_bytes(record)
    manifest_bytes = canonical_bytes(manifest)
    _atomic(output_dir / "prepare_manifest.json", manifest_bytes)
    record_path = output_dir / "execution_record.json"
    _atomic(record_path, record_bytes)
    status = "succeeded" if record.get("status") == "succeeded" else "failed"
    exec_id = record.get("execution_id")
    return Outcome(
        record=record,
        record_bytes=record_bytes,
        record_sha256=sha256_bytes(record_bytes),
        computation_status=status,
        exit_code=0 if status == "succeeded" else 1,
        execution_id=exec_id if isinstance(exec_id, str) else None,
    )


def _atomic(path: Path, payload: bytes) -> None:
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_bytes(payload)
    os.replace(temporary, path)


def write_github_output(values: dict[str, str]) -> None:
    path = os.environ.get("GITHUB_OUTPUT")
    if not path:
        return
    with open(path, "a", encoding="utf-8") as handle:
        for key, value in values.items():
            if "\n" in key or "\n" in value or "=" not in f"{key}=":
                raise Failure(
                    "invalid_request", "GitHub output values must be single-line."
                )
            handle.write(f"{key}={value}\n")
