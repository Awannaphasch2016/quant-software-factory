"""Tests for the private data boundary: SqliteSource, make_private_db, private_run."""

from __future__ import annotations

import hashlib
import json
import os
import re
import sqlite3
import subprocess
import sys
from collections.abc import Iterator
from contextlib import closing
from datetime import date
from pathlib import Path
from typing import Any

import pytest

from quant_software_factory.reporting import (
    SCHEMAS,
    DatasetError,
    FixtureSource,
    SqliteSource,
)
from quant_software_factory.reporting import (
    private_run as private_run_module,
)
from quant_software_factory.reporting import (
    returns_transactions as returns_transactions_module,
)
from quant_software_factory.reporting.checks import CheckResult
from quant_software_factory.reporting.make_private_db import main as make_db
from quant_software_factory.reporting.make_private_db import scale_value
from quant_software_factory.reporting.private_run import (
    build_result,
    find_repo_root,
    is_inside,
    leak_check,
)
from quant_software_factory.reporting.private_run import main as private_run

REPO = Path(__file__).resolve().parents[1]
FIXTURE = REPO / "data" / "fixtures" / "demo_coop_rg_2026_10_v2"
REPORT_ID = "demo_coop_rg_2026_10_v2"
COMMITTED = REPO / "reports" / REPORT_ID
PACKAGE = REPO / "src" / "quant_software_factory" / "reporting"
ACCOUNT = "DEMO-0001"
CLIENT = "DEMO-COOP"
PRIVATE_ACCOUNT = "PRIV-0001"
PRIVATE_CLIENT = "PRIVATE-CLIENT"
AS_OF = date(2026, 10, 30)
DATES = ["--opening", "2026-09-30", "--as-of", "2026-10-30"]
REPORT_FILES = ["narrative.md", "report.json", "report.md"]
PRIVATE_FILES = ["checks.json", *REPORT_FILES]
RESULT_KEYS = ["status", "checks_total", "checks_failed", "checks"]
CHECK_KEYS = ["name", "layer", "passed"]


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _make(tmp_path: Path, name: str = "private.db", *options: str) -> Path:
    db = tmp_path / name
    assert make_db([str(FIXTURE), str(db), *options]) == 0
    return db


def _run(
    db: Path, out: Path, result: Path, account: str = ACCOUNT
) -> tuple[int, dict[str, Any] | None]:
    rc = private_run(
        [
            "--db",
            str(db),
            "--private-out",
            str(out),
            "--result",
            str(result),
            "--account",
            account,
            *DATES,
        ]
    )
    if not result.exists():
        return rc, None
    data: dict[str, Any] = json.loads(result.read_text(encoding="utf-8"))
    return rc, data


def _private_checks(out: Path) -> dict[str, dict[str, Any]]:
    results: list[dict[str, Any]] = json.loads(
        (out / "checks.json").read_text(encoding="utf-8")
    )
    return {r["name"]: r for r in results}


def _load_report(path: Path) -> dict[str, Any]:
    data: dict[str, Any] = json.loads(path.read_text(encoding="utf-8"))
    return data


def _strings(value: Any) -> Iterator[str]:
    if isinstance(value, str):
        yield value
    elif isinstance(value, dict):
        for item in value.values():
            yield from _strings(item)
    elif isinstance(value, list):
        for item in value:
            yield from _strings(item)


def _alter(db: Path, *statements: str) -> None:
    with closing(sqlite3.connect(str(db))) as conn:
        for statement in statements:
            conn.execute(statement)
        conn.commit()


# --- SqliteSource ---------------------------------------------------------


