"""Contracts for the generic runner, records, and workflow file."""

from __future__ import annotations

import hashlib
import json
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

from execution.constants import REPOSITORY, RUNTIME_FILES, TIMEOUT_SECONDS
from execution.errors import Failure
from execution.jsonutil import canonical_bytes, parse_single_json
from execution.prepare import Request
from execution.scrub import scrub_repository
from execution.service import preflight_request, run_request
from tests.execution_support import (
    ROOT,
    commit_repo,
    copy_library,
    git,
    make_library_repo,
    write_files,
)

WORKFLOW = ROOT / ".github" / "workflows" / "execute-script.yml"
SHA = "a" * 40


def _request(
    code_sha: str, script_path: str, raw: str, request_id: str = "req-1"
) -> Request:
    return Request(
        schema_version=1,
        request_id=request_id,
        repository=REPOSITORY,
        code_sha=code_sha,
        script_path=script_path,
        input_raw=raw,
    )


def _run(
    tmp: Path,
    *,
    code_sha: str,
    raw: str,
    script_path: str = "scripts/calculate_max_drawdown.py",
    candidate: Path | None = None,
    allowlist: tuple[str, ...] | None = None,
    timeout_seconds: int = TIMEOUT_SECONDS,
    max_stdout_bytes: int = 256 * 1024,
    max_input_bytes: int = 256 * 1024,
    require_clean: bool = True,
    in_github_actions: bool = False,
    github_ref: str | None = "refs/heads/main",
    scrub_credentials: bool = False,
) -> Any:
    return run_request(
        _request(code_sha, script_path, raw),
        candidate_root=candidate or tmp,
        trusted_root=ROOT,
        output_dir=tmp / "out",
        run_id="42",
        run_attempt="1",
        workflow_sha=SHA,
        github_ref=github_ref,
        in_github_actions=in_github_actions,
        timeout_seconds=timeout_seconds,
        max_stdout_bytes=max_stdout_bytes,
        max_input_bytes=max_input_bytes,
        allowlist=allowlist,
        scrub_credentials=scrub_credentials,
        require_clean=require_clean,
    )


def _error_blob(record: dict[str, Any]) -> str:
    return json.dumps(
        {
            "prepare_error": record["prepare"]["error"],
            "execution_error": record["execution"]["error"],
        },
        sort_keys=True,
    )


def test_drawdown_run_records_the_script_result(tmp_path: Path) -> None:
    repo = tmp_path / "candidate"
    code_sha = make_library_repo(repo)
    evil = tmp_path / "evil"
    write_files(
        evil,
        {
            "quant_software_factory/__init__.py": (
                "def calculate_max_drawdown(equity_curve):\n    return 1.0\n"
            )
        },
    )
    os.environ["PYTHONPATH"] = str(evil)
    os.environ["BLOB_READ_WRITE_TOKEN"] = "supersecret"
    try:
        outcome = _run(
            tmp_path,
            candidate=repo,
            code_sha=code_sha,
            raw='{"equity_curve":[100,120,90,110]}',
        )
    finally:
        os.environ.pop("PYTHONPATH", None)
        os.environ.pop("BLOB_READ_WRITE_TOKEN", None)
    record = outcome.record
    assert outcome.computation_status == "succeeded"
    assert outcome.exit_code == 0
    assert record["status"] == "succeeded"
    assert record["execution_id"] == "42-1"
    assert record["prepare"]["status"] == "prepared"
    assert record["prepare"]["resolved_code_sha"] == code_sha
    assert record["prepare"]["input_raw"] == '{"equity_curve":[100,120,90,110]}'
    assert record["prepare"]["runtime"]["dependencies_lock_sha256"] is None
    assert record["prepare"]["runtime"]["declared_runtime_dependencies"] == []
    assert record["execution"]["exit_code"] == 0
    assert record["execution"]["result"] == {"max_drawdown": 0.25}
    assert record["github_run_url"].endswith("/actions/runs/42")
    text = outcome.record_bytes.decode()
    assert "supersecret" not in text
    assert "exception_type" not in text
    assert hashlib.sha256(outcome.record_bytes).hexdigest() == outcome.record_sha256


