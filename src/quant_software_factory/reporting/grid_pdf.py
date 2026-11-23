"""Draw the Grid Trade Performance PDF from a built ``report.json``.

Page 1 is Summary Performance, page 2 is Transaction and pages 3 onwards show
one instrument each, in the order of ``report.json.instruments`` (#23). The
drawing code computes no figures: every number printed is a string taken as is
from ``report.json``. Only positions are derived from numbers: the donut chart
from the ``allocation[].weight_raw`` values and the line charts from the
``chart`` series and the ``chart.axes`` scale bounds.

The output is deterministic: content streams are uncompressed, the core
Helvetica font is used (no embedded font) and the PDF creation date is taken
from ``header.generated_at``. Text uses only Latin-1 characters.
"""

from __future__ import annotations

from collections.abc import Iterable, Sequence
from datetime import datetime, timezone
from typing import Any

from fpdf import FPDF

Report = dict[str, Any]

FONT = "Helvetica"
TEXT = "#111827"
SECONDARY = "#6B7280"
BORDER = "#E5E7EB"
NAVY = "#1E3A8A"
LABEL_BLUE = "#1D4ED8"
GREEN = "#15803D"
WHITE = "#FFFFFF"
NEGATIVE = "#DC2626"
CHART_BLUE = "#2563EB"
GRID_LINE = 0.1
SERIES_LINE = 0.4
DASH = (1.5, 1.0)
SLICE_COLOURS = ("#1E3A8A", "#D97706", "#15803D", "#7C3AED")

MARGIN = 10.0
PAGE_W = 210.0
CONTENT_W = PAGE_W - 2 * MARGIN
RIGHT = PAGE_W - MARGIN
RADIUS = 3.0
PAD = 4.0
THIN = 0.2

TITLE_LINES = ("Reverse Grid Trading", "Performance")
KICKER = "REVERSE GRID TRADING"
DISCLAIMER = (
    "Disclaimer: This report is prepared for the named account holder only. "
    "It is not an offer, solicitation, or investment advice. Past performance "
    "does not indicate future results. Automated program trading carries risks "
    "from price volatility, market liquidity and falling prices, which may lead "
    "to unrealized losses."
)
FOOTNOTE = (
    "* Expected volume is an initial estimate derived from the formula: "
    "Cash/(Market Price \u00d7(1+Commission fee))"
)
CAPTION = "Pie chart by market value."
TOTAL_LABEL = "Total"

APPROX_LABEL = "Approximately Initial Cost Value (Initial Unit \u00d7 Initial Cost)"
PRICE_CHART_TITLE = "Average Cost vs. Market Price"
PRICE_CHART_CAPTION = "Average Cost and Market Price over time."
VOLUME_CHART_TITLE = "NAV (Volume %) vs. Market Price"
VOLUME_CHART_CAPTION = "NAV volume % and Market Price."
PRICE_AXIS = "Price"
VOLUME_AXIS = "Vol %"
AVG_COST_LEGEND = "Average Cost"
MARKET_PRICE_LEGEND = "Market Price"
NAV_VOLUME_LEGEND = "NAV Volume %"
CHANGE_LABEL = "Change %"
COST_CHANGE_LABEL = "Cost Change %"

# Instrument cards: (label, card key, sub-label, sub-label card key).
CardSpec = tuple[str, str, str, str]
INSTRUMENT_CARD_ROWS: tuple[tuple[CardSpec, ...], ...] = (
    (
        ("Initial Units", "initial_units", "", ""),
        ("Current Units", "current_units", CHANGE_LABEL, "current_units_change_pct"),
        ("Expected Trade Units", "expected_trade_units", "", ""),
        ("Expected Trade Return (%)", "expected_trade_return_pct", "", ""),
        ("Cash", "cash", "", ""),
    ),
    (
        ("NAV Vol", "nav_volume", "", ""),
        ("Gain Vol", "gain_volume", "", ""),
        ("Initial Cost", "initial_cost", "", ""),
        ("Current Cost", "current_cost", COST_CHANGE_LABEL, "cost_change_pct"),
    ),
)

_GENERATED_AT_FORMAT = "%Y-%m-%dT%H:%M:%SZ"

# Column spec: (header, report key, width in mm, right aligned).
Column = tuple[str, str, float, bool]

