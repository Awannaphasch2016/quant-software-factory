"""Tests for the Grid report PDF: pages 1 and 2 (#29) and 3 to 5 (#31), of #23."""

from __future__ import annotations

import json
import re
from collections.abc import Iterator
from datetime import date
from pathlib import Path
from typing import Any

import pytest
from fpdf import FPDF

from quant_software_factory.reporting import grid_performance
from quant_software_factory.reporting.grid_pdf import (
    APPROX_LABEL,
    AVG_COST_LEGEND,
    CAPTION,
    CHANGE_LABEL,
    COST_CHANGE_LABEL,
    DISCLAIMER,
    FOOTNOTE,
    INSTRUMENT_CARD_ROWS,
    MARKET_PRICE_LEGEND,
    NAV_VOLUME_LEGEND,
    NEGATIVE,
    PRICE_AXIS,
    PRICE_CHART_CAPTION,
    PRICE_CHART_TITLE,
    TEXT,
    TITLE_LINES,
    VOLUME_AXIS,
    VOLUME_CHART_CAPTION,
    VOLUME_CHART_TITLE,
    Report,
    _Writer,
    render_pdf,
)
from quant_software_factory.reporting.grid_performance import run_report
from quant_software_factory.reporting.source import FixtureSource

REPO = Path(__file__).resolve().parents[1]
FIXTURE = REPO / "data" / "fixtures" / "demo_grid_2026_11"
COMMITTED = REPO / "reports" / "demo_grid_2026_11"
DATE_RE = re.compile(r"\d{4}-\d{2}-\d{2}")
TJ_RE = re.compile(r"\((.*?)(?<!\\)\) Tj", re.S)
SECTIONS = ("Summary Performance", "Transaction", "AAA", "BBB", "CCC")
TICKERS = ("AAA", "BBB", "CCC")
TOKEN_RE = re.compile(r"/(F\d+) [\d.]+ Tf|\((.*?)(?<!\\)\) Tj", re.S)


def _obj(text: str, num: str) -> str:
    match = re.search(rf"\n{num} 0 obj\n(.*?)\nendobj", text, re.S)
    assert match is not None, num
    return match.group(1)


def _unescape(value: str) -> str:
    return re.sub(r"\\(.)", r"\1", value, flags=re.S)


def page_streams(data: bytes) -> list[str]:
    """Return the content stream of each page, in page order."""
    text = data.decode("latin-1")
    kids = re.search(r"/Kids \[([^\]]*)\]", text)
    assert kids is not None
    streams: list[str] = []
    for num in re.findall(r"(\d+) 0 R", kids.group(1)):
        contents = re.search(r"/Contents (\d+) 0 R", _obj(text, num))
        assert contents is not None
        stream = re.search(
            r"stream\n(.*?)\nendstream", _obj(text, contents.group(1)), re.S
        )
        assert stream is not None
        streams.append(stream.group(1))
    return streams


def page_texts(data: bytes) -> list[list[str]]:
    """Return the text strings of each page, read from the content streams."""
    return [[_unescape(s) for s in TJ_RE.findall(st)] for st in page_streams(data)]


def page_fonts(data: bytes) -> list[list[tuple[str, str]]]:
    """Return ``(string, BaseFont)`` for every string of each page."""
    text = data.decode("latin-1")
    names = {
        f"F{n}": _base_font(text, obj)
        for n, obj in re.findall(r"/F(\d+) (\d+) 0 R", text)
    }
    pages: list[list[tuple[str, str]]] = []
    for stream in page_streams(data):
        font = ""
        strings: list[tuple[str, str]] = []
        for match in TOKEN_RE.finditer(stream):
            if match.group(1):
                font = names[match.group(1)]
            else:
                strings.append((_unescape(match.group(2)), font))
        pages.append(strings)
    return pages


