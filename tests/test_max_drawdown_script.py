"""Entry point for calculate_max_drawdown. The scalar function is unchanged."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from quant_software_factory.risk import calculate_max_drawdown

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "calculate_max_drawdown.py"


def _run(payload: object) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPT)],
        input=json.dumps(payload),
        capture_output=True,
        text=True,
        check=False,
        cwd=ROOT,
        env={"PYTHONPATH": str(ROOT / "src"), "PATH": "/usr/bin:/bin"},
    )


def test_entry_point_returns_library_value() -> None:
    curve = [100, 120, 90, 110]
    completed = _run({"equity_curve": curve})
    assert completed.returncode == 0
    assert completed.stderr == ""
    body = json.loads(completed.stdout)
    assert body == {"max_drawdown": calculate_max_drawdown(curve)}
    assert body["max_drawdown"] == 0.25


def test_entry_point_reports_invalid_curve_without_a_traceback() -> None:
    completed = _run({"equity_curve": []})
    assert completed.returncode == 1
    assert "empty" in completed.stderr
    assert "Traceback" not in completed.stderr
    assert completed.stdout == ""
