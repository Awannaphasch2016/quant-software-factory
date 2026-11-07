"""Command line entry for the trusted runner.

The workflow invokes fixed subcommands. Request fields arrive in the
environment so the shell does not interpolate them.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Any

from execution.constants import SCHEMA_VERSION
from execution.errors import Failure
from execution.prepare import Request, parse_schema_version
from execution.service import (
    Outcome,
    preflight_request,
    run_request,
    write_github_output,
)


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    if args == ["preflight"]:
        return _preflight()
    if args == ["run"]:
        return _run()
    print("usage: python -B -m execution.runner preflight|run", file=sys.stderr)
    return 2


def _preflight() -> int:
    request, common = _from_env(require_candidate=False)
    if request is None or common is None:
        return 2
    ok, outcome = preflight_request(
        request,
        trusted_root=common["trusted_root"],
        output_dir=common["output_dir"],
        run_id=common["run_id"],
        run_attempt=common["run_attempt"],
        workflow_sha=common["workflow_sha"],
        github_ref=common["github_ref"],
        in_github_actions=common["in_github_actions"],
    )
    if ok:
        write_github_output(
            {
                "sha_ok": "true",
                "record_ready": "false",
                "record_sha256": "",
                "execution_id": f"{common['run_id']}-{common['run_attempt']}",
                "computation_status": "",
            }
        )
        return 0
    if outcome is None:
        write_github_output({"sha_ok": "false", "record_ready": "false"})
        return 2
    _emit(outcome, sha_ok=False)
    return 1


def _run() -> int:
    request, common = _from_env(require_candidate=True)
    if request is None or common is None:
        return 2
    outcome = run_request(
        request,
        candidate_root=common["candidate_root"],
        trusted_root=common["trusted_root"],
        output_dir=common["output_dir"],
        run_id=common["run_id"],
        run_attempt=common["run_attempt"],
        workflow_sha=common["workflow_sha"],
        github_ref=common["github_ref"],
        in_github_actions=common["in_github_actions"],
        scrub_credentials=True,
        require_clean=True,
    )
    _emit(
        outcome,
        sha_ok=outcome.record.get("status") == "succeeded"
        or outcome.record["prepare"]["status"] == "prepared",
    )
    return outcome.exit_code


def _emit(outcome: Outcome, *, sha_ok: bool) -> None:
    write_github_output(
        {
            "sha_ok": "true" if sha_ok else "false",
            "record_ready": "true",
            "record_sha256": outcome.record_sha256,
            "execution_id": outcome.execution_id or "",
            "computation_status": outcome.computation_status,
        }
    )


def _from_env(
    *,
    require_candidate: bool,
) -> tuple[Request | None, dict[str, Any] | None]:
    required = [
        "EXECUTION_SCHEMA_VERSION",
        "EXECUTION_REQUEST_ID",
        "EXECUTION_REPOSITORY",
        "EXECUTION_CODE_SHA",
        "EXECUTION_SCRIPT_PATH",
        "EXECUTION_INPUT_JSON",
        "EXECUTION_TRUSTED_ROOT",
        "EXECUTION_OUTPUT_DIR",
        "GITHUB_RUN_ID",
        "GITHUB_RUN_ATTEMPT",
        "GITHUB_SHA",
    ]
    if require_candidate:
        required.append("EXECUTION_CANDIDATE_ROOT")
    missing = [name for name in required if os.environ.get(name, "") == ""]
    if missing:
        print("missing environment: " + ", ".join(missing), file=sys.stderr)
        return None, None
    try:
        schema_version = parse_schema_version(os.environ["EXECUTION_SCHEMA_VERSION"])
    except Failure as exc:
        print(exc.message, file=sys.stderr)
        return None, None
    if schema_version != SCHEMA_VERSION:
        return None, None
    trusted = Path(os.environ["EXECUTION_TRUSTED_ROOT"])
    candidate = (
        Path(os.environ["EXECUTION_CANDIDATE_ROOT"]) if require_candidate else trusted
    )
    common: dict[str, Any] = {
        "trusted_root": trusted,
        "candidate_root": candidate,
        "output_dir": Path(os.environ["EXECUTION_OUTPUT_DIR"]),
        "run_id": os.environ["GITHUB_RUN_ID"],
        "run_attempt": os.environ["GITHUB_RUN_ATTEMPT"],
        "workflow_sha": os.environ["GITHUB_SHA"],
        "github_ref": os.environ.get("GITHUB_REF"),
        "in_github_actions": os.environ.get("GITHUB_ACTIONS") == "true",
    }
    request = Request(
        schema_version=schema_version,
        request_id=os.environ["EXECUTION_REQUEST_ID"],
        repository=os.environ["EXECUTION_REPOSITORY"],
        code_sha=os.environ["EXECUTION_CODE_SHA"],
        script_path=os.environ["EXECUTION_SCRIPT_PATH"],
        input_raw=os.environ["EXECUTION_INPUT_JSON"],
    )
    return request, common


if __name__ == "__main__":
    sys.exit(main())
