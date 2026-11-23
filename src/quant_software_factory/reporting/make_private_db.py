"""Build a private SQLite database from dataset CSV files.

Usage::

    python -m quant_software_factory.reporting.make_private_db <csv_dir> <db_path> \\
        [--scale K] [--account NEW_ID] [--client-name NAME]

Reads ``<csv_dir>/<dataset>.csv`` for every dataset in ``RETURNS_DATASETS`` and
writes one TEXT table per dataset to ``<db_path>``, which must not exist yet.
``--scale K`` multiplies every ``decimal`` field by ``K`` except
``performance.return_pct``, keeping the number of decimal places; quantities,
dates and percentages are unchanged. ``--account`` replaces ``account_no`` in
every table and ``--client-name`` replaces ``account_info.client_name``.

This builds the synthetic stand-in for a private database used by
:mod:`.private_run`. Exits 0 on success and 1 on any error, in which case no
database file is left behind.
"""

from __future__ import annotations

import argparse
import csv
import sqlite3
import sys
from collections.abc import Sequence
from contextlib import closing
from decimal import Inexact, localcontext
from pathlib import Path

from .schema import ACCOUNT_FIELD, RETURNS_DATASETS, SCHEMAS, parse_decimal

CLIENT_FIELD = "client_name"
UNSCALED = frozenset({("performance", "return_pct")})

Rows = list[dict[str, str]]


class BuildError(Exception):
    """The input files cannot be turned into a private database."""


def _quote(name: str) -> str:
    return '"' + name.replace('"', '""') + '"'


def read_csv(csv_dir: Path, dataset: str) -> Rows:
    """Read ``<csv_dir>/<dataset>.csv`` and check its header against the registry.

    Raises:
        BuildError: The file is missing, its header differs from the registry,
            or a row has the wrong number of values.
    """
    path = csv_dir / f"{dataset}.csv"
    if not path.is_file():
        raise BuildError(f"{path.name} not found")
    expected = [spec.name for spec in SCHEMAS[dataset]]
    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None or sorted(reader.fieldnames) != sorted(expected):
            raise BuildError(f"{path.name} header does not match the schema")
        rows: Rows = []
        for index, row in enumerate(reader, start=1):
            if None in row or None in row.values():
                raise BuildError(f"{path.name} row {index} has the wrong value count")
            rows.append(dict(row))
    return rows


def scale_value(value: str, factor: int) -> str:
    """Multiply a plain decimal string by ``factor``, keeping its decimal places.

    A blank value stays blank.

    Raises:
        BuildError: ``value`` is not a plain decimal.
    """
    if value == "":
        return value
    number = parse_decimal(value)
    if number is None:
        raise BuildError(f"not a decimal: {value!r}")
    with localcontext() as ctx:
        ctx.prec = 60
        ctx.traps[Inexact] = True
        return format(number * factor, "f")


def transform(
    dataset: str,
    rows: Rows,
    scale: int,
    account: str | None,
    client_name: str | None,
) -> Rows:
    """Apply the scale factor and the account and client name replacements."""
    scaled = [
        spec.name
        for spec in SCHEMAS[dataset]
        if spec.kind == "decimal" and (dataset, spec.name) not in UNSCALED
    ]
    out: Rows = []
    for row in rows:
        new = dict(row)
        if scale != 1:
            for name in scaled:
                new[name] = scale_value(new[name], scale)
        if account is not None:
            new[ACCOUNT_FIELD] = account
        if client_name is not None and CLIENT_FIELD in new:
            new[CLIENT_FIELD] = client_name
        out.append(new)
    return out


def write_db(db_path: Path, data: dict[str, Rows]) -> None:
    """Create ``db_path`` with one TEXT table per dataset and insert the rows.

    Raises:
        FileExistsError: ``db_path`` already exists; it is left untouched.
    """
    db_path.open("xb").close()
    try:
        with closing(sqlite3.connect(str(db_path))) as conn:
            for dataset, rows in data.items():
                fields = [spec.name for spec in SCHEMAS[dataset]]
                columns = ", ".join(f"{_quote(name)} TEXT" for name in fields)
                conn.execute(f"CREATE TABLE {_quote(dataset)} ({columns})")
                marks = ", ".join("?" for _ in fields)
                names = ", ".join(_quote(name) for name in fields)
                conn.executemany(
                    f"INSERT INTO {_quote(dataset)} ({names}) VALUES ({marks})",
                    [tuple(row[name] for name in fields) for row in rows],
                )
            conn.commit()
    except BaseException:
        db_path.unlink(missing_ok=True)
        raise


def _positive_int(value: str) -> int:
    try:
        number = int(value)
    except ValueError:
        raise argparse.ArgumentTypeError(f"not an integer: {value!r}") from None
    if number < 1:
        raise argparse.ArgumentTypeError(f"must be at least 1: {value!r}")
    return number


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="python -m quant_software_factory.reporting.make_private_db",
        description="Build a SQLite database from dataset CSV files.",
    )
    parser.add_argument("csv_dir", type=Path, help="directory holding <dataset>.csv")
    parser.add_argument("db_path", type=Path, help="database file to create")
    parser.add_argument("--scale", type=_positive_int, default=1)
    parser.add_argument("--account", help="replace account_no in every table")
    parser.add_argument(
        "--client-name", dest="client_name", help="replace account_info.client_name"
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """Build the database.

    Args:
        argv: Command line arguments; defaults to ``sys.argv[1:]``.

    Returns:
        0 on success, 1 on any error (nothing is written).
    """
    args = _parser().parse_args(argv)
    db_path: Path = args.db_path
    if db_path.exists() or db_path.is_symlink():
        print(f"error: {db_path} already exists; not overwriting", file=sys.stderr)
        return 1
    try:
        data = {
            dataset: transform(
                dataset,
                read_csv(args.csv_dir, dataset),
                args.scale,
                args.account,
                args.client_name,
            )
            for dataset in RETURNS_DATASETS
        }
        write_db(db_path, data)
    except FileExistsError:
        print(f"error: {db_path} already exists; not overwriting", file=sys.stderr)
        return 1
    except (BuildError, OSError, sqlite3.Error) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    print(f"wrote {len(data)} tables to {db_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