def test_nonzero_exit_does_not_invent_an_exception(tmp_path: Path) -> None:
    repo = tmp_path / "candidate"
    code_sha = make_library_repo(repo)
    outcome = _run(
        tmp_path, candidate=repo, code_sha=code_sha, raw='{"equity_curve":[]}'
    )
    error = outcome.record["execution"]["error"]
    assert outcome.record["execution"]["status"] == "failed"
    assert outcome.record["execution"]["result"] is None
    assert outcome.record["execution"]["exit_code"] == 1
    assert error["category"] == "script_failed"
    assert "ValueError" not in json.dumps(error)
    assert "exception_type" not in error
    assert "empty" in outcome.record["execution"]["stderr"]


def test_sha_mismatch_and_dirty_tree_stop_before_execution(tmp_path: Path) -> None:
    repo = tmp_path / "candidate"
    first = make_library_repo(repo)
    write_files(repo, {"README.md": "second\n"})
    git(repo, "add", "README.md")
    git(repo, "commit", "-m", "second")
    outcome = _run(tmp_path, candidate=repo, code_sha=first, raw="{}")
    assert outcome.record["prepare"]["status"] == "preparation_failed"
    assert outcome.record["prepare"]["error"]["category"] == "sha_mismatch"
    assert outcome.record["execution"]["status"] == "not_started"
    assert outcome.record["execution"]["exit_code"] is None
    assert "exception_type" not in _error_blob(outcome.record)

    head = git(repo, "rev-parse", "HEAD").stdout.strip()
    (repo / "extra.txt").write_text("dirty", encoding="utf-8")
    dirty = _run(tmp_path / "dirty-out", candidate=repo, code_sha=head, raw="{}")
    assert dirty.record["prepare"]["error"]["category"] == "dirty_worktree"
    assert dirty.record["execution"]["status"] == "not_started"


def test_rejects_bad_paths_symlinks_and_nonfinite_input(tmp_path: Path) -> None:
    repo = tmp_path / "candidate"
    copy_library(repo)
    outside = tmp_path / "outside.py"
    outside.write_text("print('{}')\n", encoding="utf-8")
    link = repo / "scripts" / "calculate_max_drawdown.py"
    link.unlink()
    link.symlink_to(outside)
    code_sha = commit_repo(repo)
    linked = _run(tmp_path, candidate=repo, code_sha=code_sha, raw="{}")
    assert linked.record["prepare"]["error"]["category"] == "symlink_rejected"

    traversal = _run(
        tmp_path / "traversal",
        candidate=repo,
        code_sha=code_sha,
        script_path="scripts/../scripts/calculate_max_drawdown.py",
        raw="{}",
        require_clean=False,
    )
    assert traversal.record["prepare"]["error"]["category"] == "path_rejected"

    marker = tmp_path / "marker-repo"
    write_files(
        marker,
        {
            "src/keep.txt": "src\n",
            "scripts/marker.py": (
                "from pathlib import Path\n"
                "Path(__file__).with_name('executed.txt').write_text('yes')\n"
                "print('{\"ok\": true}')\n"
            ),
        },
    )
    (marker / "src").mkdir(parents=True, exist_ok=True)
    (marker / "src" / "keep.txt").write_text("src\n", encoding="utf-8")
    marker_sha = commit_repo(marker)
    skipped = _run(
        tmp_path / "nan",
        candidate=marker,
        code_sha=marker_sha,
        script_path="scripts/marker.py",
        allowlist=("scripts/marker.py",),
        raw='{"value": NaN}',
    )
    assert skipped.record["prepare"]["error"]["category"] == "nonfinite_json"
    assert not (marker / "scripts" / "executed.txt").exists()