def _base_font(text: str, num: str) -> str:
    match = re.search(r"/BaseFont /(\S+)", _obj(text, num))
    assert match is not None
    return match.group(1)


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
    assert "/Count 5" in text
    assert len(page_texts(pdf)) == 5
    assert "/MediaBox [0 0 595.28 841.89]" in text
    assert len(re.findall(r"/Type /Page\b", text)) == 5
    assert not re.search(r"/MediaBox \[0 0 (?!595\.28 841\.89\])", text)
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


@pytest.mark.parametrize("index", range(5))
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
    assert SECTIONS[index] in strings
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


# --- Pages 3 to 5 (#31) -------------------------------------------------------

DrawnText = tuple[str, float, float, str, str]


def _instrument(report: Report, ticker: str) -> dict[str, Any]:
    item: dict[str, Any] = next(
        i for i in report["instruments"] if i["ticker"] == ticker
    )
    return item


def _page(pages: list[list[str]], ticker: str) -> list[str]:
    return pages[2 + TICKERS.index(ticker)]


@pytest.fixture(scope="module")
def drawn(report: Report) -> list[list[DrawnText]]:
    """``(value, x, y, style, colour)`` of every ``_Writer.text`` call, per page."""
    calls: list[list[DrawnText]] = []
    original = _Writer.text
    original_page = _Writer.page

    def page(self: _Writer, section: str) -> None:
        calls.append([])
        original_page(self, section)

    def text(
        self: _Writer,
        x: float,
        y: float,
        w: float,
        h: float,
        value: str,
        size: float,
        style: str = "",
        colour: str = TEXT,
        right: bool = False,
    ) -> None:
        calls[-1].append((value, x, y, style, colour))
        original(self, x, y, w, h, value, size, style, colour, right)

    with pytest.MonkeyPatch.context() as mp:
        mp.setattr(_Writer, "text", text)
        mp.setattr(_Writer, "page", page)
        render_pdf(report)
    return calls


@pytest.mark.parametrize(
    ("ticker", "expected"),
    [
        ("AAA", ["500,000", "0.00%", "24.80", "16.41", "-33.82%", "12,400,000"]),
        ("BBB", ["78,200", "-2.25%", "249,825", "1,800", "-24.14%", "12,840,000"]),
        ("CCC", ["180,000", "-40.00%", "-120,000", "-30.99%", "20,520,000"]),
    ],
)
def test_instrument_page_values(
    report: Report, pages: list[list[str]], ticker: str, expected: list[str]
) -> None:
    strings = _page(pages, ticker)
    item = _instrument(report, ticker)
    for value in expected:
        assert value in strings, value
    for value in item["cards"].values():
        assert value in strings, value
    assert item["initial_cost_value"] in strings
    labels = [spec[0] for row in INSTRUMENT_CARD_ROWS for spec in row]
    assert labels == [
        "Initial Units",
        "Current Units",
        "Expected Trade Units",
        "Expected Trade Return (%)",
        "Cash",
        "NAV Vol",
        "Gain Vol",
        "Initial Cost",
        "Current Cost",
    ]
    for label in (
        *labels,
        CHANGE_LABEL,
        COST_CHANGE_LABEL,
        APPROX_LABEL,
        PRICE_CHART_TITLE,
        PRICE_CHART_CAPTION,
        VOLUME_CHART_TITLE,
        VOLUME_CHART_CAPTION,
        PRICE_AXIS,
        VOLUME_AXIS,
        AVG_COST_LEGEND,
        MARKET_PRICE_LEGEND,
        NAV_VOLUME_LEGEND,
        "Transaction details",
    ):
        assert label in strings, label
    assert APPROX_LABEL == (
        "Approximately Initial Cost Value (Initial Unit \u00d7 Initial Cost)"
    )
    # Price titles both axes of chart 1, the right axis of chart 2 and the
    # price column of the transaction table.
    assert strings.count(PRICE_AXIS) == 4
    assert strings.count(MARKET_PRICE_LEGEND) == 2