@pytest.mark.parametrize("dataset", list(SCHEMAS))
@pytest.mark.parametrize(
    ("as_of", "accounts"),
    [
        (date(2026, 10, 30), [ACCOUNT]),
        (date(2026, 10, 12), [ACCOUNT]),
        (date(2026, 9, 30), [ACCOUNT]),
        (date(2026, 8, 31), [ACCOUNT]),
        (date(2026, 10, 30), ["OTHER"]),
        (date(2026, 10, 30), []),
    ],
)
def test_sqlite_source_matches_fixture_source(
    tmp_path: Path, dataset: str, as_of: date, accounts: list[str]
) -> None:
    db = _make(tmp_path)
    expected = FixtureSource(FIXTURE).load(dataset, as_of, accounts)
    actual = SqliteSource(db).load(dataset, as_of, accounts)
    assert actual == expected
    assert all(isinstance(v, str) for row in actual for v in row.values())


def test_sqlite_source_full_fixture_nonempty(tmp_path: Path) -> None:
    db = _make(tmp_path)
    for dataset in SCHEMAS:
        rows = SqliteSource(db).load(dataset, AS_OF, [ACCOUNT])
        assert rows, dataset
        assert rows == FixtureSource(FIXTURE).load(dataset, AS_OF, [ACCOUNT])


def test_sqlite_source_insertion_order(tmp_path: Path) -> None:
    db = _make(tmp_path)
    # Insert an earlier date after the existing rows: rowid order wins.
    _alter(
        db,
        "INSERT INTO cash_flow VALUES ('2026-10-01', 'DEMO-0001', 'DEPOSIT', '1.00')",
    )
    rows = SqliteSource(db).load("cash_flow", AS_OF, [ACCOUNT])
    assert rows[-1]["date"] == "2026-10-01"
    assert len(rows) == 2


def test_sqlite_source_unknown_dataset(tmp_path: Path) -> None:
    db = _make(tmp_path)
    with pytest.raises(KeyError):
        SqliteSource(db).load("unknown", AS_OF, [ACCOUNT])


def test_sqlite_source_missing_table(tmp_path: Path) -> None:
    db = _make(tmp_path)
    _alter(db, "DROP TABLE nav_daily")
    with pytest.raises(DatasetError, match="table nav_daily not found"):
        SqliteSource(db).load("nav_daily", AS_OF, [ACCOUNT])


def test_sqlite_source_extra_column(tmp_path: Path) -> None:
    db = _make(tmp_path)
    _alter(db, "ALTER TABLE nav_daily ADD COLUMN note TEXT")
    with pytest.raises(DatasetError, match="extra fields: note"):
        SqliteSource(db).load("nav_daily", AS_OF, [ACCOUNT])


def test_sqlite_source_missing_column(tmp_path: Path) -> None:
    db = _make(tmp_path)
    _alter(
        db,
        "DROP TABLE cash_flow",
        "CREATE TABLE cash_flow (date TEXT, account_no TEXT, flow_type TEXT)",
    )
    with pytest.raises(DatasetError, match="missing fields: amount"):
        SqliteSource(db).load("cash_flow", AS_OF, [ACCOUNT])


def test_sqlite_source_non_text_value(tmp_path: Path) -> None:
    db = _make(tmp_path)
    _alter(db, "UPDATE cash_flow SET amount = NULL")
    with pytest.raises(DatasetError, match="non-text value"):
        SqliteSource(db).load("cash_flow", AS_OF, [ACCOUNT])


def test_sqlite_source_missing_file(tmp_path: Path) -> None:
    db = tmp_path / "absent.db"
    with pytest.raises(DatasetError):
        SqliteSource(db).load("nav_daily", AS_OF, [ACCOUNT])
    assert not db.exists()


def test_sqlite_source_is_read_only(tmp_path: Path) -> None:
    db = _make(tmp_path)
    before = _sha256(db)
    source = SqliteSource(db)
    for dataset in SCHEMAS:
        source.load(dataset, AS_OF, [ACCOUNT])
    assert _sha256(db) == before
    assert sorted(p.name for p in tmp_path.iterdir()) == ["private.db"]


# --- make_private_db ------------------------------------------------------


