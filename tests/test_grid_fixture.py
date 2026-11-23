"""Tests for the Grid Trade Performance datasets (issue #25, part 1 of #23)."""

from __future__ import annotations

from datetime import date
from pathlib import Path

import pytest

from quant_software_factory.reporting import SCHEMAS, FixtureSource, SqliteSource
from quant_software_factory.reporting.make_private_db import read_csv, write_db
from quant_software_factory.reporting.schema import RETURNS_DATASETS, validate_rows

REPO = Path(__file__).resolve().parents[1]
GRID = REPO / "data" / "fixtures" / "demo_grid_2026_11"
AS_OF = date(2026, 11, 6)
ACCOUNT = "DEMO-0001"
GRID_DATASETS: tuple[str, ...] = (
    "account_info",
    "nav_daily",
    "holdings_daily",
    "transactions",
    "grid_setup",
    "grid_cash",
)
ROW_COUNTS: dict[str, int] = {
    "account_info": 1,
    "nav_daily": 35,
    "holdings_daily": 105,
    "transactions": 26,
    "grid_setup": 3,
    "grid_cash": 105,
}


def _grid_db(tmp_path: Path) -> Path:
    db = tmp_path / "grid.db"
    write_db(db, {dataset: read_csv(GRID, dataset) for dataset in GRID_DATASETS})
    return db


def test_grid_fixture_files_match_datasets() -> None:
    assert {p.stem for p in GRID.glob("*.csv")} == set(GRID_DATASETS)


@pytest.mark.parametrize("dataset", GRID_DATASETS)
def test_grid_fixture_schema_valid(dataset: str) -> None:
    rows = FixtureSource(GRID).load(dataset, AS_OF, [ACCOUNT])
    assert validate_rows(dataset, rows) == []
    assert len(rows) == ROW_COUNTS[dataset]


def test_grid_setup_rows() -> None:
    rows = FixtureSource(GRID).load("grid_setup", AS_OF, [ACCOUNT])
    assert [(r["instrument"], r["display_order"]) for r in rows] == [
        ("AAA", "1"),
        ("BBB", "2"),
        ("CCC", "3"),
    ]


def test_grid_setup_has_no_date_field() -> None:
    names = {spec.name for spec in SCHEMAS["grid_setup"]}
    assert "date" not in names
    assert "period" not in names
    rows = FixtureSource(GRID).load("grid_setup", date(2024, 1, 1), [ACCOUNT])
    assert len(rows) == 3


def test_grid_cash_value() -> None:
    rows = FixtureSource(GRID).load("grid_cash", AS_OF, [ACCOUNT])
    matches = [
        r["cash"]
        for r in rows
        if r["date"] == "2026-11-06" and r["instrument"] == "BBB"
    ]
    assert matches == ["249824.70"]


def test_grid_cash_limited_to_as_of() -> None:
    source = FixtureSource(GRID)
    full = source.load("grid_cash", AS_OF, [ACCOUNT])
    earlier = source.load("grid_cash", date(2026, 3, 25), [ACCOUNT])
    assert 0 < len(earlier) < len(full)
    assert all(r["date"] <= "2026-03-25" for r in earlier)


def test_grid_transactions_adjustment_sides() -> None:
    rows = FixtureSource(GRID).load("transactions", AS_OF, [ACCOUNT])
    sides = [r["side"] for r in rows]
    assert sides.count("PORT_ADJUSTED") == 1
    assert sides.count("GAIN_ADJUSTMENT") == 1


def test_unknown_side_still_rejected() -> None:
    row = FixtureSource(GRID).load("transactions", AS_OF, [ACCOUNT])[0]
    errors = validate_rows("transactions", [{**row, "side": "FOO"}])
    assert len(errors) == 1
    assert "side 'FOO'" in errors[0]


def test_returns_datasets() -> None:
    assert set(RETURNS_DATASETS) <= set(SCHEMAS)
    assert len(RETURNS_DATASETS) == 6
    assert "grid_setup" not in RETURNS_DATASETS
    assert "grid_cash" not in RETURNS_DATASETS


@pytest.mark.parametrize("dataset", GRID_DATASETS)
@pytest.mark.parametrize(
    ("as_of", "accounts"),
    [
        (AS_OF, [ACCOUNT]),
        (date(2026, 3, 25), [ACCOUNT]),
        (date(2024, 2, 28), [ACCOUNT]),
        (date(2024, 1, 1), [ACCOUNT]),
        (AS_OF, ["OTHER"]),
        (AS_OF, []),
    ],
)
def test_grid_sqlite_matches_fixture(
    tmp_path: Path, dataset: str, as_of: date, accounts: list[str]
) -> None:
    db = _grid_db(tmp_path)
    expected = FixtureSource(GRID).load(dataset, as_of, accounts)
    actual = SqliteSource(db).load(dataset, as_of, accounts)
    assert actual == expected
    assert all(isinstance(v, str) for row in actual for v in row.values())


def test_grid_sqlite_expected_values(tmp_path: Path) -> None:
    source = SqliteSource(_grid_db(tmp_path))
    for dataset in GRID_DATASETS:
        assert len(source.load(dataset, AS_OF, [ACCOUNT])) == ROW_COUNTS[dataset]
    setup = source.load("grid_setup", AS_OF, [ACCOUNT])
    assert [r["display_order"] for r in setup] == ["1", "2", "3"]
    cash = source.load("grid_cash", AS_OF, [ACCOUNT])
    assert {
        "date": "2026-11-06",
        "account_no": ACCOUNT,
        "instrument": "BBB",
        "cash": "249824.70",
    } in cash
