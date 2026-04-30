"""Tests for src/processing/parse_ocr.py."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock, patch

import pytest

from src.processing.parse_ocr import (
    _extract_monthly,
    _find_ocr_column,
    _monthly_to_quarterly,
    parse_ocr,
)

# ── _find_ocr_column ──────────────────────────────────────────────────────────


def test_find_ocr_column_exact_match() -> None:
    rows = [("Date", "90-day rate", "OCR", "Swap rate")]
    assert _find_ocr_column(rows) == 2  # type: ignore[arg-type]


def test_find_ocr_column_official_cash_rate() -> None:
    rows = [("Date", "Official Cash Rate", "90-day")]
    assert _find_ocr_column(rows) == 1  # type: ignore[arg-type]


def test_find_ocr_column_case_insensitive() -> None:
    rows = [("Date", "official cash rate", "swap")]
    assert _find_ocr_column(rows) == 1  # type: ignore[arg-type]


def test_find_ocr_column_not_found_raises_value_error() -> None:
    rows = [("Date", "90-day rate", "swap rate")]
    with pytest.raises(ValueError, match="No OCR column"):
        _find_ocr_column(rows)  # type: ignore[arg-type]


# ── _extract_monthly ──────────────────────────────────────────────────────────


def _dt(year: int, month: int) -> datetime:
    return datetime(year, month, 1)


def test_extract_monthly_returns_date_value_pairs() -> None:
    rows = [
        (_dt(2024, 1), 5.5),
        (_dt(2024, 2), 5.5),
        (_dt(2024, 3), 5.5),
    ]
    result = _extract_monthly(rows, date_col=0, ocr_col=1)
    assert result == [
        (_dt(2024, 1), 5.5),
        (_dt(2024, 2), 5.5),
        (_dt(2024, 3), 5.5),
    ]


def test_extract_monthly_skips_null_ocr() -> None:
    rows = [
        (_dt(2024, 1), 5.5),
        (_dt(2024, 2), None),
        (_dt(2024, 3), 5.5),
    ]
    result = _extract_monthly(rows, date_col=0, ocr_col=1)
    assert len(result) == 2
    assert (_dt(2024, 2), None) not in result


def test_extract_monthly_skips_non_date_rows() -> None:
    rows = [
        ("Date", "OCR"),  # header row — no month attribute
        (_dt(2024, 1), 5.5),
    ]
    result = _extract_monthly(rows, date_col=0, ocr_col=1)
    assert len(result) == 1


def test_extract_monthly_converts_string_to_float() -> None:
    rows = [(_dt(2024, 1), "5.5")]
    result = _extract_monthly(rows, date_col=0, ocr_col=1)
    assert result == [(_dt(2024, 1), 5.5)]


# ── _monthly_to_quarterly ─────────────────────────────────────────────────────


def test_monthly_to_quarterly_uses_last_month_per_quarter() -> None:
    monthly = [
        (_dt(2024, 1), 5.5),
        (_dt(2024, 2), 5.5),
        (_dt(2024, 3), 5.25),  # last in Q1
        (_dt(2024, 4), 5.5),
        (_dt(2024, 5), 5.5),
        (_dt(2024, 6), 5.5),  # last in Q2
    ]
    result = _monthly_to_quarterly(monthly)
    assert ("2024-Q1", 5.25) in result
    assert ("2024-Q2", 5.5) in result


def test_monthly_to_quarterly_single_month_per_quarter() -> None:
    monthly = [(_dt(2024, 3), 5.5)]
    result = _monthly_to_quarterly(monthly)
    assert result == [("2024-Q1", 5.5)]


def test_monthly_to_quarterly_sorted_output() -> None:
    monthly = [
        (_dt(2023, 12), 5.5),
        (_dt(2024, 3), 5.25),
        (_dt(2024, 6), 5.5),
    ]
    result = _monthly_to_quarterly(monthly)
    periods = [p for p, _ in result]
    assert periods == sorted(periods)


def test_monthly_to_quarterly_overwrites_with_later_month() -> None:
    # Q1 has Jan=5.5, Feb=5.5, Mar=5.25 → Q1 value should be 5.25
    monthly = [
        (_dt(2024, 1), 5.5),
        (_dt(2024, 2), 5.5),
        (_dt(2024, 3), 5.25),
    ]
    result = _monthly_to_quarterly(monthly)
    assert len(result) == 1
    assert result[0] == ("2024-Q1", 5.25)


def test_monthly_to_quarterly_empty_returns_empty() -> None:
    assert _monthly_to_quarterly([]) == []


# ── parse_ocr integration ─────────────────────────────────────────────────────


def _make_mock_workbook(rows: list[tuple[Any, ...]]) -> MagicMock:
    """Build a mock openpyxl workbook with a single active sheet."""
    ws_mock = MagicMock()
    ws_mock.iter_rows.return_value = iter(rows)
    wb_mock = MagicMock()
    wb_mock.active = ws_mock
    wb_mock.__enter__ = MagicMock(return_value=wb_mock)
    wb_mock.__exit__ = MagicMock(return_value=False)
    return wb_mock


def test_parse_ocr_happy_path(tmp_path: Path) -> None:
    """Mock XLSX with OCR column returns canonical rows."""
    xlsx_path = tmp_path / "rbnz-ocr.xlsx"
    xlsx_path.touch()

    rows_data = [
        ("Date", "90-day", "OCR"),  # header
        (_dt(2024, 1), 5.25, 5.5),
        (_dt(2024, 2), 5.25, 5.5),
        (_dt(2024, 3), 5.25, 5.5),  # end of Q1
        (_dt(2024, 4), 5.25, 5.5),
        (_dt(2024, 5), 5.25, 5.5),
        (_dt(2024, 6), 5.25, 5.5),  # end of Q2
    ]

    with patch(
        "src.processing.parse_ocr.openpyxl.load_workbook",
        return_value=_make_mock_workbook(rows_data),
    ):
        rows = parse_ocr(xlsx_path=xlsx_path)

    assert len(rows) == 2  # Q1 and Q2
    assert rows[0] == {
        "entity": "RBNZ",
        "metric": "OCR",
        "value": 5.5,
        "period": "2024-Q1",
        "source": "rbnz-ocr",
    }
    assert rows[1]["period"] == "2024-Q2"


def test_parse_ocr_missing_file_raises_file_not_found(tmp_path: Path) -> None:
    """FileNotFoundError raised with clear message when file missing."""
    with pytest.raises(FileNotFoundError, match="OCR XLSX not found"):
        parse_ocr(xlsx_path=tmp_path / "nonexistent.xlsx")


def test_parse_ocr_no_ocr_column_raises_value_error(tmp_path: Path) -> None:
    """ValueError raised when no OCR column found."""
    xlsx_path = tmp_path / "rbnz-ocr.xlsx"
    xlsx_path.touch()

    rows_data = [
        ("Date", "90-day rate", "Swap rate"),
        (_dt(2024, 1), 5.25, 3.5),
    ]

    with (
        patch(
            "src.processing.parse_ocr.openpyxl.load_workbook",
            return_value=_make_mock_workbook(rows_data),
        ),
        pytest.raises(ValueError, match="No OCR column"),
    ):
        parse_ocr(xlsx_path=xlsx_path)


def test_parse_ocr_canonical_schema(tmp_path: Path) -> None:
    """All rows have entity=RBNZ, metric=OCR, source=rbnz-ocr."""
    xlsx_path = tmp_path / "rbnz-ocr.xlsx"
    xlsx_path.touch()

    rows_data = [
        ("Date", "OCR"),
        (_dt(2024, 3), 5.5),
        (_dt(2024, 6), 5.5),
    ]

    with patch(
        "src.processing.parse_ocr.openpyxl.load_workbook",
        return_value=_make_mock_workbook(rows_data),
    ):
        rows = parse_ocr(xlsx_path=xlsx_path)

    for row in rows:
        assert row["entity"] == "RBNZ"
        assert row["metric"] == "OCR"
        assert row["source"] == "rbnz-ocr"


def test_parse_ocr_fallback_to_glob(tmp_path: Path) -> None:
    """Falls back to rbnz-ocr*.xlsx glob when primary path absent."""
    (tmp_path / "rbnz-ocr-2024.xlsx").touch()

    rows_data = [
        ("Date", "OCR"),
        (_dt(2024, 6), 5.5),
    ]

    with patch(
        "src.processing.parse_ocr.openpyxl.load_workbook",
        return_value=_make_mock_workbook(rows_data),
    ):
        rows = parse_ocr(raw_dir=tmp_path)

    assert len(rows) == 1
    assert rows[0]["value"] == 5.5


def test_parse_ocr_no_file_anywhere_raises(tmp_path: Path) -> None:
    """FileNotFoundError when no file found via any resolution method."""
    with pytest.raises(FileNotFoundError):
        parse_ocr(raw_dir=tmp_path)


def test_parse_ocr_monthly_to_quarterly_conversion(tmp_path: Path) -> None:
    """Monthly data: 3 months in a quarter → last value is used."""
    xlsx_path = tmp_path / "rbnz-ocr.xlsx"
    xlsx_path.touch()

    rows_data = [
        ("Date", "OCR"),
        (_dt(2024, 1), 5.75),  # Jan
        (_dt(2024, 2), 5.5),  # Feb
        (_dt(2024, 3), 5.25),  # Mar — this is the Q1 value
    ]

    with patch(
        "src.processing.parse_ocr.openpyxl.load_workbook",
        return_value=_make_mock_workbook(rows_data),
    ):
        rows = parse_ocr(xlsx_path=xlsx_path)

    assert len(rows) == 1
    assert rows[0]["period"] == "2024-Q1"
    assert rows[0]["value"] == 5.25  # last month of Q1
