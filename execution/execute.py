"""Stage 2: run the prepared script and record the actual outcome."""

from __future__ import annotations

import os
import signal
import subprocess
import sys
import tempfile
import threading
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from execution.constants import MAX_STDERR_BYTES, MAX_STDOUT_BYTES, TIMEOUT_SECONDS
from execution.errors import Failure
from execution.jsonutil import parse_single_json, sha256_bytes


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ")


def not_started_execution(*, timeout_seconds: int) -> dict[str, Any]:
    return {
        "status": "not_started",
        "started_at": None,
        "finished_at": None,
        "timeout_seconds": timeout_seconds,
        "exit_code": None,
        "stdout": "",
        "stderr": "",
        "stdout_truncated": False,
        "stderr_truncated": False,
        "stdout_sha256": sha256_bytes(b""),
        "stderr_sha256": sha256_bytes(b""),
        "result": None,
        "error": None,
    }


def execute_script(
    *,
    trusted_root: Path,
    candidate_root: Path,
    script: Path,
    src: Path,
    input_raw: str,
    timeout_seconds: int = TIMEOUT_SECONDS,
    max_stdout_bytes: int = MAX_STDOUT_BYTES,
    max_stderr_bytes: int = MAX_STDERR_BYTES,
) -> dict[str, Any]:
    if src.is_symlink() or src.resolve() != candidate_root.resolve() / "src":
        raise Failure(
            "path_rejected", "Prepared src directory does not match the candidate."
        )
    bootstrap = trusted_root / "execution" / "bootstrap.py"
    if bootstrap.is_symlink() or not bootstrap.is_file():
        raise Failure("provenance_error", "Trusted bootstrap is missing.")
    started = utc_now()
    command = [
        sys.executable,
        "-I",
        "-B",
        str(bootstrap.resolve()),
        str(candidate_root.resolve()),
        str(script),
    ]
    with tempfile.TemporaryDirectory(prefix="execution-cwd-") as cwd:
        completed = _run_child(
            command,
            cwd=Path(cwd),
            input_bytes=input_raw.encode("utf-8"),
            timeout_seconds=timeout_seconds,
            max_stdout_bytes=max_stdout_bytes,
            max_stderr_bytes=max_stderr_bytes,
        )
    finished = utc_now()
    stdout_text, stdout_error = _decode(completed.stdout)
    stderr_text, stderr_error = _decode(completed.stderr)
    section: dict[str, Any] = {
        "status": "failed",
        "started_at": started,
        "finished_at": finished,
        "timeout_seconds": timeout_seconds,
        "exit_code": completed.exit_code,
        "stdout": stdout_text or "",
        "stderr": stderr_text or "",
        "stdout_truncated": completed.stdout_truncated,
        "stderr_truncated": completed.stderr_truncated,
        "stdout_sha256": sha256_bytes(completed.stdout),
        "stderr_sha256": sha256_bytes(completed.stderr),
        "stdout_undecodable": stdout_error,
        "stderr_undecodable": stderr_error,
        "result": None,
        "error": None,
    }
    section["error"] = _outcome_error(
        completed=completed,
        stdout_text=stdout_text,
        stdout_undecodable=stdout_error,
        timeout_seconds=timeout_seconds,
    )
    if section["error"] is None and stdout_text is not None:
        try:
            section["result"] = parse_single_json(
                stdout_text, depth_category="malformed_output"
            )
        except Failure as exc:
            section["error"] = exc.as_dict()
        else:
            section["status"] = "succeeded"
    return section


class _Completed:
    def __init__(
        self,
        *,
        exit_code: int | None,
        stdout: bytes,
        stderr: bytes,
        stdout_truncated: bool,
        stderr_truncated: bool,
        timed_out: bool,
        spawn_error: str | None,
    ) -> None:
        self.exit_code = exit_code
        self.stdout = stdout
        self.stderr = stderr
        self.stdout_truncated = stdout_truncated
        self.stderr_truncated = stderr_truncated
        self.timed_out = timed_out
        self.spawn_error = spawn_error


