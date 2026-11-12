"""Narrative writing rules, number traceability, helpers and formatters."""

from __future__ import annotations

import json
import re
from decimal import Decimal
from pathlib import Path
from typing import Any

import pytest

from quant_software_factory.reports.returns_transactions.checks import (
    report_values,
    untraceable_numbers,
)
from quant_software_factory.reports.returns_transactions.cli import main
from quant_software_factory.reports.returns_transactions.formatting import (
    fmt_int,
    fmt_money,
    fmt_pct,
)
from quant_software_factory.reports.returns_transactions.narrative import (
    BANNED_PHRASES,
    NUMBER_RE,
    banned_phrases_in,
    first_word,
    repeated_openers,
    split_paragraphs,
    split_sentences,
    word_count,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
FIXTURE_DIR = REPO_ROOT / "data" / "examples" / "demo_coop_rg_2026_10"


@pytest.fixture(scope="module")
def generated(tmp_path_factory: pytest.TempPathFactory) -> tuple[str, dict[str, Any]]:
    out = tmp_path_factory.mktemp("narrative")
    assert main([str(FIXTURE_DIR), str(out)]) == 0
    narrative = (out / "narrative.md").read_text(encoding="utf-8")
    report = json.loads((out / "report.json").read_text(encoding="utf-8"))
    return narrative, report


def test_every_narrative_number_is_in_report_json(
    generated: tuple[str, dict[str, Any]],
) -> None:
    narrative, report = generated
    values = report_values(report)
    tokens = NUMBER_RE.findall(narrative)
    assert tokens
    for token in tokens:
        assert token in values, token
    assert untraceable_numbers(narrative, report) == []
    assert not re.search(r"\d", NUMBER_RE.sub(" ", narrative))


def test_narrative_mentions_period_activity(
    generated: tuple[str, dict[str, Any]],
) -> None:
    narrative, _ = generated
    for value in ("17,835.00", "-3,037.00", "3,600.00", "27,398.00", "3.83%"):
        assert value in narrative


def test_narrative_matches_report_block(generated: tuple[str, dict[str, Any]]) -> None:
    narrative, report = generated
    assert split_paragraphs(narrative) == report["narrative"]["paragraphs"]


def test_narrative_style(generated: tuple[str, dict[str, Any]]) -> None:
    narrative, _ = generated
    assert 2 <= len(split_paragraphs(narrative)) <= 4
    assert word_count(narrative) < 180
    assert banned_phrases_in(narrative) == []
    assert repeated_openers(narrative) == []
    lowered = narrative.casefold()
    for phrase in BANNED_PHRASES:
        assert not re.search(r"\b" + re.escape(phrase) + r"\b", lowered)


def test_split_paragraphs() -> None:
    assert split_paragraphs("One.\n\nTwo.\n\n\nThree.\n") == ["One.", "Two.", "Three."]
    assert split_paragraphs("Single paragraph.\n") == ["Single paragraph."]


def test_split_sentences_keeps_decimals() -> None:
    text = "Cash was 1,234.56 THB. It rose! Did it? Yes."
    assert split_sentences(text) == [
        "Cash was 1,234.56 THB.",
        "It rose!",
        "Did it?",
        "Yes.",
    ]
    assert split_sentences("   ") == []


def test_first_word() -> None:
    assert first_word("The account sold") == "the"
    assert first_word("  BBB paid") == "bbb"
    assert first_word("") == ""


def test_word_count() -> None:
    assert word_count("one two  three\nfour") == 4


def test_repeated_openers() -> None:
    assert repeated_openers("The cat sat. The dog ran.") == ["the"]
    assert repeated_openers("The cat sat.\n\nthe dog ran.") == ["the"]
    assert repeated_openers("The cat sat. A dog ran. The bird flew.") == []


def test_banned_phrases() -> None:
    assert banned_phrases_in("A robust result.") == ["robust"]
    assert banned_phrases_in("It Will rise.") == ["will"]
    assert banned_phrases_in("In today's dynamic market, gains.") == [
        "in today's dynamic market"
    ]
    assert banned_phrases_in("Willow trees and plain words.") == []


def test_number_regex() -> None:
    text = "Gain of -3,037.00 THB, 9,000 shares, 3.83% return. Total 17,835.00."
    assert NUMBER_RE.findall(text) == ["-3,037.00", "9,000", "3.83%", "17,835.00"]


def test_untraceable_numbers_detects_missing_and_stray_digits() -> None:
    report: dict[str, Any] = {
        "kpi_summary": {"total_pnl": "27,398.00"},
        "narrative": {"paragraphs": ["1,234.56"]},
    }
    assert untraceable_numbers("Total 27,398.00 THB.", report) == []
    assert untraceable_numbers("Total 1,234.56 THB.", report) == ["1,234.56"]
    stray = untraceable_numbers("On 2026-10-30 the total was 27,398.00.", report)
    assert stray


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        (Decimal("2.675"), "2.68"),
        (Decimal("0.005"), "0.01"),
        (Decimal("-0.001"), "0.00"),
        (Decimal("-0.005"), "-0.01"),
        (Decimal("17835"), "17,835.00"),
        (Decimal("-3037"), "-3,037.00"),
        (Decimal("1234567.891"), "1,234,567.89"),
        (Decimal("0"), "0.00"),
    ],
)
def test_fmt_money(value: Decimal, expected: str) -> None:
    assert fmt_money(value) == expected


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        (Decimal("6.1224489795918367"), "6.12%"),
        (Decimal("-5"), "-5.00%"),
        (Decimal("3.8318881118881"), "3.83%"),
        (Decimal("-0.004"), "0.00%"),
        (Decimal("100"), "100.00%"),
    ],
)
def test_fmt_pct(value: Decimal, expected: str) -> None:
    assert fmt_pct(value) == expected


def test_fmt_int() -> None:
    assert fmt_int(9000) == "9,000"
    assert fmt_int(100) == "100"
    assert fmt_int(1234567) == "1,234,567"
