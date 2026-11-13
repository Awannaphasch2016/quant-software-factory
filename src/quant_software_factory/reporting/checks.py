"""Layer A data checks: freshness (A1), completeness (A2) and schema (A3).

All data is read through :meth:`DataSource.load`; this module never opens files.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from datetime import date

from .schema import (
    DATE_FIELD,
    PERIOD_FIELD,
    SCHEMAS,
    parse_date,
    parse_period,
    validate_rows,
)
from .source import DatasetError, DataSource

LAYER = "A"
VALID = "valid"

Rows = list[dict[str, str]]


@dataclass(frozen=True)
class CheckResult:
    """Outcome of one data check."""

    name: str
    layer: str
    passed: bool
    expected: str
    actual: str

    def to_dict(self) -> dict[str, str | bool]:
        """Return the result as a dict with a fixed key order."""
        return {
            "name": self.name,
            "layer": self.layer,
            "passed": self.passed,
            "expected": self.expected,
            "actual": self.actual,
        }


def _schema_check(
    source: DataSource, dataset: str, account: str, as_of: date
) -> tuple[CheckResult, Rows | None]:
    name = f"A3_schema_{dataset}"
    try:
        rows = source.load(dataset, as_of, [account])
    except DatasetError as exc:
        return CheckResult(name, LAYER, False, VALID, str(exc)), None
    errors = validate_rows(dataset, rows)
    if errors:
        return CheckResult(name, LAYER, False, VALID, "; ".join(errors)), None
    return CheckResult(name, LAYER, True, VALID, VALID), rows


def _row_count(rows: Rows) -> tuple[bool, str]:
    return len(rows) >= 1, f"{len(rows)} row(s)"


def _has_date(day: date) -> Callable[[Rows], tuple[bool, str]]:
    def check(rows: Rows) -> tuple[bool, str]:
        found = any(parse_date(r[DATE_FIELD]) == day for r in rows)
        return found, "present" if found else "absent"

    return check


def run_checks(
    source: DataSource, account: str, opening: date, as_of: date
) -> list[CheckResult]:
    """Run all Layer A checks for one account.

    Args:
        source: Data source to read through.
        account: Account number.
        opening: Report opening date.
        as_of: Report as-of date.

    Returns:
        Check results sorted by name. A1/A2 checks whose dataset failed A3 are
        reported as not run (``passed`` false, reason in ``actual``).
    """
    results: list[CheckResult] = []
    loaded: dict[str, Rows] = {}
    for dataset in SCHEMAS:
        result, rows = _schema_check(source, dataset, account, as_of)
        results.append(result)
        if rows is not None:
            loaded[dataset] = rows

    def freshness(rows: Rows) -> tuple[bool, str]:
        dates = [d for d in (parse_date(r[DATE_FIELD]) for r in rows) if d]
        if not dates:
            return False, "no rows"
        latest = max(dates)
        return latest == as_of, latest.isoformat()

    month = (as_of.year, as_of.month)
    month_text = f"{as_of.year:04d}-{as_of.month:02d}"

    def as_of_month(rows: Rows) -> tuple[bool, str]:
        found = any(parse_period(r[PERIOD_FIELD]) == month for r in rows)
        return found, "present" if found else "absent"

    dependent: list[tuple[str, str, str, Callable[[Rows], tuple[bool, str]]]] = [
        ("A1_freshness_nav_daily", "nav_daily", as_of.isoformat(), freshness),
        ("A2_account_info_has_rows", "account_info", ">= 1 row", _row_count),
        ("A2_holdings_daily_has_rows", "holdings_daily", ">= 1 row", _row_count),
        (
            "A2_nav_daily_as_of_date",
            "nav_daily",
            f"row dated {as_of.isoformat()}",
            _has_date(as_of),
        ),
        ("A2_nav_daily_has_rows", "nav_daily", ">= 1 row", _row_count),
        (
            "A2_nav_daily_opening_date",
            "nav_daily",
            f"row dated {opening.isoformat()}",
            _has_date(opening),
        ),
        (
            "A2_performance_as_of_month",
            "performance",
            f"row for period {month_text}",
            as_of_month,
        ),
        ("A2_performance_has_rows", "performance", ">= 1 row", _row_count),
    ]
    for name, dataset, expected, check in dependent:
        if dataset not in loaded:
            actual = f"not run: A3_schema_{dataset} failed"
            results.append(CheckResult(name, LAYER, False, expected, actual))
            continue
        passed, actual = check(loaded[dataset])
        results.append(CheckResult(name, LAYER, passed, expected, actual))
    return sorted(results, key=lambda r: r.name)