@pytest.mark.parametrize(("ticker", "count"), [("AAA", 7), ("BBB", 7), ("CCC", 6)])
def test_instrument_page_transactions(
    report: Report, pages: list[list[str]], ticker: str, count: int
) -> None:
    strings = _page(pages, ticker)
    titles = ["Trade Date", "Side", "Qty", "Price", "Amount"]
    start = strings.index("Trade Date")
    assert strings[start : start + 5] == titles
    starts = [i for i, s in enumerate(strings) if DATE_RE.fullmatch(s)]
    rows = [" ".join(strings[i : i + 5]) for i in starts]
    item = _instrument(report, ticker)
    assert len(rows) == count
    assert rows == [" ".join(r.values()) for r in item["transactions"]]
    if ticker == "BBB":
        assert rows[0] == "2026-10-20 Sell 1,800 139.00 249,824.70"


@pytest.mark.parametrize("ticker", TICKERS)
def test_chart_labels(report: Report, pages: list[list[str]], ticker: str) -> None:
    strings = _page(pages, ticker)
    chart = _instrument(report, ticker)["chart"]
    labels = [x["label"] for x in chart["x_labels"]]
    assert len(labels) == 6
    assert (labels[0], labels[-1]) == ("28 Feb", "06 Nov")
    assert [s for s in strings if s in labels] == labels * 2
    axes = chart["axes"]
    for name in ("price", "nav_volume_pct", "market_price"):
        assert len(axes[name]["ticks"]) == 4
    # Ticks are drawn bottom to top, left label then right label.
    chart_one = [v for v in axes["price"]["ticks"] for _ in range(2)]
    chart_two = [
        v
        for pair in zip(
            axes["nav_volume_pct"]["ticks"], axes["market_price"]["ticks"], strict=True
        )
        for v in pair
    ]
    for ticks in (chart_one, chart_two):
        start = next(
            i for i in range(len(strings)) if strings[i : i + len(ticks)] == ticks
        )
        assert start > 0


def test_chart_series_points(report: Report, monkeypatch: pytest.MonkeyPatch) -> None:
    counts: list[int] = []
    original = FPDF.polyline

    def polyline(self: FPDF, point_list: Any, *args: Any, **kwargs: Any) -> None:
        counts.append(len(point_list))
        original(self, point_list, *args, **kwargs)

    monkeypatch.setattr(FPDF, "polyline", polyline)
    data = render_pdf(report)
    assert counts == [35] * 12
    assert data == (COMMITTED / "report.pdf").read_bytes()


@pytest.mark.parametrize("ticker", TICKERS)
def test_dashed_market_price(pdf: bytes, ticker: str) -> None:
    stream = page_streams(pdf)[2 + TICKERS.index(ticker)]
    dashes = re.findall(r"\[([^\]]*)\] [\d.]+ d", stream)
    assert len(dashes) == 2
    assert dashes[0] != ""
    assert dashes[1] == ""
    # Only the red market price line is dashed: red is set just before the
    # dash pattern, and all 35 points are drawn before the reset.
    on = re.search(r"\[[^\]]+\] [\d.]+ d\n", stream)
    off = stream.index("[] 0 d")
    assert on is not None
    assert stream[: on.start()].endswith("0.8627 0.149 0.149 RG\n")
    dashed = stream[on.end() : off]
    assert dashed.count(" m\n") == 1
    assert dashed.count(" l\n") == 34
    for page in page_streams(pdf)[:2]:
        assert not re.search(r"\] [\d.]+ d", page)


@pytest.mark.parametrize(
    ("ticker", "value", "colour"),
    [
        ("AAA", "0.00%", TEXT),
        ("AAA", "-33.82%", NEGATIVE),
        ("BBB", "-2.25%", NEGATIVE),
        ("BBB", "-24.14%", NEGATIVE),
        ("CCC", "-40.00%", NEGATIVE),
        ("CCC", "-30.99%", NEGATIVE),
    ],
)
def test_negative_sub_values_red(
    drawn: list[list[DrawnText]], ticker: str, value: str, colour: str
) -> None:
    calls = drawn[2 + TICKERS.index(ticker)]
    colours = {c[4] for c in calls if c[0] == value and c[3] == "B" and c[1] > 50}
    assert colours == {colour}


