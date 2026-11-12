"""Layer 1: bad inputs are rejected with exit 1 and no report.md."""

from __future__ import annotations

import json
import shutil
from pathlib import Path

import pytest

from quant_software_factory.reports.returns_transactions.cli import main

REPO_ROOT = Path(__file__).resolve().parents[1]
FIXTURE_DIR = REPO_ROOT / "data" / "examples" / "demo_coop_rg_2026_10"


def _copy_fixture(tmp_path: Path) -> Path:
    target = tmp_path / "demo_coop_rg_2026_10"
    shutil.copytree(FIXTURE_DIR, target)
    return target


def _edit(path: Path, old: str, new: str) -> None:
    text = path.read_text(encoding="utf-8")
    assert old in text
    path.write_bytes(text.replace(old, new).encode("utf-8"))


def _run_and_load_checks(input_dir: Path, output_dir: Path) -> dict[str, bool]:
    code = main([str(input_dir), str(output_dir)])
    assert code == 1
    assert not (output_dir / "report.md").exists()
    assert not (output_dir / "report.json").exists()
    assert not (output_dir / "narrative.md").exists()
    checks = json.loads((output_dir / "checks.json").read_text(encoding="utf-8"))
    assert isinstance(checks, list)
    for check in checks:
        assert set(check) == {"name", "passed", "expected", "actual"}
    return {check["name"]: check["passed"] for check in checks}


def test_missing_column_is_rejected(tmp_path: Path) -> None:
    input_dir = _copy_fixture(tmp_path)
    path = input_dir / "transactions.csv"
    lines = path.read_text(encoding="utf-8").splitlines()
    rewritten = []
    for line in lines:
        fields = line.split(",")
        del fields[6]  # the tax column
        rewritten.append(",".join(fields))
    path.write_bytes(("\n".join(rewritten) + "\n").encode("utf-8"))

    results = _run_and_load_checks(input_dir, tmp_path / "out")
    assert results["input.columns.transactions.csv"] is False


def test_sell_exceeding_holdings_is_rejected(tmp_path: Path) -> None:
    input_dir = _copy_fixture(tmp_path)
    _edit(
        input_dir / "transactions.csv",
        "2026-10-12,AAA,SELL,3000,",
        "2026-10-12,AAA,SELL,20000,",
    )
    results = _run_and_load_checks(input_dir, tmp_path / "out")
    assert results["input.sell_volume"] is False


def test_missing_closing_price_is_rejected(tmp_path: Path) -> None:
    input_dir = _copy_fixture(tmp_path)
    _edit(input_dir / "prices.csv", "2026-10-30,AAA,52.00\n", "")
    results = _run_and_load_checks(input_dir, tmp_path / "out")
    assert results["input.prices.closing"] is False
    assert results["input.prices.opening"] is True


def test_missing_opening_price_is_rejected(tmp_path: Path) -> None:
    input_dir = _copy_fixture(tmp_path)
    _edit(input_dir / "prices.csv", "2026-09-30,BBB,21.00\n", "")
    results = _run_and_load_checks(input_dir, tmp_path / "out")
    assert results["input.prices.opening"] is False


def test_unknown_side_is_rejected(tmp_path: Path) -> None:
    input_dir = _copy_fixture(tmp_path)
    _edit(input_dir / "transactions.csv", "AAA,SELL,", "AAA,SWAP,")
    results = _run_and_load_checks(input_dir, tmp_path / "out")
    assert results["input.sides"] is False


def test_out_of_period_trade_date_is_rejected(tmp_path: Path) -> None:
    input_dir = _copy_fixture(tmp_path)
    _edit(input_dir / "transactions.csv", "2026-10-26,CASH", "2026-11-02,CASH")
    results = _run_and_load_checks(input_dir, tmp_path / "out")
    assert results["input.dates.transactions"] is False


def test_out_of_period_price_date_is_rejected(tmp_path: Path) -> None:
    input_dir = _copy_fixture(tmp_path)
    _edit(input_dir / "prices.csv", "2026-09-30,BBB", "2026-09-29,BBB")
    results = _run_and_load_checks(input_dir, tmp_path / "out")
    assert results["input.dates.prices"] is False


def test_non_numeric_price_is_rejected(tmp_path: Path) -> None:
    input_dir = _copy_fixture(tmp_path)
    _edit(input_dir / "prices.csv", "2026-10-30,BBB,19.00", "2026-10-30,BBB,abc")
    results = _run_and_load_checks(input_dir, tmp_path / "out")
    assert results["input.parse.prices.csv"] is False
    # Dependent checks are omitted after a structural failure.
    assert "input.prices.closing" not in results


def test_missing_file_is_rejected(tmp_path: Path) -> None:
    input_dir = _copy_fixture(tmp_path)
    (input_dir / "prices.csv").unlink()
    results = _run_and_load_checks(input_dir, tmp_path / "out")
    assert results["input.files.prices.csv"] is False


@pytest.mark.parametrize(
    ("old", "new"),
    [
        ("2026-10-26,CASH,DEPOSIT,,,0.00,0.00,50000.00", "2026-10-26,CASH,DEPOSIT"),
        ("AAA,BUY,2000,", "AAA,BUY,,"),
        ("2026-10-05,", "2026-13-05,"),
    ],
    ids=["wrong-field-count", "blank-buy-qty", "invalid-date"],
)
def test_malformed_transaction_rows_are_rejected(
    tmp_path: Path, old: str, new: str
) -> None:
    input_dir = _copy_fixture(tmp_path)
    _edit(input_dir / "transactions.csv", old, new)
    results = _run_and_load_checks(input_dir, tmp_path / "out")
    assert results["input.parse.transactions.csv"] is False
