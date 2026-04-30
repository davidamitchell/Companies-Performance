"""Tests for src/processing/extract_disclosures.py."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock, patch

import pytest

from src.processing.extract_disclosures import (
    _detect_unit_scale,
    _extract_first_value,
    _extract_metric,
    _extract_second_pct,
    extract_disclosures,
)

# ── Unit scale detection ──────────────────────────────────────────────────────


def test_detect_unit_scale_millions_dollar_sign() -> None:
    assert _detect_unit_scale("$ millions Note Current Previous") == 1.0


def test_detect_unit_scale_millions_nzdm() -> None:
    assert _detect_unit_scale("NZ$m NZ$m") == 1.0


def test_detect_unit_scale_thousands_apostrophe() -> None:
    assert _detect_unit_scale("$'000 $'000") == 0.001


def test_detect_unit_scale_thousands_word() -> None:
    assert _detect_unit_scale("NZD thousands") == 0.001


def test_detect_unit_scale_defaults_to_millions_when_ambiguous() -> None:
    assert _detect_unit_scale("some random text with no unit indicators") == 1.0


# ── _extract_first_value ──────────────────────────────────────────────────────


def test_extract_first_value_plain_number() -> None:
    assert _extract_first_value("Net interest income 824 794", scale=1.0) == 824.0


def test_extract_first_value_skips_note_number() -> None:
    # Note reference "5" should be skipped; (582) is the real value
    assert _extract_first_value("Operating expenses 5 (582) (534)", scale=1.0) == -582.0


def test_extract_first_value_bracketed_negative() -> None:
    assert _extract_first_value("Interest expense (1,159) (595)", scale=1.0) == -1159.0


def test_extract_first_value_comma_thousands() -> None:
    assert _extract_first_value("Loans and advances 7 32,445 29,682", scale=1.0) == 32445.0


def test_extract_first_value_large_note_skipped() -> None:
    # Note 17 should be skipped; 28,176 is the real value
    assert _extract_first_value("Deposits 17 28,176 25,756", scale=1.0) == 28176.0


def test_extract_first_value_nzd_thousands_scale() -> None:
    # With scale=0.001, value of 32,445 (thousands) → 32.445 (NZDm)
    result = _extract_first_value("Loans and advances 7 32,445 29,682", scale=0.001)
    assert result == pytest.approx(32.445)


def test_extract_first_value_returns_none_when_no_number() -> None:
    assert _extract_first_value("Just some text with no numbers here", scale=1.0) is None


def test_extract_first_value_skips_only_bare_integers_not_bracketed() -> None:
    # (5) is bracketed — should NOT be skipped as a note number
    result = _extract_first_value("Some metric (5) 10", scale=1.0)
    assert result == -5.0


# ── Bracketed negative parsing ────────────────────────────────────────────────


@pytest.mark.parametrize(
    "line,expected",
    [
        ("Credit impairment (24) (37)", -24.0),
        ("Income tax expense 6 (72) (70)", -72.0),
        ("Interest expense 2 (1,159) (595)", -1159.0),
        ("Reserves 26 (6) 102", -6.0),
    ],
)
def test_bracketed_negative_parsing(line: str, expected: float) -> None:
    assert _extract_first_value(line, scale=1.0) == expected


# ── _extract_second_pct ───────────────────────────────────────────────────────


def test_extract_second_pct_returns_current_period_ratio() -> None:
    line = "Common equity Tier 1 capital ratio 4.5% 11.9% 10.3%"
    assert _extract_second_pct(line) == 11.9


def test_extract_second_pct_total_capital_ratio() -> None:
    line = "Total capital ratio 8.0% 15.6% 14.3%"
    assert _extract_second_pct(line) == 15.6


def test_extract_second_pct_falls_back_when_only_one_pct() -> None:
    # Some older formats may only show the bank's ratio without the minimum
    line = "CET1 ratio 12.5%"
    assert _extract_second_pct(line) == 12.5


def test_extract_second_pct_returns_none_when_no_pct() -> None:
    assert _extract_second_pct("No percentages on this line") is None


# ── _extract_metric ───────────────────────────────────────────────────────────


def test_extract_metric_first_value_strategy() -> None:
    text = "Financial statements\nNet interest income 824 794\nOther income 53"
    result = _extract_metric(text, [r"net interest income\b"], "first_value", 1.0)
    assert result == 824.0


def test_extract_metric_second_pct_strategy() -> None:
    text = "Capital adequacy\nTotal capital ratio 8.0% 15.6% 14.3%\n"
    result = _extract_metric(text, [r"total capital ratio\b"], "second_pct", 1.0)
    assert result == 15.6


def test_extract_metric_uses_first_matching_line() -> None:
    # If the metric appears more than once, first occurrence is used
    text = "Net interest income 824 794\nNet interest income 820 790\n"
    result = _extract_metric(text, [r"net interest income\b"], "first_value", 1.0)
    assert result == 824.0


def test_extract_metric_returns_none_when_not_found() -> None:
    text = "Some financial text without the metric"
    result = _extract_metric(text, [r"net interest income\b"], "first_value", 1.0)
    assert result is None


def test_extract_metric_case_insensitive() -> None:
    text = "NET INTEREST INCOME 824 794"
    result = _extract_metric(text, [r"net interest income\b"], "first_value", 1.0)
    assert result == 824.0


# ── extract_disclosures ───────────────────────────────────────────────────────


def _make_sources_config(bank_id: str, entity_name: str) -> dict[str, Any]:
    return {
        "financial_disclosures": {
            "banks": [
                {
                    "id": bank_id,
                    "rbnz_entity_name": entity_name,
                }
            ]
        }
    }


_KIWIBANK_TEXT = """\
Financial statements
Income statement
For the year ended 30 June 2024
$ millions Note 30 June 24 30 June 23
Interest income 2 1,983 1,389
Interest expense 2 (1,159) (595)
Net interest income 824 794
Other operating income 4 53 39
Total operating income 880 816
Operating expenses 5 (582) (534)
Profit after tax 202 175
Balance sheet
As at 30 June 2024
$ millions Note 30 June 24 30 June 23
Loans and advances 7 32,445 29,682
Deposits 17 28,176 25,756
Total assets 36,650 33,838
Total equity 2,621 2,311
Capital adequacy and regulatory liquidity ratios
Common equity Tier 1 capital ratio 4.5% 11.9% 10.3%
Total capital ratio 8.0% 15.6% 14.3%
"""


def _mock_pdfplumber(text: str):
    """Return a context manager that yields a mock pdfplumber PDF with one page."""
    page = MagicMock()
    page.extract_text.return_value = text
    pdf_mock = MagicMock()
    pdf_mock.pages = [page]
    pdf_mock.__enter__ = MagicMock(return_value=pdf_mock)
    pdf_mock.__exit__ = MagicMock(return_value=False)
    return pdf_mock


def test_extract_disclosures_happy_path(tmp_path: Path) -> None:
    """Happy path: single PDF with sidecar returns all expected metrics."""
    bank_dir = tmp_path / "kiwibank"
    bank_dir.mkdir()
    pdf_path = bank_dir / "kiwibank-disclosure-2024-06-30.pdf"
    pdf_path.touch()

    meta = {
        "bank_id": "kiwibank",
        "period_end": "2024-06-30",
        "period_type": "full_year",
    }
    (bank_dir / "kiwibank-disclosure-2024-06-30.meta.json").write_text(
        json.dumps(meta), encoding="utf-8"
    )

    sources = _make_sources_config("kiwibank", "Kiwibank")
    with patch(
        "src.processing.extract_disclosures.pdfplumber.open",
        return_value=_mock_pdfplumber(_KIWIBANK_TEXT),
    ):
        rows = extract_disclosures(tmp_path, sources)

    assert len(rows) > 0
    metrics_found = {r["metric"] for r in rows}
    assert "Net Interest Income" in metrics_found
    assert "Total Operating Income" in metrics_found
    assert "Operating Expenses" in metrics_found
    assert "Profit After Tax" in metrics_found
    assert "Total Assets" in metrics_found
    assert "Net Loans and Advances" in metrics_found
    assert "Deposits" in metrics_found
    assert "Equity" in metrics_found
    assert "CET1 Ratio" in metrics_found
    assert "Total Capital Ratio" in metrics_found


def test_extract_disclosures_correct_values(tmp_path: Path) -> None:
    """Extracted values match the known text content."""
    bank_dir = tmp_path / "kiwibank"
    bank_dir.mkdir()
    pdf_path = bank_dir / "kiwibank-disclosure-2024-06-30.pdf"
    pdf_path.touch()
    (bank_dir / "kiwibank-disclosure-2024-06-30.meta.json").write_text(
        json.dumps({"bank_id": "kiwibank", "period_end": "2024-06-30"}),
        encoding="utf-8",
    )

    sources = _make_sources_config("kiwibank", "Kiwibank")
    with patch(
        "src.processing.extract_disclosures.pdfplumber.open",
        return_value=_mock_pdfplumber(_KIWIBANK_TEXT),
    ):
        rows = extract_disclosures(tmp_path, sources)

    by_metric = {r["metric"]: r["value"] for r in rows}
    assert by_metric["Net Interest Income"] == 824.0
    assert by_metric["Total Operating Income"] == 880.0
    assert by_metric["Operating Expenses"] == -582.0
    assert by_metric["Profit After Tax"] == 202.0
    assert by_metric["Total Assets"] == 36650.0
    assert by_metric["Net Loans and Advances"] == 32445.0
    assert by_metric["Deposits"] == 28176.0
    assert by_metric["Equity"] == 2621.0
    assert by_metric["CET1 Ratio"] == 11.9
    assert by_metric["Total Capital Ratio"] == 15.6


def test_extract_disclosures_source_field_is_disclosure_kiwibank(tmp_path: Path) -> None:
    """Source field is 'disclosure-kiwibank' for Kiwibank rows."""
    bank_dir = tmp_path / "kiwibank"
    bank_dir.mkdir()
    (bank_dir / "kiwibank-disclosure-2024-06-30.pdf").touch()
    (bank_dir / "kiwibank-disclosure-2024-06-30.meta.json").write_text(
        json.dumps({"bank_id": "kiwibank", "period_end": "2024-06-30"}),
        encoding="utf-8",
    )

    sources = _make_sources_config("kiwibank", "Kiwibank")
    with patch(
        "src.processing.extract_disclosures.pdfplumber.open",
        return_value=_mock_pdfplumber(_KIWIBANK_TEXT),
    ):
        rows = extract_disclosures(tmp_path, sources)

    assert all(r["source"] == "disclosure-kiwibank" for r in rows)


def test_extract_disclosures_period_format(tmp_path: Path) -> None:
    """Period is YYYY-QN derived from period_end in meta.json."""
    bank_dir = tmp_path / "kiwibank"
    bank_dir.mkdir()
    (bank_dir / "kiwibank-disclosure-2024-06-30.pdf").touch()
    (bank_dir / "kiwibank-disclosure-2024-06-30.meta.json").write_text(
        json.dumps({"bank_id": "kiwibank", "period_end": "2024-06-30"}),
        encoding="utf-8",
    )

    sources = _make_sources_config("kiwibank", "Kiwibank")
    with patch(
        "src.processing.extract_disclosures.pdfplumber.open",
        return_value=_mock_pdfplumber(_KIWIBANK_TEXT),
    ):
        rows = extract_disclosures(tmp_path, sources)

    assert all(r["period"] == "2024-Q2" for r in rows)


def test_extract_disclosures_missing_sidecar_skips_pdf(
    tmp_path: Path, caplog: pytest.LogCaptureFixture
) -> None:
    """PDF without a .meta.json sidecar is skipped and a warning is logged."""
    bank_dir = tmp_path / "kiwibank"
    bank_dir.mkdir()
    (bank_dir / "kiwibank-disclosure-2024-06-30.pdf").touch()
    # No .meta.json created

    sources = _make_sources_config("kiwibank", "Kiwibank")
    import logging

    with caplog.at_level(logging.WARNING):
        rows = extract_disclosures(tmp_path, sources)

    assert rows == []
    assert any("Sidecar missing" in r.message for r in caplog.records)


def test_extract_disclosures_empty_pdf_returns_empty_list(tmp_path: Path) -> None:
    """PDF that yields no text returns an empty list and does not crash."""
    bank_dir = tmp_path / "kiwibank"
    bank_dir.mkdir()
    (bank_dir / "kiwibank-disclosure-2024-06-30.pdf").touch()
    (bank_dir / "kiwibank-disclosure-2024-06-30.meta.json").write_text(
        json.dumps({"bank_id": "kiwibank", "period_end": "2024-06-30"}),
        encoding="utf-8",
    )

    sources = _make_sources_config("kiwibank", "Kiwibank")
    with patch(
        "src.processing.extract_disclosures.pdfplumber.open",
        return_value=_mock_pdfplumber(""),
    ):
        rows = extract_disclosures(tmp_path, sources)

    assert rows == []


def test_extract_disclosures_nzd_thousands_normalisation(tmp_path: Path) -> None:
    """Values in NZD thousands are divided by 1000 to yield NZDm."""
    text_thousands = """\
