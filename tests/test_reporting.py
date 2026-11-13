"""Tests for quant_software_factory.reporting (data layer and Layer A checks)."""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
from datetime import date
from pathlib import Path
from typing import Any

import pytest

from quant_software_factory.reporting import FixtureSource
from quant_software_factory.reporting.check_data import main

REPO = Path(__file__).resolve().parents[1]
FIXTURE = REPO / "data" / "fixtures" / "demo_coop_rg_2026_10_v2"
COMMITTED = REPO / "reports" / "demo_coop_rg_2026_10_v2" / "checks.json"
ACCOUNT = "DEMO-0001"
CHECK_NAMES = sorted(
    [
        "A1_freshness_nav_daily",
        "A2_account_info_has_rows",
        "A2_holdings_daily_has_rows",
        "A2_nav_daily_as_of_date",
        "A2_nav_daily_has_rows",
        "A2_nav_daily_opening_date",
        "A2_performance_as_of_month",
        "A2_performance_has_rows",
        "A3_schema_account_info",
        "A3_schema_cash_flow",
        "A3_schema_holdings_daily",
        "A3_schema_nav_daily",
        "A3_schema_performance",
        "A3_schema_transactions",
    ]
)


def _run(root: Path, out: Path) -> tuple[int, list[dict[str, Any]]]:
    rc = main(
        [
            str(root),
            "--account",
            ACCOUNT,
            "--opening",
            "2026-09-30",
            "--as-of",
            "2026-10-30",
            "--out",
            str(out),
        ]
    )
    results: list[dict[str, Any]] = json.loads(
        (out / "checks.json").read_text(encoding="utf-8")
    )
    return rc, results


