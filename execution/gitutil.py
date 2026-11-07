"""Git helpers that do not run repository hooks."""

from __future__ import annotations

import re
import subprocess
from pathlib import Path

from execution.constants import SHA_PATTERN
from execution.errors import Failure

_SHA = re.compile(SHA_PATTERN)


def git(repo: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [
            "git",
            "-c",
            "core.hooksPath=/dev/null",
            "-c",
            "protocol.file.allow=never",
            "-C",
            str(repo),
            *args,
        ],
        capture_output=True,
        text=True,
        check=False,
    )


def git_output(repo: Path, *args: str) -> str:
    completed = git(repo, *args)
    if completed.returncode != 0:
        detail = (completed.stderr or completed.stdout or "").strip()
        raise Failure(
            "git_unavailable",
            "git command failed while resolving the candidate commit.",
            {"args": list(args), "stderr": detail[:500]},
        )
    return completed.stdout.strip()


def resolve_commit(repo: Path, requested_sha: str) -> str:
    if not isinstance(requested_sha, str) or _SHA.fullmatch(requested_sha) is None:
        raise Failure(
            "invalid_sha",
            "code_sha must be the full 40-character lowercase commit SHA.",
        )
    if not (repo / ".git").exists():
        raise Failure("git_unavailable", "Candidate directory is not a git checkout.")
    head = git_output(repo, "rev-parse", "HEAD")
    kind = git_output(repo, "cat-file", "-t", requested_sha)
    verified = git_output(repo, "rev-parse", "--verify", f"{requested_sha}^{{commit}}")
    if kind != "commit" or head != requested_sha or verified != requested_sha:
        raise Failure(
            "sha_mismatch",
            "Candidate checkout HEAD is not the requested commit.",
            {"requested_code_sha": requested_sha, "resolved_code_sha": head},
        )
    return head


def worktree_dirty(repo: Path) -> bool:
    completed = git(repo, "status", "--porcelain")
    if completed.returncode != 0:
        raise Failure(
            "git_unavailable",
            "git status failed.",
            {"stderr": (completed.stderr or "")[:500]},
        )
    return bool(completed.stdout.strip())