def _run_child(
    command: list[str],
    *,
    cwd: Path,
    input_bytes: bytes,
    timeout_seconds: int,
    max_stdout_bytes: int,
    max_stderr_bytes: int,
) -> _Completed:
    try:
        proc = subprocess.Popen(
            command,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=cwd,
            env=_child_env(cwd),
            start_new_session=True,
        )
    except OSError as exc:
        return _Completed(
            exit_code=None,
            stdout=b"",
            stderr=str(exc).encode("utf-8", errors="replace"),
            stdout_truncated=False,
            stderr_truncated=False,
            timed_out=False,
            spawn_error=str(exc),
        )
    out: dict[str, bytes | bool] = {}
    err: dict[str, bytes | bool] = {}
    assert proc.stdout is not None
    assert proc.stderr is not None
    threads = [
        threading.Thread(
            target=_read_capped,
            args=(proc.stdout, max_stdout_bytes, out, proc),
        ),
        threading.Thread(
            target=_read_capped,
            args=(proc.stderr, max_stderr_bytes, err, proc),
        ),
    ]
    for thread in threads:
        thread.start()
    timed_out = False
    try:
        if proc.stdin is not None:
            try:
                proc.stdin.write(input_bytes)
                proc.stdin.close()
            except BrokenPipeError:
                pass
        try:
            proc.wait(timeout=timeout_seconds)
        except subprocess.TimeoutExpired:
            timed_out = True
            _kill_group(proc)
            proc.wait(timeout=5)
    finally:
        _kill_group(proc)
        for thread in threads:
            thread.join(timeout=5)
    return _Completed(
        exit_code=proc.returncode,
        stdout=_as_bytes(out.get("data")),
        stderr=_as_bytes(err.get("data")),
        stdout_truncated=bool(out.get("truncated")),
        stderr_truncated=bool(err.get("truncated")),
        timed_out=timed_out,
        spawn_error=None,
    )


def _as_bytes(value: object) -> bytes:
    if isinstance(value, bytes):
        return value
    return b""


def _read_capped(
    pipe: object,
    limit: int,
    sink: dict[str, bytes | bool],
    proc: subprocess.Popen[bytes],
) -> None:
    data = bytearray()
    truncated = False
    reader = getattr(pipe, "read", None)
    if reader is None:
        sink["data"] = b""
        sink["truncated"] = False
        return
    while True:
        chunk = reader(65536)
        if not isinstance(chunk, bytes) or chunk == b"":
            break
        if truncated:
            continue
        if len(data) + len(chunk) > limit:
            data.extend(chunk[: max(0, limit - len(data))])
            truncated = True
            _kill_group(proc)
            continue
        data.extend(chunk)
    sink["data"] = bytes(data)
    sink["truncated"] = truncated


def _kill_group(proc: subprocess.Popen[bytes]) -> None:
    if not proc.pid:
        return
    try:
        os.killpg(proc.pid, signal.SIGKILL)
    except (ProcessLookupError, PermissionError, OSError):
        return


def _child_env(home: Path) -> dict[str, str]:
    return {
        "PATH": "/usr/bin:/bin",
        "LANG": "C.UTF-8",
        "LC_ALL": "C.UTF-8",
        "HOME": str(home),
        "TMPDIR": str(home),
    }


def _decode(data: bytes) -> tuple[str | None, bool]:
    try:
        return data.decode("utf-8"), False
    except UnicodeDecodeError:
        return None, True


def _outcome_error(
    *,
    completed: _Completed,
    stdout_text: str | None,
    stdout_undecodable: bool,
    timeout_seconds: int,
) -> dict[str, Any] | None:
    if completed.spawn_error is not None:
        return Failure(
            "spawn_failed",
            "The approved script could not be started.",
        ).as_dict()
    if completed.timed_out:
        return Failure(
            "timeout",
            "The approved script exceeded the time limit.",
            {"timeout_seconds": timeout_seconds, "exit_code": completed.exit_code},
        ).as_dict()
    if completed.stdout_truncated:
        return Failure(
            "output_too_large",
            "Script stdout exceeded the byte cap.",
            {"exit_code": completed.exit_code},
        ).as_dict()
    if completed.exit_code != 0:
        return Failure(
            "script_failed",
            "Approved script exited with a nonzero status.",
            {"exit_code": completed.exit_code},
        ).as_dict()
    if stdout_undecodable or stdout_text is None:
        return Failure(
            "malformed_output",
            "Script stdout was not valid UTF-8.",
            {"exit_code": completed.exit_code},
        ).as_dict()
    return None