HOLDINGS_COLUMNS: tuple[Column, ...] = (
    ("Ticker", "ticker", 16.0, False),
    ("Volume", "volume", 18.0, True),
    ("Cost Value", "cost_value", 25.0, True),
    ("Avg Cost", "avg_cost", 16.0, True),
    ("Market Price", "market_price", 20.0, True),
    ("Market Value", "market_value", 25.0, True),
)
SUMMARY_COLUMNS: tuple[Column, ...] = (
    ("Ticker", "ticker", 15.0, False),
    ("Avg Cost", "avg_cost", 18.0, True),
    ("Market Price", "market_price", 20.0, True),
    ("Initial Units", "initial_units", 20.0, True),
    ("Current Units", "current_units", 21.0, True),
    ("Cash", "cash", 24.0, True),
    ("Expected Volume", "expected_volume", 24.0, True),
    ("NAV Volume", "nav_volume", 20.0, True),
    ("Gain Volume", "gain_volume", 20.0, True),
)
TRANSACTION_COLUMNS: tuple[Column, ...] = (
    ("Trade Date", "trade_date", 30.0, False),
    ("Ticker", "ticker", 22.0, False),
    ("Side", "side", 40.0, False),
    ("Qty", "qty", 28.0, True),
    ("Price", "price", 28.0, True),
    ("Amount", "amount", 34.0, True),
)
INSTRUMENT_TRANSACTION_COLUMNS: tuple[Column, ...] = (
    ("Trade Date", "trade_date", 34.0, False),
    ("Side", "side", 40.0, False),
    ("Qty", "qty", 34.0, True),
    ("Price", "price", 34.0, True),
    ("Amount", "amount", 40.0, True),
)

# One plotted line: (values, colour, dashed).
Series = tuple[Sequence[str], str, bool]


def _sign_colour(value: str) -> str:
    """Red for a value printed with a leading minus sign, else the text colour."""
    return NEGATIVE if value.startswith("-") else TEXT


def _creation_date(generated_at: str) -> datetime:
    """Parse ``YYYY-MM-DDTHH:MM:SSZ`` as an aware UTC datetime."""
    parsed = datetime.strptime(generated_at, _GENERATED_AT_FORMAT)
    return parsed.replace(tzinfo=timezone.utc)