def test_malformed_output_timeout_and_caps(tmp_path: Path) -> None:
    repo = tmp_path / "scripts-repo"
    write_files(
        repo,
        {
            "src/keep.txt": "src\n",
            "scripts/bad.py": "print('not-json')\n",
            "scripts/two.py": "print('{}\\n{}')\n",
            "scripts/nan.py": "print('{\"value\": NaN}')\n",
            "scripts/boom.py": "raise RuntimeError('boom')\n",
            "scripts/sleep.py": "import time\ntime.sleep(30)\n",
            "scripts/big.py": "print('x' * 100000)\n",
        },
    )
    code_sha = commit_repo(repo)

    def once(name: str, **kwargs: Any) -> Any:
        return _run(
            tmp_path / name,
            candidate=repo,
            code_sha=code_sha,
            script_path=f"scripts/{name}.py",
            allowlist=(f"scripts/{name}.py",),
            raw="{}",
            **kwargs,
        )

    malformed = once("bad")
    assert malformed.record["execution"]["error"]["category"] == "malformed_output"
    assert malformed.record["execution"]["result"] is None
    two = once("two")
    assert two.record["execution"]["error"]["category"] == "malformed_output"
    nonfinite = once("nan")
    assert nonfinite.record["execution"]["error"]["category"] == "nonfinite_json"
    boom = once("boom")
    assert boom.record["execution"]["error"]["category"] == "script_failed"
    assert "RuntimeError" not in json.dumps(boom.record["execution"]["error"])
    assert "Traceback" in boom.record["execution"]["stderr"]
    timed = once("sleep", timeout_seconds=1)
    assert timed.record["execution"]["error"]["category"] == "timeout"
    assert "exception_type" not in json.dumps(timed.record["execution"]["error"])
    huge = once("big", max_stdout_bytes=64)
    assert huge.record["execution"]["error"]["category"] == "output_too_large"
    oversized = _run(
        tmp_path / "oversized",
        candidate=repo,
        code_sha=code_sha,
        script_path="scripts/bad.py",
        allowlist=("scripts/bad.py",),
        raw="{" + ("1" * 300) + "}",
        max_input_bytes=32,
    )
    assert oversized.record["prepare"]["status"] == "preparation_failed"
    assert oversized.record["prepare"]["error"]["category"] == "input_too_large"
    assert oversized.record["execution"]["status"] == "not_started"


def test_dispatch_ref_and_repository_are_fixed(tmp_path: Path) -> None:
    repo = tmp_path / "candidate"
    code_sha = make_library_repo(repo)
    wrong_repo = Request(
        1, "req-1", "other/repo", code_sha, "scripts/calculate_max_drawdown.py", "{}"
    )
    outcome = run_request(
        wrong_repo,
        candidate_root=repo,
        trusted_root=ROOT,
        output_dir=tmp_path / "out",
        run_id="7",
        run_attempt="1",
        workflow_sha=SHA,
        require_clean=True,
    )
    assert outcome.record["prepare"]["error"]["category"] == "repository_mismatch"
    rejected = _run(
        tmp_path / "ref",
        candidate=repo,
        code_sha=code_sha,
        raw="{}",
        in_github_actions=True,
        github_ref="refs/heads/feature",
    )
    assert rejected.record["prepare"]["error"]["category"] == "dispatch_ref_rejected"


def test_preflight_rejects_a_branch_name_without_a_record_on_success(
    tmp_path: Path,
) -> None:
    bad = _request("main", "scripts/calculate_max_drawdown.py", "{}")
    ok, outcome = preflight_request(
        bad,
        trusted_root=ROOT,
        output_dir=tmp_path / "bad",
        run_id="42",
        run_attempt="1",
        workflow_sha=SHA,
        github_ref="refs/heads/main",
        in_github_actions=True,
    )
    assert ok is False
    assert outcome is not None
    assert outcome.record["prepare"]["error"]["category"] == "invalid_sha"
    good = _request(SHA, "scripts/calculate_max_drawdown.py", "{}")
    ready, no_record = preflight_request(
        good,
        trusted_root=ROOT,
        output_dir=tmp_path / "good",
        run_id="42",
        run_attempt="1",
        workflow_sha=SHA,
        github_ref="refs/heads/main",
        in_github_actions=True,
    )
    assert ready is True
    assert no_record is None
    assert not (tmp_path / "good" / "execution_record.json").exists()