def _by_name(results: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    return {r["name"]: r for r in results}


def _copy_fixture(tmp_path: Path) -> Path:
    root = tmp_path / "data"
    shutil.copytree(FIXTURE, root)
    return root


def _edit(path: Path, edits: list[tuple[str, str]]) -> None:
    text = path.read_text(encoding="utf-8")
    for old, new in edits:
        assert old in text, old
        text = text.replace(old, new)
    path.write_text(text, encoding="utf-8")


@pytest.mark.parametrize(
    ("dataset", "as_of", "accounts", "expected"),
    [
        ("account_info", date(2026, 10, 30), [ACCOUNT], 1),
        ("nav_daily", date(2026, 10, 30), [ACCOUNT], 2),
        ("nav_daily", date(2026, 9, 30), [ACCOUNT], 1),
        ("holdings_daily", date(2026, 10, 30), [ACCOUNT], 2),
        ("transactions", date(2026, 10, 30), [ACCOUNT], 4),
        ("transactions", date(2026, 10, 12), [ACCOUNT], 2),
        ("cash_flow", date(2026, 10, 30), [ACCOUNT], 1),
        ("performance", date(2026, 10, 30), [ACCOUNT], 1),
        ("nav_daily", date(2026, 10, 30), ["OTHER"], 0),
    ],
)
def test_load_expected_rows(
    dataset: str, as_of: date, accounts: list[str], expected: int
) -> None:
    rows = FixtureSource(FIXTURE).load(dataset, as_of, accounts)
    assert len(rows) == expected
    assert all(isinstance(v, str) for row in rows for v in row.values())


def test_load_unknown_dataset_raises_keyerror() -> None:
    with pytest.raises(KeyError):
        FixtureSource(FIXTURE).load("unknown", date(2026, 10, 30), [ACCOUNT])


def test_fixture_all_checks_pass(tmp_path: Path) -> None:
    rc, results = _run(FIXTURE, tmp_path)
    assert rc == 0
    assert [r["name"] for r in results] == CHECK_NAMES
    for r in results:
        assert list(r) == ["name", "layer", "passed", "expected", "actual"]
        assert r["layer"] == "A"
        assert r["passed"] is True


def test_checks_json_deterministic_and_matches_committed(tmp_path: Path) -> None:
    first, second = tmp_path / "one", tmp_path / "two"
    _run(FIXTURE, first)
    _run(FIXTURE, second)
    data = (first / "checks.json").read_bytes()
    assert data == (second / "checks.json").read_bytes()
    assert data == COMMITTED.read_bytes()
    assert data.endswith(b"\n")


NAV_OPENING_ROW = "2026-09-30,DEMO-0001,715000.00,100000.00,615000.00\n"
PERF_ROW = "2026-10,DEMO-0001,14798.00,3600.00,9000.00,27398.00,3.83\n"


@pytest.mark.parametrize(
    ("file_name", "edits", "failing_check"),
    [
        (
            "nav_daily.csv",
            [("2026-10-30,DEMO-0001", "2026-10-29,DEMO-0001")],
            "A1_freshness_nav_daily",
        ),
        ("nav_daily.csv", [(NAV_OPENING_ROW, "")], "A2_nav_daily_opening_date"),
        ("performance.csv", [(PERF_ROW, "")], "A2_performance_has_rows"),
        ("holdings_daily.csv", None, "A3_schema_holdings_daily"),
        (
            "cash_flow.csv",
            [("flow_type,amount\n", "flow_type\n"), ("DEPOSIT,50000.00", "DEPOSIT")],
            "A3_schema_cash_flow",
        ),
        (
            "cash_flow.csv",
            [("amount\n", "amount,note\n"), ("50000.00\n", "50000.00,x\n")],
            "A3_schema_cash_flow",
        ),
        ("nav_daily.csv", [("792398.00", "79x398.00")], "A3_schema_nav_daily"),
        (
            "transactions.csv",
            [("BBB,DIVIDEND", "BBB,TRANSFER")],
            "A3_schema_transactions",
        ),
        (
            "transactions.csv",
            [("164835.00,17835.00", "164835.00,")],
            "A3_schema_transactions",
        ),
    ],
)
def test_failing_inputs(
    tmp_path: Path,
    file_name: str,
    edits: list[tuple[str, str]] | None,
    failing_check: str,
) -> None:
    root = _copy_fixture(tmp_path)
    if edits is None:
        (root / file_name).unlink()
    else:
        _edit(root / file_name, edits)
    rc, results = _run(root, tmp_path / "out")
    assert rc == 1
    assert _by_name(results)[failing_check]["passed"] is False


def test_missing_holdings_reports_dependent_checks_not_run(tmp_path: Path) -> None:
    root = _copy_fixture(tmp_path)
    (root / "holdings_daily.csv").unlink()
    rc, results = _run(root, tmp_path / "out")
    checks = _by_name(results)
    assert rc == 1
    assert checks["A3_schema_holdings_daily"]["actual"] == (
        "holdings_daily.csv not found"
    )
    dependent = checks["A2_holdings_daily_has_rows"]
    assert dependent["passed"] is False
    assert dependent["actual"] == "not run: A3_schema_holdings_daily failed"
    failed = sorted(name for name, r in checks.items() if not r["passed"])
    assert failed == ["A2_holdings_daily_has_rows", "A3_schema_holdings_daily"]


@pytest.mark.parametrize(
    ("file_name", "edits", "message"),
    [
        ("nav_daily.csv", [("792398.00", "79x398.00")], "nav '79x398.00'"),
        ("transactions.csv", [("BBB,DIVIDEND", "BBB,TRANSFER")], "side 'TRANSFER'"),
        (
            "transactions.csv",
            [("164835.00,17835.00", "164835.00,")],
            "row 2: realized_pl is required for SELL",
        ),
        ("cash_flow.csv", [("amount\n", "amount,note\n")], "extra fields: note"),
        ("nav_daily.csv", [("2026-09-30", "2026-13-01")], "is not an ISO date"),
    ],
)
def test_schema_failure_messages(
    tmp_path: Path, file_name: str, edits: list[tuple[str, str]], message: str
) -> None:
    root = _copy_fixture(tmp_path)
    _edit(root / file_name, edits)
    _, results = _run(root, tmp_path / "out")
    dataset = file_name.removesuffix(".csv")
    assert message in _by_name(results)[f"A3_schema_{dataset}"]["actual"]


def test_empty_transactions_and_cash_flow_pass(tmp_path: Path) -> None:
    root = _copy_fixture(tmp_path)
    for name in ("transactions.csv", "cash_flow.csv"):
        path = root / name
        header = path.read_text(encoding="utf-8").splitlines()[0]
        path.write_text(header + "\n", encoding="utf-8")
    rc, results = _run(root, tmp_path / "out")
    assert rc == 0
    assert all(r["passed"] for r in results)


def test_module_entrypoint(tmp_path: Path) -> None:
    proc = subprocess.run(
        [
            sys.executable,
            "-m",
            "quant_software_factory.reporting.check_data",
            str(FIXTURE),
            "--account",
            ACCOUNT,
            "--opening",
            "2026-09-30",
            "--as-of",
            "2026-10-30",
            "--out",
            str(tmp_path),
        ],
        check=False,
        capture_output=True,
        text=True,
    )
    assert proc.returncode == 0, proc.stderr
    assert (tmp_path / "checks.json").read_bytes() == COMMITTED.read_bytes()
