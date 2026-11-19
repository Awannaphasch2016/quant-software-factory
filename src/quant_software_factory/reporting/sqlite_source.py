"""``DataSource`` backed by a read-only SQLite database file.

The database holds one table per dataset, named exactly as the dataset, with
the fields of the schema registry stored as TEXT. It is the stand-in for a
private database in the trusted zone; see :mod:`.private_run`.
"""

from __future__ import annotations

import sqlite3
from collections.abc import Sequence
from contextlib import closing
from datetime import date
from pathlib import Path

from .schema import (
    ACCOUNT_FIELD,
    DATE_FIELD,
    PERIOD_FIELD,
    SCHEMAS,
    parse_date,
    parse_period,
)
from .source import DatasetError


def _quote(name: str) -> str:
    return '"' + name.replace('"', '""') + '"'


class SqliteSource:
    """``DataSource`` reading the table ``<dataset>`` of a SQLite file.

    The file is opened read-only for every :meth:`load` call; nothing is ever
    written to it.
    """

    def __init__(self, path: Path) -> None:
        self._path = path

    def _uri(self) -> str:
        return self._path.resolve().as_uri() + "?mode=ro"

    def load(
        self, dataset: str, as_of: date, accounts: Sequence[str]
    ) -> list[dict[str, str]]:
        """See :meth:`DataSource.load`.

        Rows are returned in insertion order (``ORDER BY rowid``) with the same
        ``as_of`` and account filtering as :class:`FixtureSource`.

        Raises:
            KeyError: ``dataset`` is not in the schema registry.
            DatasetError: The database cannot be opened, the table is missing,
                its columns differ from the registry, or a value is not text.
        """
        if dataset not in SCHEMAS:
            raise KeyError(dataset)
        fields = [spec.name for spec in SCHEMAS[dataset]]
        expected = set(fields)
        table = _quote(dataset)
        try:
            with closing(sqlite3.connect(self._uri(), uri=True)) as conn:
                found = conn.execute(
                    "SELECT 1 FROM sqlite_master WHERE type = 'table' AND name = ?",
                    (dataset,),
                ).fetchone()
                if found is None:
                    raise DatasetError(f"table {dataset} not found")
                columns = [
                    str(row[1]) for row in conn.execute(f"PRAGMA table_info({table})")
                ]
                header = set(columns)
                if header != expected or len(header) != len(columns):
                    parts = []
                    if missing := sorted(expected - header):
                        parts.append(f"missing fields: {', '.join(missing)}")
                    if extra := sorted(header - expected):
                        parts.append(f"extra fields: {', '.join(extra)}")
                    if not parts:
                        parts.append("duplicate field names")
                    raise DatasetError(f"table {dataset} " + "; ".join(parts))
                select = ", ".join(_quote(name) for name in fields)
                raw = conn.execute(
                    f"SELECT {select} FROM {table} ORDER BY rowid"
                ).fetchall()
        except sqlite3.Error as exc:
            raise DatasetError(f"table {dataset} cannot be read: {exc}") from exc

        wanted = set(accounts)
        as_of_month = (as_of.year, as_of.month)
        rows: list[dict[str, str]] = []
        for index, values in enumerate(raw, start=1):
            if not all(isinstance(value, str) for value in values):
                raise DatasetError(f"table {dataset} row {index} has a non-text value")
            row = dict(zip(fields, values, strict=True))
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
            rows.append(row)
        return rows