def test_card_values_bold_14(report: Report) -> None:
    sizes: dict[str, set[float]] = {}
    original = _Writer.text

    def text(
        self: _Writer,
        x: float,
        y: float,
        w: float,
        h: float,
        value: str,
        size: float,
        style: str = "",
        colour: str = TEXT,
        right: bool = False,
    ) -> None:
        sizes.setdefault(value, set()).add(size if style == "B" else -size)
        original(self, x, y, w, h, value, size, style, colour, right)

    with pytest.MonkeyPatch.context() as mp:
        mp.setattr(_Writer, "text", text)
        render_pdf(report)
    for spec in (s for row in INSTRUMENT_CARD_ROWS for s in row):
        assert -7.0 in sizes[spec[0]], spec[0]
    assert 14.0 in sizes["-120,000"]
    assert 14.0 in sizes["16.41"]


def test_bold_strings(pdf: bytes, report: Report) -> None:
    fonts = page_fonts(pdf)
    header = report["header"]
    for page in fonts:
        bold = {s for s, f in page if f == "Helvetica-Bold"}
        assert set(TITLE_LINES) <= bold
    page_one = fonts[0]
    customer = [s for s, f in page_one if f == "Helvetica-Bold"]
    for key in ("client", "account", "strategy", "inception"):
        assert header[key] in customer, key
    total_start = next(i for i, (s, _) in enumerate(page_one) if s == "Total")
    total = report["holdings_total"]
    row = page_one[total_start : total_start + 6]
    assert [s for s, _ in row] == ["Total", *list(total.values())[1:]]
    assert {f for _, f in row} == {"Helvetica-Bold"}
    # Only the Total row of the holdings table is bold.
    cash = report["holdings"][-1]["cost_value"]
    assert (cash, "Helvetica") in page_one


def test_caption_inside_allocation_panel(drawn: list[list[DrawnText]]) -> None:
    captions = [c for c in drawn[0] if c[0] == CAPTION]
    assert len(captions) == 1
    _, x, y, _, _ = captions[0]
    panel_top, panel_h = 101.0, 58.0
    donut_bottom = panel_top + 12 + 32
    assert donut_bottom < y < panel_top + panel_h - 3.5
    assert x == 14.0


def test_transaction_panel_above_footer(report: Report) -> None:
    for item in report["instruments"]:
        assert 184 + 14 + 7 * (len(item["transactions"]) + 1) < 268


def test_instrument_page_changes_with_report(report: Report) -> None:
    changed = json.loads(json.dumps(report))
    _instrument(changed, "CCC")["cards"]["cost_change_pct"] = "-12.34%"
    assert "-12.34%" in page_texts(render_pdf(changed))[4]


def test_render_error_fails_g10(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    def fail(report: Report) -> bytes:
        raise RuntimeError("draw failed")

    monkeypatch.setattr(grid_performance, "render_pdf", fail)
    out = tmp_path / "out"
    out.mkdir()
    for name in ("checks.json", "report.json", "report.pdf", "keep.txt"):
        (out / name).write_text("stale\n", encoding="utf-8")
    rc = grid_performance.main(
        [
            str(FIXTURE),
            str(out),
            "--account",
            "DEMO-0001",
            "--as-of",
            "2026-11-06",
            "--generated-at",
            "2026-11-06T18:00:00Z",
        ]
    )
    assert rc == 1
    assert sorted(p.name for p in out.iterdir()) == ["checks.json", "keep.txt"]
    checks = {
        r["name"]: r
        for r in json.loads((out / "checks.json").read_text(encoding="utf-8"))
    }
    assert checks["G10_pdf_pages"]["passed"] is False
    assert checks["G10_pdf_pages"]["actual"] == "not drawn: RuntimeError: draw failed"
    assert all(r["passed"] for n, r in checks.items() if n != "G10_pdf_pages")
