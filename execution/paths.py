"""Allowlisted script paths. Symlinks and escapes are rejected."""

from __future__ import annotations

import json
from pathlib import Path, PurePosixPath

from execution.errors import Failure


def normalize_script_path(script_path: str) -> str:
    if not isinstance(script_path, str) or script_path == "":
        raise Failure("path_rejected", "Script path must be a non-empty string.")
    if len(script_path) > 256:
        raise Failure("path_rejected", "Script path is too long.")
    if (
        "\x00" in script_path
        or "\\" in script_path
        or script_path.startswith("/")
        or any(character.isspace() for character in script_path)
    ):
        raise Failure(
            "path_rejected",
            "Script path must be a repo-relative POSIX path without whitespace.",
        )
    pure = PurePosixPath(script_path)
    if pure.is_absolute() or ".." in pure.parts or "." in pure.parts:
        raise Failure("path_rejected", "Script path must not contain '.' or '..'.")
    if pure.as_posix() != script_path or not script_path.endswith(".py"):
        raise Failure(
            "path_rejected",
            "Script path must be a normalized relative .py path.",
        )
    return script_path


def load_allowlist(trusted_root: Path) -> tuple[str, ...]:
    path = trusted_root / "execution" / "allowlist.json"
    if path.is_symlink() or not path.is_file():
        raise Failure("path_rejected", "Trusted allowlist is missing.")
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise Failure("path_rejected", "Trusted allowlist is not JSON.") from exc
    if not isinstance(payload, dict) or payload.get("schema_version") != 1:
        raise Failure("path_rejected", "Trusted allowlist schema is not version 1.")
    scripts = payload.get("scripts")
    if not isinstance(scripts, list) or not scripts:
        raise Failure("path_rejected", "Trusted allowlist has no scripts.")
    normalized: list[str] = []
    for entry in scripts:
        if not isinstance(entry, str):
            raise Failure("path_rejected", "Allowlist entries must be strings.")
        normalized.append(normalize_script_path(entry))
    if len(set(normalized)) != len(normalized):
        raise Failure("path_rejected", "Allowlist contains duplicate paths.")
    return tuple(normalized)


def resolve_src(candidate_root: Path) -> Path:
    root = _real_directory(candidate_root, "candidate root")
    src = root / "src"
    if src.is_symlink():
        raise Failure("symlink_rejected", "candidate src is a symlink.")
    if not src.is_dir():
        raise Failure("src_missing", "candidate src directory is missing.")
    if src.resolve() != src:
        raise Failure("symlink_rejected", "candidate src does not resolve canonically.")
    if not src.resolve().is_relative_to(root):
        raise Failure(
            "path_rejected", "candidate src resolves outside the candidate root."
        )
    return src


def resolve_script(
    candidate_root: Path, script_path: str, allowlist: tuple[str, ...]
) -> Path:
    normalized = normalize_script_path(script_path)
    if normalized not in allowlist:
        raise Failure(
            "script_not_allowlisted",
            "Script path is not on the trusted allowlist.",
            {"script_path": normalized},
        )
    root = _real_directory(candidate_root, "candidate root")
    current = root
    for part in PurePosixPath(normalized).parts:
        current = current / part
        if current.is_symlink():
            raise Failure(
                "symlink_rejected",
                "Script path contains a symlink.",
                {"component": part},
            )
        if not current.exists():
            raise Failure(
                "script_not_found",
                "Allowlisted script does not exist at this commit.",
                {"script_path": normalized},
            )
    if not current.is_file():
        raise Failure("path_rejected", "Allowlisted script path is not a file.")
    resolved = current.resolve()
    if resolved != current or not resolved.is_relative_to(root):
        raise Failure(
            "path_rejected", "Script path resolves outside the candidate root."
        )
    return resolved


def _real_directory(path: Path, label: str) -> Path:
    if path.is_symlink():
        raise Failure("symlink_rejected", f"{label} is a symlink.")
    root = path.resolve()
    if not root.is_dir():
        raise Failure("candidate_missing", f"{label} is not a directory.")
    return root
