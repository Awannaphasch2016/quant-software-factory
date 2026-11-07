"""Helpers for execution-runner tests."""

from __future__ import annotations

import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

LIBRARY_FILES = (
    "src/quant_software_factory/__init__.py",
    "src/quant_software_factory/risk.py",
    "src/quant_software_factory/py.typed",
    "scripts/calculate_max_drawdown.py",
    "pyproject.toml",
)


def git(repo: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", "-C", str(repo), *args],
        check=True,
        capture_output=True,
        text=True,
    )


def commit_repo(repo: Path) -> str:
    git(repo, "init")
    git(repo, "config", "user.email", "execution-test@example.com")
    git(repo, "config", "user.name", "Execution Test")
    git(repo, "add", ".")
    git(repo, "commit", "-m", "candidate")
    return git(repo, "rev-parse", "HEAD").stdout.strip()


def write_files(repo: Path, files: dict[str, str]) -> None:
    for relative, content in files.items():
        path = repo / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")


def copy_library(repo: Path) -> None:
    for relative in LIBRARY_FILES:
        target = repo / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes((ROOT / relative).read_bytes())


def make_library_repo(repo: Path) -> str:
    copy_library(repo)
    return commit_repo(repo)
