"""Remove persisted git credentials before any approved script runs."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from execution.gitutil import git

_KEYS = ("http.extraheader", "credential.helper")


def scrub_repository(repo: Path) -> dict[str, Any]:
    removed: list[str] = []
    for key in _KEYS:
        listed = git(repo, "config", "--local", "--get-all", key)
        if listed.returncode != 0 or not listed.stdout.strip():
            continue
        unset = git(repo, "config", "--local", "--unset-all", key)
        if unset.returncode == 0:
            removed.append(key)
    sanitized = _strip_authorization(repo / ".git" / "config")
    return {"removed_keys": removed, "sanitized_config": sanitized}


def _strip_authorization(config_path: Path) -> bool:
    if config_path.is_symlink() or not config_path.is_file():
        return False
    original = config_path.read_text(encoding="utf-8", errors="replace")
    kept: list[str] = []
    changed = False
    for line in original.splitlines(keepends=True):
        upper = line.upper()
        if "AUTHORIZATION" in upper or "EXTRAHEADER" in upper:
            changed = True
            continue
        kept.append(line)
    if changed:
        config_path.write_text("".join(kept), encoding="utf-8")
    return changed
