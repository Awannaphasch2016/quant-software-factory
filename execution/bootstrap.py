"""Trusted launcher for one allowlisted script.

Isolated Python ignores PYTHONPATH. This process inserts only the candidate
``src`` directory, then executes the already validated script path.
"""

from __future__ import annotations

import sys
from pathlib import Path


def main() -> int:
    if len(sys.argv) != 3:
        print("bootstrap expected <candidate_root> <script>", file=sys.stderr)
        return 2
    candidate = Path(sys.argv[1])
    script = Path(sys.argv[2])
    if candidate.is_symlink() or script.is_symlink():
        print("bootstrap rejected a symlink", file=sys.stderr)
        return 2
    root = candidate.resolve()
    src = root / "src"
    script_resolved = script.resolve()
    if (
        src.is_symlink()
        or not src.is_dir()
        or not src.resolve().is_relative_to(root)
        or not script_resolved.is_file()
        or not script_resolved.is_relative_to(root)
    ):
        print("bootstrap rejected the candidate paths", file=sys.stderr)
        return 2
    sys.path.insert(0, str(src))
    import runpy

    runpy.run_path(str(script_resolved), run_name="__main__")
    return 0


if __name__ == "__main__":
    sys.exit(main())