def test_credentials_are_removed_from_a_checkout(tmp_path: Path) -> None:
    repo = tmp_path / "checkout"
    write_files(repo, {"README.md": "x\n"})
    commit_repo(repo)
    git(repo, "config", "--local", "http.extraheader", "AUTHORIZATION: basic secret")
    result = scrub_repository(repo)
    assert "http.extraheader" in result["removed_keys"]
    listed = subprocess.run(
        ["git", "-C", str(repo), "config", "--local", "--get", "http.extraheader"],
        capture_output=True,
        text=True,
        check=False,
    )
    assert listed.returncode != 0
    assert "AUTHORIZATION" not in (repo / ".git" / "config").read_text(encoding="utf-8")


def test_cli_run_uses_the_environment_contract(tmp_path: Path) -> None:
    trusted = tmp_path / "trusted"
    for relative in RUNTIME_FILES:
        target = trusted / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes((ROOT / relative).read_bytes())
    workflow_sha = commit_repo(trusted)
    candidate = tmp_path / "candidate"
    code_sha = make_library_repo(candidate)
    output = tmp_path / "output"
    env = os.environ.copy()
    env.pop("BLOB_READ_WRITE_TOKEN", None)
    env.pop("GITHUB_OUTPUT", None)
    env.pop("GITHUB_STEP_SUMMARY", None)
    env.update(
        {
            "EXECUTION_SCHEMA_VERSION": "1",
            "EXECUTION_REQUEST_ID": "cli-req",
            "EXECUTION_REPOSITORY": REPOSITORY,
            "EXECUTION_CODE_SHA": code_sha,
            "EXECUTION_SCRIPT_PATH": "scripts/calculate_max_drawdown.py",
            "EXECUTION_INPUT_JSON": '{"equity_curve":[100,120,90,110]}',
            "EXECUTION_CANDIDATE_ROOT": str(candidate),
            "EXECUTION_TRUSTED_ROOT": str(trusted),
            "EXECUTION_OUTPUT_DIR": str(output),
            "GITHUB_RUN_ID": "99",
            "GITHUB_RUN_ATTEMPT": "1",
            "GITHUB_SHA": workflow_sha,
            "GITHUB_REF": "refs/heads/main",
            "GITHUB_ACTIONS": "true",
            "PYTHONPATH": str(trusted),
        }
    )
    completed = subprocess.run(
        [sys.executable, "-B", "-m", "execution.runner", "run"],
        cwd=trusted,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )
    assert completed.returncode == 0, completed.stderr
    record = json.loads((output / "execution_record.json").read_text(encoding="utf-8"))
    assert record["execution"]["result"] == {"max_drawdown": 0.25}
    assert record["prepare"]["credential_scrub"]["candidate"]["removed_keys"] == []


def test_runner_has_no_expected_drawdown_oracle() -> None:
    for relative in RUNTIME_FILES:
        if relative.endswith((".py", ".mjs")):
            text = (ROOT / relative).read_text(encoding="utf-8")
            assert "0.25" not in text
            assert "equity_curve" not in text


def test_canonical_json_rejects_nonfinite_and_sorts_keys() -> None:
    left = canonical_bytes({"b": 1, "a": [2, 3]})
    right = canonical_bytes({"a": [2, 3], "b": 1})
    assert left == right
    try:
        parse_single_json('{"value": Infinity}', depth_category="input_rejected")
    except Failure as exc:
        assert exc.category == "nonfinite_json"
    else:
        raise AssertionError("Infinity was accepted")


