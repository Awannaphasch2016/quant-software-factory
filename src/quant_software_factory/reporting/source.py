"""Data access interface for report datasets and its fixture implementation."""

from __future__ import annotations

import csv
from collections.abc import Sequence
from datetime import date
from pathlib import Path
from typing import Protocol

from .schema import (
    ACCOUNT_FIELD,
    DATE_FIELD,
    PERIOD_FIELD,
    SCHEMAS,
    parse_date,
    parse_period,
)


class DatasetError(Exception):
    """A known dataset cannot be read in its declared shape."""


class DataSource(Protocol):
    """Read-only access to precomputed report datasets."""

    def load(
        self, dataset: str, as_of: date, accounts: Sequence[str]
    ) -> list[dict[str, str]]:
        """Return the raw string values of each row for the given accounts.

        Rows of datasets with a ``date`` field are limited to ``date <= as_of``;
        ``performance`` rows to periods not after the as-of month;
        ``account_info`` returns all rows for the accounts.

        Raises:
            KeyError: ``dataset`` is not in the schema registry.
            DatasetError: The dataset is missing, has no header, has fields
                other than the registered ones, or has a malformed row.
        """
        ...


class FixtureSource:
    """``DataSource`` backed by ``<root>/<dataset>.csv`` files."""

    def __init__(self, root: Path) -> None:
        self._root = root

    def load(
        self, dataset: str, as_of: date, accounts: Sequence[str]
    ) -> list[dict[str, str]]:
        """See :meth:`DataSource.load`."""
        if dataset not in SCHEMAS:
            raise KeyError(dataset)
        file_name = f"{dataset}.csv"
        path = self._root / file_name
        if not path.is_file():
            raise DatasetError(f"{file_name} not found")
        expected = {spec.name for spec in SCHEMAS[dataset]}
        wanted = set(accounts)
        as_of_month = (as_of.year, as_of.month)
        rows: list[dict[str, str]] = []
        with path.open(encoding="utf-8", newline="") as handle:
            reader = csv.DictReader(handle)
            if reader.fieldnames is None:
                raise DatasetError(f"{file_name} is empty (no header)")
            header = set(reader.fieldnames)
            if header != expected or len(header) != len(reader.fieldnames):
                parts = []
                if missing := sorted(expected - header):
                    parts.append(f"missing fields: {', '.join(missing)}")
                if extra := sorted(header - expected):
                    parts.append(f"extra fields: {', '.join(extra)}")
                if not parts:
                    parts.append("duplicate field names")
                raise DatasetError(f"{file_name} " + "; ".join(parts))
            for index, row in enumerate(reader, start=1):
                if None in row or None in row.values():
                    raise DatasetError(
                        f"{file_name} row {index} does not have {len(expected)} values"
                    )
                if row[ACCOUNT_FIELD] not in wanted:
                    continue
                if DATE_FIELD in expected:
                    day = parse_date(row[DATE_FIELD])
                    if day is not None and day > as_of:
                        continue
                elif PERIOD_FIELD in expected:
                    period = parse_period(row[PERIOD_FIELD])
                    if period is not None and period > as_of_month:
                        continue
                rows.append(dict(row))
        return rows