$'000 Note Current Previous
Net interest income 824,000 794,000
Total operating income 880,000 816,000
Operating expenses (582,000) (534,000)
Profit after tax 202,000 175,000
Total assets 36,650,000 33,838,000
Loans and advances 32,445,000 29,682,000
Deposits 28,176,000 25,756,000
Total equity 2,621,000 2,311,000
Common equity Tier 1 capital ratio 4.5% 11.9% 10.3%
Total capital ratio 8.0% 15.6% 14.3%
"""
    bank_dir = tmp_path / "kiwibank"
    bank_dir.mkdir()
    (bank_dir / "kiwibank-disclosure-2024-06-30.pdf").touch()
    (bank_dir / "kiwibank-disclosure-2024-06-30.meta.json").write_text(
        json.dumps({"bank_id": "kiwibank", "period_end": "2024-06-30"}),
        encoding="utf-8",
    )

    sources = _make_sources_config("kiwibank", "Kiwibank")
    with patch(
        "src.processing.extract_disclosures.pdfplumber.open",
        return_value=_mock_pdfplumber(text_thousands),
    ):
        rows = extract_disclosures(tmp_path, sources)

    by_metric = {r["metric"]: r["value"] for r in rows}
    # Values should be normalised to NZDm (÷ 1000)
    assert by_metric["Net Interest Income"] == pytest.approx(824.0)
    assert by_metric["Total Assets"] == pytest.approx(36650.0)
    assert by_metric["Operating Expenses"] == pytest.approx(-582.0)


def test_extract_disclosures_entity_from_config(tmp_path: Path) -> None:
    """Entity name comes from rbnz_entity_name in sources config."""
    bank_dir = tmp_path / "kiwibank"
    bank_dir.mkdir()
    (bank_dir / "kiwibank-disclosure-2024-06-30.pdf").touch()
    (bank_dir / "kiwibank-disclosure-2024-06-30.meta.json").write_text(
        json.dumps({"bank_id": "kiwibank", "period_end": "2024-06-30"}),
        encoding="utf-8",
    )

    sources = _make_sources_config("kiwibank", "Kiwibank")
    with patch(
        "src.processing.extract_disclosures.pdfplumber.open",
        return_value=_mock_pdfplumber(_KIWIBANK_TEXT),
    ):
        rows = extract_disclosures(tmp_path, sources)

    assert all(r["entity"] == "Kiwibank" for r in rows)