def test_workflow_trust_boundaries() -> None:
    text = WORKFLOW.read_text(encoding="utf-8")
    header, _, _rest = text.partition("\npermissions:\n")
    assert "workflow_dispatch:" in header
    assert "pull_request" not in header
    assert "push:" not in header
    upload_at = text.index("\n  upload:\n")
    execute = text[:upload_at]
    upload = text[upload_at:]
    assert "BLOB_READ_WRITE_TOKEN" not in execute
    assert upload.count("secrets.BLOB_READ_WRITE_TOKEN") == 1
    assert "environment: execution-upload" in upload
    assert "environment:" not in execute.split("jobs:", 1)[1]
    assert "inputs.code_sha" not in upload
    assert "execution.runner" not in upload
    assert "persist-credentials: false" in execute
    assert execute.count("persist-credentials: false") == 2
    assert upload.count("persist-credentials: false") == 1
    assert "contents: write" not in text
    assert "npm ci --ignore-scripts" in upload
    assert 'python-version: "3.12.16"' in text
    assert 'node-version: "22.23.4"' in text
    uses = re.findall(r"uses:\s+\S+", text)
    assert uses
    for pin in uses:
        assert re.search(r"@[0-9a-f]{40}(?:\s|#|$)", pin)
        assert "@v" not in pin
    config = json.loads(
        (ROOT / "execution" / "trust_config.json").read_text(encoding="utf-8")
    )
    assert config["blob"]["store_id"] == "store_CEauyrab8003cHZO"
    assert config["blob"]["access"] == "private"
    assert config["repository"] == REPOSITORY


def test_node_uploader_contracts() -> None:
    completed = subprocess.run(
        ["node", "--test", "execution/uploader/upload_record.test.mjs"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert completed.returncode == 0, completed.stdout + completed.stderr


def test_upload_cli_missing_credentials(tmp_path: Path) -> None:
    record = {
        "schema_version": 1,
        "record_type": "execution_record",
        "request_id": "req-1",
        "execution_id": "42-1",
        "repository": REPOSITORY,
        "status": "succeeded",
        "prepare": {"status": "prepared", "error": None},
        "execution": {
            "status": "succeeded",
            "exit_code": 0,
            "result": {"max_drawdown": 0.25},
            "error": None,
        },
    }
    record_path = tmp_path / "execution_record.json"
    payload = canonical_bytes(record)
    record_path.write_bytes(payload)
    receipt_path = tmp_path / "receipt.json"
    env = os.environ.copy()
    env.pop("BLOB_READ_WRITE_TOKEN", None)
    env.pop("VERCEL_OIDC_TOKEN", None)
    env.pop("GITHUB_OUTPUT", None)
    env.pop("GITHUB_STEP_SUMMARY", None)
    env.update(
        {
            "EXECUTION_RECORD_READY": "true",
            "EXECUTION_RECORD_PATH": str(record_path),
            "EXPECTED_RECORD_SHA256": hashlib.sha256(payload).hexdigest(),
            "EXECUTION_RECEIPT_PATH": str(receipt_path),
            "EXECUTION_TRUSTED_ROOT": str(ROOT),
            "GITHUB_RUN_ID": "42",
            "GITHUB_RUN_ATTEMPT": "1",
        }
    )
    completed = subprocess.run(
        ["node", "execution/uploader/upload_record.mjs"],
        cwd=ROOT,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )
    assert completed.returncode == 1
    receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    assert receipt["storage"]["status"] == "storage_failed"
    assert receipt["storage"]["error"]["category"] == "missing_credentials"
    assert receipt["computation"]["status"] == "succeeded"
    assert receipt["computation"]["result"] == {"max_drawdown": 0.25}
    assert "supersecret" not in receipt_path.read_text(encoding="utf-8")
