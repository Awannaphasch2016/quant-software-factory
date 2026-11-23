"""Tests for the Grid report PDF, pages 1 and 2 (#29, part 3 of #23)."""

from __future__ import annotations

import json
import re
from collections.abc import Iterator
from datetime import date
from pathlib import Path
from typing import Any

import pytest

from quant_software_factory.reporting import grid_performance
from quant_software_factory.reporting.grid_pdf import (
    CAPTION,
    DISCLAIMER,
    FOOTNOTE,
    Report,
    render_pdf,
)
from quant_software_factory.reporting.grid_performance import run_report
from quant_software_factory.reporting.source import FixtureSource

REPO = Path(__file__).resolve().parents[1]
FIXTURE = REPO / "data" / "fixtures" / "demo_grid_2026_11"
COMMITTED = REPO / "reports" / "demo_grid_2026_11"
DATE_RE = re.compile(r"\d{4}-\d{2}-\d{2}")
TJ_RE = re.compile(r"\((.*?)(?<!\\)\) Tj", re.S)


def _obj(text: str, num: str) -> str:
    match = re.search(rf"\n{num} 0 obj\n(.*?)\nendobj", text, re.S)
    assert match is not None, num
    return match.group(1)


def page_texts(data: bytes) -> list[list[str]]:
    """Return the text strings of each page, read from the content streams."""
    text = data.decode("latin-1")
    kids = re.search(r"/Kids \[([^\]]*)\]", text)
    assert kids is not None
    pages: list[list[str]] = []
    for num in re.findall(r"(\d+) 0 R", kids.group(1)):
        contents = re.search(r"/Contents (\d+) 0 R", _obj(text, num))
        assert contents is not None
        stream = re.search(
            r"stream\n(.*?)\nendstream", _obj(text, contents.group(1)), re.S
        )
        assert stream is not None
        strings = TJ_RE.findall(stream.group(1))
        pages.append([re.sub(r"\\(.)", r"\1", s, flags=re.S) for s in strings])
    return pages


def _leaves(value: Any) -> Iterator[str]:
    if isinstance(value, dict):
        for item in value.values():
            yield from _leaves(item)
    elif isinstance(value, list):
        for item in value:
            yield from _leaves(item)
    else:
        assert isinstance(value, str)
        yield value


@pytest.fixture(scope="module")
def report() -> Report:
    data: Report = json.loads((COMMITTED / "report.json").read_text(encoding="utf-8"))
    return data


@pytest.fixture(scope="module")
def pdf(report: Report) -> bytes:
    return render_pdf(report)


@pytest.fixture(scope="module")
def pages(pdf: bytes) -> list[list[str]]:
    return page_texts(pdf)


def test_document_structure(pdf: bytes) -> None:
    text = pdf.decode("latin-1")
    assert pdf.startswith(b"%PDF-")
    assert "/Count 2" in text
    assert len(page_texts(pdf)) == 2
    assert "/MediaBox [0 0 595.28 841.89]" in text
    assert "/Filter" not in text
    assert "/CreationDate (D:20261106180000Z)" in text
    assert "/Producer" not in text
    assert set(re.findall(r"/BaseFont /(\S+)", text)) == {
        "Helvetica",
        "Helvetica-Bold",
    }
    assert "/FontFile" not in text


def test_deterministic_and_matches_committed(report: Report, pdf: bytes) -> None:
    assert render_pdf(report) == pdf
    assert (COMMITTED / "report.pdf").read_bytes() == pdf


def test_latin1_only(pages: list[list[str]]) -> None:
    for strings in pages:
        for s in strings:
            assert "\u2212" not in s
            s.encode("latin-1")


@pytest.mark.parametrize("index", [0, 1])
def test_frame_on_every_page(
    report: Report, pages: list[list[str]], index: int
) -> None:
    header = report["header"]
    strings = pages[index]
    for expected in (
        "REVERSE GRID TRADING",
        "Reverse Grid Trading",
        "Performance",
        f"{header['client']} \u00b7 {header['account']}",
        header["as_of_label"],
        f"Request: {header['request_id']}    Generated: {header['generated_at']}",
    ):
        assert expected in strings
    assert ("Summary Performance", "Transaction")[index] in strings
    disclaimer = " ".join(s for s in strings if "Disclaimer" in s or "unreal" in s)
    assert disclaimer == DISCLAIMER


def test_page_one_values(report: Report, pages: list[list[str]]) -> None:
    strings = pages[0]
    for expected in (
        "28,360,975",
        "249,825",
        "830,000",
        "0.9%",
        "BBB 38.1%",
        "26,473,509.22",
        "28,360,974.70",
        "-120,000",
        "Customer",
        "Client name",
        "Account no.",
        "Strategy",
        "Inception",
        "Reverse Grid (GT)",
        "28 Feb 2024",
        "Net Asset Value",
        "As of report date",
        "Cash on Hand",
        "Dividend (YTD)",
        "Cash on Hand %",
        "Port Allocation",
        CAPTION,
        "Total",
        FOOTNOTE,
    ):
        assert expected in strings, expected
    legend = [s for s in strings if re.fullmatch(r"[A-Z]+ \d+\.\d%", s)]
    assert legend == [f"{a['label']} {a['weight']}" for a in report["allocation"]]
    assert strings.count("Summary Performance") == 2
    for row in report["holdings"]:
        for value in row.values():
            assert value in strings
    for row in report["summary"]:
        for value in row.values():
            assert value in strings


def test_page_two_rows(report: Report, pages: list[list[str]]) -> None:
    strings = pages[1]
    assert "Transaction details" in strings
    for title in ("Trade Date", "Ticker", "Side", "Qty", "Price", "Amount"):
        assert title in strings
    starts = [i for i, s in enumerate(strings) if DATE_RE.fullmatch(s)]
    assert len(starts) == 25
    rows = [" ".join(strings[i : i + 6]) for i in starts]
    assert rows[0] == "2026-10-20 BBB Sell 1,800 139.00 249,824.70"
    assert rows == [" ".join(r.values()) for r in report["transactions"]]
    assert "Port Adjusted" in strings
    assert "Gain Adjustment" in strings


def test_numbers_come_from_report(report: Report, pages: list[list[str]]) -> None:
    header = report["header"]
    allowed = set(_leaves(report))
    allowed |= {f"{a['label']} {a['weight']}" for a in report["allocation"]}
    allowed |= {
        f"{header['client']} \u00b7 {header['account']}",
        f"Request: {header['request_id']}    Generated: {header['generated_at']}",
        FOOTNOTE,
    }
    for strings in pages:
        for s in strings:
            if re.search(r"\d", s):
                assert s in allowed, s


def test_changed_report_changes_pdf(report: Report) -> None:
    changed = json.loads(json.dumps(report))
    changed["cards"]["nav"] = "1,234"
    assert "1,234" in page_texts(render_pdf(changed))[0]


def test_render_error_writes_nothing(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    def fail(report: Report) -> bytes:
        raise RuntimeError("draw failed")

    run = run_report(
        FixtureSource(FIXTURE),
        "DEMO-0001",
        date(2026, 11, 6),
        "2026-11-06T18:00:00Z",
    )
    monkeypatch.setattr(grid_performance, "render_pdf", fail)
    out = tmp_path / "out"
    with pytest.raises(RuntimeError):
        grid_performance.write_outputs(out, run.results, run.report)
    assert not out.exists()