def test_make_private_db_tables_are_text(tmp_path: Path) -> None:
    db = _make(tmp_path)
    with closing(sqlite3.connect(str(db))) as conn:
        tables = sorted(
            r[0]
            for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")
        )
        assert tables == sorted(SCHEMAS)
        for dataset, specs in SCHEMAS.items():
            info = list(conn.execute(f'PRAGMA table_info("{dataset}")'))
            assert [r[1] for r in info] == [s.name for s in specs]
            assert {r[2] for r in info} == {"TEXT"}


def test_make_private_db_scale_and_replace(tmp_path: Path) -> None:
    db = _make(
        tmp_path,
        "scaled.db",
        "--scale",
        "3",
        "--account",
        PRIVATE_ACCOUNT,
        "--client-name",
        PRIVATE_CLIENT,
    )
    source = SqliteSource(db)
    assert source.load("nav_daily", AS_OF, [ACCOUNT]) == []
    info = source.load("account_info", AS_OF, [PRIVATE_ACCOUNT])
    assert [r["client_name"] for r in info] == [PRIVATE_CLIENT]
    assert info[0]["strategy"] == "Reverse Grid"
    trades = source.load("transactions", AS_OF, [PRIVATE_ACCOUNT])
    original = FixtureSource(FIXTURE).load("transactions", AS_OF, [ACCOUNT])
    assert trades[0]["price"] == "131.85"
    assert trades[0]["amount"] == "-264000.00"
    assert trades[0]["realized_pl"] == ""
    for new, old in zip(trades, original, strict=True):
        assert new["qty"] == old["qty"]
        assert new["date"] == old["date"]
    perf = source.load("performance", AS_OF, [PRIVATE_ACCOUNT])
    assert perf[0]["return_pct"] == "3.83"
    assert perf[0]["total_pl"] == "82194.00"
    holdings = source.load("holdings_daily", AS_OF, [PRIVATE_ACCOUNT])
    assert [h["volume"] for h in holdings] == ["9000", "3000"]


def test_make_private_db_scale_one_is_verbatim(tmp_path: Path) -> None:
    db = _make(tmp_path, "one.db", "--scale", "1")
    for dataset in SCHEMAS:
        rows = SqliteSource(db).load(dataset, AS_OF, [ACCOUNT])
        assert rows == FixtureSource(FIXTURE).load(dataset, AS_OF, [ACCOUNT])


@pytest.mark.parametrize(
    ("value", "factor", "expected"),
    [
        ("43.95", 3, "131.85"),
        ("-88000.00", 3, "-264000.00"),
        ("0.00", 5, "0.00"),
        ("7", 2, "14"),
        ("", 3, ""),
        ("1.5", 1, "1.5"),
    ],
)
def test_scale_value(value: str, factor: int, expected: str) -> None:
    assert scale_value(value, factor) == expected


