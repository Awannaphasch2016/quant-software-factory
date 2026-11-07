"""Runtime provenance captured from the trusted runner and candidate tree."""

from __future__ import annotations

import importlib.metadata
import json
import platform
import re
import sys
from pathlib import Path
from typing import Any

from execution.constants import LOCKFILES, REPOSITORY, RUNTIME_FILES, WORKFLOW_PATH
from execution.errors import Failure
from execution.jsonutil import sha256_bytes, sha256_file


def load_trust_config(trusted_root: Path) -> dict[str, Any]:
    path = trusted_root / "execution" / "trust_config.json"
    if path.is_symlink() or not path.is_file():
        raise Failure("provenance_error", "Trusted configuration is missing.")
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise Failure("provenance_error", "Trusted configuration is not JSON.") from exc
    if not isinstance(payload, dict):
        raise Failure("provenance_error", "Trusted configuration must be an object.")
    if payload.get("repository") != REPOSITORY:
        raise Failure(
            "provenance_error", "Trusted repository does not match the runner."
        )
    if payload.get("default_branch") != "main":
        raise Failure("provenance_error", "Trusted default branch must be main.")
    return payload


def file_set_sha256(trusted_root: Path) -> str:
    lines: list[str] = []
    for relative in RUNTIME_FILES:
        path = trusted_root / relative
        if path.is_symlink() or not path.is_file():
            raise Failure(
                "provenance_error",
                "A trusted runner file is missing.",
                {"path": relative},
            )
        lines.append(f"{relative}\0{sha256_file(str(path))}\n")
    return sha256_bytes("".join(lines).encode("utf-8"))


def workflow_file_sha256(trusted_root: Path) -> str:
    path = trusted_root / WORKFLOW_PATH
    if path.is_symlink() or not path.is_file():
        raise Failure("provenance_error", "Trusted workflow file is missing.")
    return sha256_file(str(path))


def dependency_provenance(candidate_root: Path) -> dict[str, Any]:
    lock_path: str | None = None
    lock_sha: str | None = None
    for name in LOCKFILES:
        path = candidate_root / name
        if path.is_symlink():
            raise Failure(
                "symlink_rejected",
                "Dependency lockfile is a symlink.",
                {"path": name},
            )
        if path.is_file():
            lock_path = name
            lock_sha = sha256_file(str(path))
            break
    pyproject = candidate_root / "pyproject.toml"
    pyproject_sha: str | None = None
    declared: list[str] | None = None
    if pyproject.is_symlink():
        raise Failure("symlink_rejected", "pyproject.toml is a symlink.")
    if pyproject.is_file():
        raw = pyproject.read_bytes()
        pyproject_sha = sha256_bytes(raw)
        declared = _declared_dependencies(raw.decode("utf-8", errors="replace"))
    return {
        "dependencies_lock_sha256": lock_sha,
        "dependencies_lock_path": lock_path,
        "pyproject_sha256": pyproject_sha,
        "declared_runtime_dependencies": declared,
        "installed_for_execution": False,
    }


def interpreter_provenance() -> dict[str, Any]:
    distributions: list[dict[str, str]] = []
    for dist in importlib.metadata.distributions():
        name = dist.metadata.get("Name")
        if not isinstance(name, str) or name == "":
            continue
        distributions.append({"name": name, "version": dist.version})
    distributions.sort(key=lambda item: item["name"].casefold())
    return {
        "python": {
            "version": platform.python_version(),
            "implementation": platform.python_implementation(),
            "version_info": list(sys.version_info[:3]),
            "sys_version": sys.version,
        },
        "platform": {
            "system": platform.system(),
            "release": platform.release(),
            "machine": platform.machine(),
        },
        "installed_distributions": distributions,
    }


def _declared_dependencies(pyproject: str) -> list[str] | None:
    if "[project]" not in pyproject:
        return None
    section = pyproject.split("[project]", 1)[1]
    section = re.split(r"(?m)^\[", section, maxsplit=1)[0]
    match = re.search(r"(?m)^dependencies\s*=\s*\[(.*?)\]", section, re.S)
    if match is None:
        return None
    body = match.group(1).strip()
    if body == "":
        return []
    return re.findall(r"['\"]([^'\"]+)['\"]", body)