class _Writer:
    """Draws the report pages on one :class:`FPDF` document."""

    def __init__(self, report: Report) -> None:
        self.report = report
        self.header: dict[str, str] = report["header"]
        pdf = FPDF(orientation="P", unit="mm", format="A4")
        pdf.set_compression(False)
        pdf.set_margins(MARGIN, MARGIN, MARGIN)
        pdf.set_auto_page_break(False)
        pdf.set_creation_date(_creation_date(self.header["generated_at"]))
        self.pdf = pdf

    # --- Primitives ---------------------------------------------------------

    def text(
        self,
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
        """Print ``value`` in one cell, left or right aligned."""
        pdf = self.pdf
        pdf.set_font(FONT, style, size)
        pdf.set_text_color(colour)
        pdf.set_xy(x, y)
        pdf.cell(w, h, value, align="R" if right else "L")

    def width(self, value: str, size: float, style: str = "") -> float:
        """Width of ``value`` in mm at the given font size and style."""
        self.pdf.set_font(FONT, style, size)
        return float(self.pdf.get_string_width(value))

    def square(self, x: float, y: float, colour: str) -> None:
        """Small filled legend square."""
        self.pdf.set_fill_color(colour)
        self.pdf.rect(x, y, 2.5, 2.5, style="F")

    def panel(self, x: float, y: float, w: float, h: float) -> None:
        """White panel with a thin rounded border."""
        pdf = self.pdf
        pdf.set_line_width(THIN)
        pdf.set_draw_color(BORDER)
        pdf.set_fill_color(WHITE)
        pdf.rect(x, y, w, h, style="DF", round_corners=True, corner_radius=RADIUS)

    def hline(
        self, x1: float, x2: float, y: float, width: float = THIN, colour: str = BORDER
    ) -> None:
        pdf = self.pdf
        pdf.set_line_width(width)
        pdf.set_draw_color(colour)
        pdf.line(x1, y, x2, y)

    def table(
        self,
        x: float,
        y: float,
        columns: Sequence[Column],
        rows: Sequence[dict[str, str]],
        row_h: float,
        size: float = 8.0,
        bold_last: bool = False,
    ) -> float:
        """Draw a table; return the y below its last row.

        The header row is printed in the secondary colour; a thin separator
        follows the header and every row. Each value is one cell.
        """
        width = sum(c[2] for c in columns)
        cx = x
        for title, _, w, right in columns:
            self.text(cx, y, w, row_h, title, size - 1, "B", SECONDARY, right)
            cx += w
        y += row_h
        self.hline(x, x + width, y)
        for index, row in enumerate(rows):
            style = "B" if bold_last and index == len(rows) - 1 else ""
            cx = x
            for _, key, w, right in columns:
                self.text(cx, y, w, row_h, row[key], size, style, TEXT, right)
                cx += w
            y += row_h
            if index < len(rows) - 1:
                self.hline(x, x + width, y)
        return y

    # --- Shared frame -------------------------------------------------------

    def page(self, section: str) -> None:
        """Start a page with the header panel, section title and footer."""
        pdf = self.pdf
        pdf.add_page()
        header = self.header

        self.panel(MARGIN, MARGIN, CONTENT_W, 32)
        left = MARGIN + 5
        self.text(left, 14, 100, 3, KICKER, 7, "B", LABEL_BLUE)
        self.text(left, 18, 120, 8, TITLE_LINES[0], 20, "B")
        self.text(left, 26, 120, 8, TITLE_LINES[1], 20, "B")
        subtitle = f"{header['client']} \u00b7 {header['account']}"
        self.text(left, 35, 120, 4, subtitle, 9, "", SECONDARY)
        self.text(RIGHT - 75, 14, 70, 4, header["as_of_label"], 8, "", SECONDARY, True)

        self.text(MARGIN, 45, CONTENT_W, 6, section, 12, "B")
        self.hline(MARGIN, RIGHT, 52, 0.6, NAVY)

        self.hline(MARGIN, RIGHT, 268)
        pdf.set_font(FONT, "", 6)
        pdf.set_text_color(SECONDARY)
        pdf.set_xy(MARGIN, 270)
        pdf.multi_cell(CONTENT_W, 2.8, DISCLAIMER, align="L")
        request = (
            f"Request: {header['request_id']}    Generated: {header['generated_at']}"
        )
        self.text(MARGIN, 280, CONTENT_W, 4, request, 7, "", SECONDARY)

    # --- Page 1 -------------------------------------------------------------

    def customer(self, x: float, y: float, w: float, h: float) -> None:
        header = self.header
        self.panel(x, y, w, h)
        self.text(x + PAD, y + 3, w - 2 * PAD, 5, "Customer", 9, "B")
        pairs = (
            ("Client name", header["client"]),
            ("Account no.", header["account"]),
            ("Strategy", header["strategy"]),
            ("Inception", header["inception"]),
        )
        row_y = y + 11
        for label, value in pairs:
            self.text(x + PAD, row_y, 26, 5, label, 7, "", SECONDARY)
            self.text(x + PAD + 26, row_y, w - 2 * PAD - 26, 5, value, 8, "B")
            self.hline(x + PAD, x + w - PAD, row_y + 6)
            row_y += 7

    def card(
        self,
        x: float,
        y: float,
        w: float,
        h: float,
        label: str,
        value: str,
        colour: str = TEXT,
        sub_label: str = "",
    ) -> None:
        self.panel(x, y, w, h)
        self.text(x + PAD, y + 2.5, w - 2 * PAD, 4, label, 8, "", SECONDARY)
        self.text(x + PAD, y + 7, w - 2 * PAD, 7, value, 15, "B", colour)
        if sub_label:
            self.text(x + PAD, y + 14, w - 2 * PAD, 3, sub_label, 6.5, "", SECONDARY)

    def cards(self, x: float, y: float, w: float) -> None:
        cards = self.report["cards"]
        gap = 4.0
        card_w = (w - gap) / 2
        card_h = 18.0
        x2 = x + card_w + gap
        y2 = y + card_h + gap
        nav_sub = "As of report date"
        self.card(x, y, card_w, card_h, "Net Asset Value", cards["nav"], TEXT, nav_sub)
        self.card(x2, y, card_w, card_h, "Cash on Hand", cards["cash_on_hand"])
        self.card(x, y2, card_w, card_h, "Dividend (YTD)", cards["dividend_ytd"], GREEN)
        self.card(x2, y2, card_w, card_h, "Cash on Hand %", cards["cash_pct"])

    def donut(self, x: float, y: float, diameter: float) -> dict[str, str]:
        """Draw the allocation donut; return the slice colour of each label.

        Slices follow the holdings order (CASH last), start at 12 o'clock and
        run clockwise; each angle is its ``weight_raw`` share of the total.
        """
        pdf = self.pdf
        raw = {a["label"]: float(a["weight_raw"]) for a in self.report["allocation"]}
        labels = [h["ticker"] for h in self.report["holdings"] if h["ticker"] in raw]
        total = sum(raw[label] for label in labels)
        colours: dict[str, str] = {}
        start = -90.0
        for index, label in enumerate(labels):
            colour = SLICE_COLOURS[index % len(SLICE_COLOURS)]
            colours[label] = colour
            sweep = 360.0 * raw[label] / total if total > 0 else 0.0
            end = start + sweep
            if sweep > 0:
                pdf.set_fill_color(colour)
                # Page y grows downwards, so increasing angles run clockwise.
                pdf.solid_arc(x, y, diameter, round(start, 4), round(end, 4), style="F")
            start = end
        hole = diameter * 0.55
        offset = (diameter - hole) / 2
        pdf.set_fill_color(WHITE)
        pdf.ellipse(x + offset, y + offset, hole, hole, style="F")
        return colours

    def allocation(self, y: float, h: float) -> None:
        report = self.report
        self.panel(MARGIN, y, CONTENT_W, h)
        self.text(MARGIN + PAD, y + 3, 80, 5, "Port Allocation", 9, "B")

        diameter = 32.0
        chart_x = MARGIN + PAD
        chart_y = y + 12
        colours = self.donut(chart_x, chart_y, diameter)
        legend_x = chart_x + diameter + 4
        legend_y = chart_y + 5
        for item in report["allocation"]:
            label = item["label"]
            self.pdf.set_fill_color(colours.get(label, SECONDARY))
            self.pdf.rect(legend_x, legend_y + 1, 2.5, 2.5, style="F")
            entry = f"{label} {item['weight']}"
            self.text(legend_x + 3.5, legend_y, 18, 4.5, entry, 7.5)
            legend_y += 6

        total = {**report["holdings_total"], "ticker": TOTAL_LABEL}
        table_w = sum(c[2] for c in HOLDINGS_COLUMNS)
        rows = [*report["holdings"], total]
        self.table(
            RIGHT - PAD - table_w, y + 10, HOLDINGS_COLUMNS, rows, 6.5, bold_last=True
        )
        # Inside the panel, under the donut.
        caption_y = chart_y + diameter + 2
        self.text(chart_x, caption_y, 55, 3.5, CAPTION, 7, "", SECONDARY)

    def summary(self, y: float, h: float) -> None:
        self.panel(MARGIN, y, CONTENT_W, h)
        self.text(MARGIN + PAD, y + 3, 80, 5, "Summary Performance", 9, "B")
        bottom = self.table(
            MARGIN + PAD, y + 10, SUMMARY_COLUMNS, self.report["summary"], 7.0
        )
        self.text(MARGIN + PAD, bottom + 2, CONTENT_W - 2 * PAD, 3, FOOTNOTE, 6)

    def page_one(self) -> None:
        self.page("Summary Performance")
        customer_w = CONTENT_W * 0.45
        self.customer(MARGIN, 57, customer_w, 40)
        cards_x = MARGIN + customer_w + 4
        self.cards(cards_x, 57, RIGHT - cards_x)
        self.allocation(101, 58)
        self.summary(166, 47)

    # --- Page 2 -------------------------------------------------------------

    def page_two(self) -> None:
        self.page("Transaction")
        rows = self.report["transactions"]
        row_h = 7.0
        top = 57.0
        self.panel(MARGIN, top, CONTENT_W, 14 + row_h * (len(rows) + 1))
        self.text(MARGIN + PAD, top + 3, 80, 5, "Transaction details", 9, "B")
        self.table(MARGIN + PAD, top + 10, TRANSACTION_COLUMNS, rows, row_h)

    # --- Instrument pages ---------------------------------------------------

    def instrument_card(
        self,
        x: float,
        y: float,
        w: float,
        h: float,
        cards: dict[str, str],
        spec: CardSpec,
    ) -> None:
        """Card: value (bold 14 pt) over its label, optional sub-label and value.

        The sub-label value is red when it is printed with a minus sign.
        """
        label, key, sub_label, sub_key = spec
        pad = 2.5
        inner = w - 2 * pad
        self.panel(x, y, w, h)
        self.text(x + pad, y + 3, inner, 6, cards[key], 14, "B")
        self.text(x + pad, y + 10, inner, 3.5, label, 7, "", SECONDARY)
        if sub_label:
            self.text(x + pad, y + 13.5, inner, 3, sub_label, 6.5, "", SECONDARY)
            sub_x = x + pad + self.width(sub_label, 6.5) + 1.5
            value = cards[sub_key]
            colour = _sign_colour(value)
            self.text(sub_x, y + 13.5, x + w - pad - sub_x, 3, value, 6.5, "B", colour)

    def instrument_cards(self, item: Report, y: float) -> float:
        """Draw the card grid and the approximate value line; return its bottom."""
        cards: dict[str, str] = item["cards"]
        gap = 3.0
        card_h = 18.0
        for row in INSTRUMENT_CARD_ROWS:
            card_w = (CONTENT_W - gap * (len(row) - 1)) / len(row)
            for index, spec in enumerate(row):
                x = MARGIN + index * (card_w + gap)
                self.instrument_card(x, y, card_w, card_h, cards, spec)
            y += card_h + gap
        self.hline(MARGIN, RIGHT, y)
        y += 1.5
        self.text(MARGIN, y, CONTENT_W, 3.5, APPROX_LABEL, 7, "", SECONDARY)
        value_x = MARGIN + self.width(APPROX_LABEL, 7) + 2
        value = item["initial_cost_value"]
        self.text(value_x, y, RIGHT - value_x, 3.5, value, 7, "", SECONDARY)
        return y + 3.5

    def legend(
        self, right: float, y: float, entries: Iterable[tuple[str, str]]
    ) -> None:
        """Legend entries (colour square and label) ending at ``right``."""
        items = list(entries)
        widths = [self.width(label, 6.5) for label, _ in items]
        x = right - sum(3.5 + w for w in widths) - 3 * (len(items) - 1)
        for (label, colour), w in zip(items, widths, strict=True):
            self.square(x, y + 0.25, colour)
            self.text(x + 3.5, y, w, 3, label, 6.5, "", SECONDARY)
            x += 3.5 + w + 3

    def chart(
        self,
        x: float,
        y: float,
        w: float,
        h: float,
        chart: Report,
        titles: tuple[str, str, str, str],
        axes: tuple[str, str],
        legend: Sequence[tuple[str, str]],
        series: tuple[Series, Series],
    ) -> None:
        """Line chart panel with two series, each scaled to its own axis.

        ``titles`` holds the chart title, the caption and the left and right
        axis titles; ``axes`` names the ``chart.axes`` entries of the left and
        right axes; ``series`` holds the left-axis and the right-axis series.
        Every point is plotted, evenly spaced by index.
        """
        pdf = self.pdf
        title, caption, left_title, right_title = titles
        self.panel(x, y, w, h)
        self.text(x + PAD, y + 3, w - 2 * PAD, 5, title, 9, "B")
        self.legend(x + w - PAD, y + 9, legend)

        left = x + 14
        right = x + w - 14
        top = y + 17
        bottom = y + h - 9
        self.text(
            x + 1, top - 4.5, left - x - 2, 3, left_title, 6, "B", SECONDARY, True
        )
        self.text(
            right + 1, top - 4.5, x + w - right - 2, 3, right_title, 6, "B", SECONDARY
        )

        dates: list[str] = chart["dates"]
        count = len(dates)

        def x_at(index: int) -> float:
            if count <= 1:
                return (left + right) / 2
            return left + (right - left) * index / (count - 1)

        # Light grid: one line per y tick and per x label.
        left_axis: dict[str, Any] = chart["axes"][axes[0]]
        right_axis: dict[str, Any] = chart["axes"][axes[1]]
        ticks = len(left_axis["ticks"])
        tick_ys = [
            bottom - (bottom - top) * k / (ticks - 1) if ticks > 1 else bottom
            for k in range(ticks)
        ]
        for tick_y in tick_ys:
            self.hline(left, right, tick_y, GRID_LINE)
        pdf.set_line_width(GRID_LINE)
        pdf.set_draw_color(BORDER)
        for label in chart["x_labels"]:
            at = x_at(int(label["index"]))
            pdf.line(at, top, at, bottom)

        for (values, colour, dashed), scale in zip(
            series, (left_axis, right_axis), strict=True
        ):
            low = float(scale["min"])
            high = float(scale["max"])
            span = high - low

            def y_at(value: str, low: float = low, span: float = span) -> float:
                return bottom - (bottom - top) * (float(value) - low) / span

            points = [(x_at(i), y_at(v)) for i, v in enumerate(values)]
            pdf.set_line_width(SERIES_LINE)
            pdf.set_draw_color(colour)
            if dashed:
                pdf.set_dash_pattern(dash=DASH[0], gap=DASH[1])
            pdf.polyline(points, style="D")
            if dashed:
                pdf.set_dash_pattern()

        for tick_y, low_label, high_label in zip(
            tick_ys, left_axis["ticks"], right_axis["ticks"], strict=True
        ):
            self.text(
                x + 1, tick_y - 1.5, left - x - 2, 3, low_label, 6, "", SECONDARY, True
            )
            self.text(
                right + 1,
                tick_y - 1.5,
                x + w - right - 2,
                3,
                high_label,
                6,
                "",
                SECONDARY,
            )
        for label in chart["x_labels"]:
            at = x_at(int(label["index"]))
            pdf.set_font(FONT, "", 6)
            pdf.set_text_color(SECONDARY)
            pdf.set_xy(at - 8, bottom + 1)
            pdf.cell(16, 3, label["label"], align="C")

        self.text(x, y + h + 1, w, 3.5, caption, 7, "", SECONDARY)

    def instrument_page(self, item: Report) -> None:
        """One instrument: card grid, two line charts and its transactions."""
        self.page(item["ticker"])
        self.instrument_cards(item, 57)

        chart = item["chart"]
        gap = 4.0
        chart_w = (CONTENT_W - gap) / 2
        chart_y = 107.0
        chart_h = 68.0
        self.chart(
            MARGIN,
            chart_y,
            chart_w,
            chart_h,
            chart,
            (PRICE_CHART_TITLE, PRICE_CHART_CAPTION, PRICE_AXIS, PRICE_AXIS),
            ("price", "price"),
            ((AVG_COST_LEGEND, NAVY), (MARKET_PRICE_LEGEND, GREEN)),
            ((chart["avg_cost"], NAVY, False), (chart["market_price"], GREEN, False)),
        )
        self.chart(
            MARGIN + chart_w + gap,
            chart_y,
            chart_w,
            chart_h,
            chart,
            (VOLUME_CHART_TITLE, VOLUME_CHART_CAPTION, VOLUME_AXIS, PRICE_AXIS),
            ("nav_volume_pct", "market_price"),
            ((NAV_VOLUME_LEGEND, CHART_BLUE), (MARKET_PRICE_LEGEND, NEGATIVE)),
            (
                (chart["nav_volume_pct"], CHART_BLUE, False),
                (chart["market_price"], NEGATIVE, True),
            ),
        )

        rows = item["transactions"]
        row_h = 7.0
        top = 184.0
        self.panel(MARGIN, top, CONTENT_W, 14 + row_h * (len(rows) + 1))
        self.text(MARGIN + PAD, top + 3, 80, 5, "Transaction details", 9, "B")
        self.table(MARGIN + PAD, top + 10, INSTRUMENT_TRANSACTION_COLUMNS, rows, row_h)


def render_pdf(report: Report) -> bytes:
    """Draw the Grid report: pages 1 and 2, then one page per instrument.

    Args:
        report: The report dict as written to ``report.json``.

    Returns:
        The PDF bytes; equal for equal input.
    """
    writer = _Writer(report)
    writer.page_one()
    writer.page_two()
    for item in report["instruments"]:
        writer.instrument_page(item)
    return bytes(writer.pdf.output())