def test_make_private_db_refuses_existing_target(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    db = tmp_path / "existing.db"
    db.write_bytes(b"keep me")
    assert make_db([str(FIXTURE), str(db)]) != 0
    assert db.read_bytes() == b"keep me"
    assert "already exists" in capsys.readouterr().err


def test_make_private_db_missing_csv_leaves_nothing(tmp_path: Path) -> None:
    csv_dir = tmp_path / "csv"
    csv_dir.mkdir()
    for path in FIXTURE.iterdir():
        if path.name != "performance.csv":
            (csv_dir / path.name).write_bytes(path.read_bytes())
    db = tmp_path / "partial.db"
    assert make_db([str(csv_dir), str(db)]) == 1
    assert not db.exists()


@pytest.mark.parametrize("scale", ["0", "-2", "1.5", "x"])
def test_make_private_db_rejects_bad_scale(tmp_path: Path, scale: str) -> None:
    db = tmp_path / "bad.db"
    with pytest.raises(SystemExit) as exc:
        make_db([str(FIXTURE), str(db), "--scale", scale])
    assert exc.value.code == 2
    assert not db.exists()


# --- private_run: expected values -----------------------------------------


def test_private_run_scale_one(tmp_path: Path) -> None:
    db = _make(tmp_path)
    digest = _sha256(db)
    out = tmp_path / "private" / "run-one"
    rc, result = _run(db, out, tmp_path / "boundary" / "result.json")
    assert rc == 0
    assert _sha256(db) == digest
    assert sorted(p.name for p in out.iterdir()) == PRIVATE_FILES

    report = _load_report(out / "report.json")
    committed = _load_report(COMMITTED / "report.json")
    assert report["header"]["report_id"] == "run-one"
    report["header"]["report_id"] = committed["header"]["report_id"]
    assert report == committed

    assert result is not None
    assert list(result) == RESULT_KEYS
    assert result["status"] == "passed"
    assert result["checks_total"] == 29
    assert result["checks_failed"] == 0
    names = [c["name"] for c in result["checks"]]
    assert names == sorted(names)
    committed_checks = json.loads((COMMITTED / "checks.json").read_text("utf-8"))
    assert result["checks"] == [{k: c[k] for k in CHECK_KEYS} for c in committed_checks]
    for check in result["checks"]:
        assert list(check) == CHECK_KEYS
    assert "boundary_leak_check" not in names

    private = _private_checks(out)
    assert len(private) == 30
    leak = private["boundary_leak_check"]
    assert leak["passed"] is True
    assert leak["layer"] == "boundary"


def test_private_run_report_id_matches_committed_name(tmp_path: Path) -> None:
    db = _make(tmp_path)
    out = tmp_path / "private" / REPORT_ID
    rc, _ = _run(db, out, tmp_path / "result.json")
    assert rc == 0
    assert (out / "report.json").read_bytes() == (
        COMMITTED / "report.json"
    ).read_bytes()


def test_private_run_scale_three(tmp_path: Path) -> None:
    db1 = _make(tmp_path)
    db3 = _make(
        tmp_path,
        "scaled.db",
        "--scale",
        "3",
        "--account",
        PRIVATE_ACCOUNT,
        "--client-name",
        PRIVATE_CLIENT,
    )
    digest = _sha256(db3)
    result1, result3 = tmp_path / "r1.json", tmp_path / "r3.json"
    assert _run(db1, tmp_path / "out1" / "x", result1)[0] == 0
    out3 = tmp_path / "out3" / "x"
    rc, result = _run(db3, out3, result3, PRIVATE_ACCOUNT)
    assert rc == 0
    assert _sha256(db3) == digest
    kpi = _load_report(out3 / "report.json")["kpi_summary"]
    assert kpi["net_asset_value"] == "2,377,194.00"
    assert kpi["total_pl"] == "82,194.00"
    assert kpi["period_return"] == "3.83%"
    assert result3.read_bytes() == result1.read_bytes()
    assert result is not None
    assert result["status"] == "passed"


@pytest.mark.parametrize(
    ("options", "account", "client"),
    [
        ((), ACCOUNT, CLIENT),
        (
            ("--scale", "3", "--account", PRIVATE_ACCOUNT, "--client-name", "PC"),
            PRIVATE_ACCOUNT,
            "PC",
        ),
    ],
)
def test_result_holds_no_private_values(
    tmp_path: Path, options: tuple[str, ...], account: str, client: str
) -> None:
    db = _make(tmp_path, "p.db", *options)
    out = tmp_path / "private" / "x"
    result = tmp_path / "result.json"
    assert _run(db, out, result, account)[0] == 0
    text = result.read_text(encoding="utf-8")
    report = _load_report(out / "report.json")
    assert account not in text
    assert client not in text
    assert str(tmp_path) not in text
    header = report["header"]
    for key in ("as_of", "opening_date", "period_start", "period_end", "period"):
        assert header[key] not in text
    figures = [
        s
        for block in ("kpi_summary", "holdings", "transactions")
        for s in _strings(report[block])
        if re.search(r"\d", s)
    ]
    assert figures
    for figure in figures:
        assert figure not in text, figure
    assert not re.search(r"\d[.,]\d", text)
    for check in json.loads(text)["checks"]:
        assert list(check) == CHECK_KEYS


# --- private_run: boundary ------------------------------------------------


def test_find_repo_root() -> None:
    assert find_repo_root() == REPO


def test_is_inside(tmp_path: Path) -> None:
    assert is_inside(REPO, REPO)
    assert is_inside(REPO / "a" / "b", REPO)
    assert not is_inside(tmp_path, REPO)
    assert not is_inside(REPO.parent / (REPO.name + "-sibling"), REPO)


def test_private_out_inside_repo(tmp_path: Path) -> None:
    db = _make(tmp_path)
    out = REPO / "private_out_must_not_exist"
    result = tmp_path / "result.json"
    rc, data = _run(db, out, result)
    assert rc == 2
    assert data is None
    assert not out.exists()
    assert not result.exists()


def test_result_inside_repo(tmp_path: Path) -> None:
    db = _make(tmp_path)
    out = tmp_path / "private" / "x"
    result = REPO / "result_must_not_exist.json"
    rc, _ = _run(db, out, result)
    assert rc == 2
    assert not result.exists()
    assert not out.exists()
    assert not (tmp_path / "private").exists()


def test_private_out_inside_repo_via_symlink(tmp_path: Path) -> None:
    link = tmp_path / "link"
    try:
        os.symlink(REPO, link, target_is_directory=True)
    except (OSError, NotImplementedError):
        pytest.skip("symlinks not available")
    db = _make(tmp_path)
    out = link / "private_out_must_not_exist"
    rc, _ = _run(db, out, tmp_path / "result.json")
    assert rc == 2
    assert not (REPO / "private_out_must_not_exist").exists()
    assert not (tmp_path / "result.json").exists()


def test_forced_leak(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    db = _make(tmp_path)
    out = tmp_path / "private" / "x"
    result = tmp_path / "result.json"
    result.write_text("stale\n", encoding="utf-8")
    original = private_run_module.render_result

    def leaky(results: Any) -> str:
        return original(results).replace('"checks_total": 29', '"total": "2,377.00"')

    monkeypatch.setattr(private_run_module, "render_result", leaky)
    rc, data = _run(db, out, result)
    assert rc == 3
    assert data is None
    assert not result.exists()
    private = _private_checks(out)
    assert private["boundary_leak_check"]["passed"] is False
    assert "figure" in private["boundary_leak_check"]["actual"]
    assert "2,377" not in private["boundary_leak_check"]["actual"]
    assert sorted(p.name for p in out.iterdir()) == ["checks.json"]


@pytest.mark.parametrize(
    ("text", "passed", "category"),
    [
        ('{"checks": []}', True, None),
        ("x DEMO-0001 x", False, "account id"),
        ("x DEMO-COOP x", False, "client name"),
        ("1.5", False, "figure"),
        ("1,000", False, "figure"),
        ('{"a": 29,\n "b": 0}', True, None),
    ],
)
def test_leak_check(text: str, passed: bool, category: str | None) -> None:
    result = leak_check(text, ACCOUNT, [CLIENT, ""])
    assert result.passed is passed
    assert result.name == "boundary_leak_check"
    if category is not None:
        assert category in result.actual
        assert ACCOUNT not in result.actual
        assert CLIENT not in result.actual


def test_leak_check_skips_empty_needles() -> None:
    assert leak_check("anything", "", [""]).passed


def test_build_result_shape() -> None:
    results = [
        CheckResult("B1", "B", False, "1.00", "2.00"),
        CheckResult("A1", "A", True, "x", "y"),
    ]
    assert build_result(results) == {
        "status": "failed",
        "checks_total": 2,
        "checks_failed": 1,
        "checks": [
            {"name": "A1", "layer": "A", "passed": True},
            {"name": "B1", "layer": "B", "passed": False},
        ],
    }


# --- private_run: failing inputs ------------------------------------------


def test_private_run_missing_table(tmp_path: Path) -> None:
    db = _make(tmp_path)
    _alter(db, "DROP TABLE holdings_daily")
    digest = _sha256(db)
    out = tmp_path / "private" / "x"
    rc, result = _run(db, out, tmp_path / "result.json")
    assert rc == 1
    assert _sha256(db) == digest
    assert result is not None
    assert result["status"] == "failed"
    assert result["checks_total"] == 29
    checks = {c["name"]: c for c in result["checks"]}
    assert checks["A3_schema_holdings_daily"]["passed"] is False
    assert checks["A3_schema_nav_daily"]["passed"] is True
    private = _private_checks(out)
    assert "not found" in private["A3_schema_holdings_daily"]["actual"]
    assert private["boundary_leak_check"]["passed"] is True
    assert sorted(p.name for p in out.iterdir()) == ["checks.json"]


def test_private_run_extra_column_fails(tmp_path: Path) -> None:
    db = _make(tmp_path)
    _alter(db, "ALTER TABLE performance ADD COLUMN note TEXT")
    rc, result = _run(db, tmp_path / "private" / "x", tmp_path / "result.json")
    assert rc == 1
    assert result is not None
    checks = {c["name"]: c for c in result["checks"]}
    assert checks["A3_schema_performance"]["passed"] is False


# --- shared logic and entry points ------------------------------------------


def test_both_commands_use_run_report(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    calls: list[str] = []
    original = returns_transactions_module.run_report

    def spy(*args: Any, **kwargs: Any) -> Any:
        calls.append(type(args[0]).__name__)
        return original(*args, **kwargs)

    monkeypatch.setattr(returns_transactions_module, "run_report", spy)
    monkeypatch.setattr(private_run_module, "run_report", spy)
    rc = returns_transactions_module.main(
        [str(FIXTURE), str(tmp_path / "fixture_out"), "--account", ACCOUNT, *DATES]
    )
    assert rc == 0
    db = _make(tmp_path)
    assert _run(db, tmp_path / "private" / "x", tmp_path / "result.json")[0] == 0
    assert calls == ["FixtureSource", "SqliteSource"]


def test_module_entrypoints(tmp_path: Path) -> None:
    db = tmp_path / "private.db"
    proc = subprocess.run(
        [
            sys.executable,
            "-m",
            "quant_software_factory.reporting.make_private_db",
            str(FIXTURE),
            str(db),
        ],
        check=False,
        capture_output=True,
        text=True,
    )
    assert proc.returncode == 0, proc.stderr
    result = tmp_path / "result.json"
    proc = subprocess.run(
        [
            sys.executable,
            "-m",
            "quant_software_factory.reporting.private_run",
            "--db",
            str(db),
            "--private-out",
            str(tmp_path / "private" / "x"),
            "--result",
            str(result),
            "--account",
            ACCOUNT,
            *DATES,
        ],
        check=False,
        capture_output=True,
        text=True,
    )
    assert proc.returncode == 0, proc.stderr
    assert proc.stdout == "29 checks, 0 failed\n"
    assert json.loads(result.read_text(encoding="utf-8"))["status"] == "passed"


@pytest.mark.parametrize(
    "module", ["sqlite_source.py", "make_private_db.py", "private_run.py"]
)
def test_no_hard_coded_private_values(module: str) -> None:
    text = (PACKAGE / module).read_text(encoding="utf-8")
    for value in (
        "DEMO-COOP",
        "DEMO-0001",
        "PRIV-0001",
        "PRIVATE-CLIENT",
        "Reverse Grid",
        "2024-02-28",
        "password",
        "localhost",
    ):
        assert value not in text
    assert not re.search(r"\d+\.\d+\.\d+\.\d+|https?://|[a-z]+://", text)
