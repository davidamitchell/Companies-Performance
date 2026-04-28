"""Tests for scripts/spike_multi_bank_pdf.py."""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import MagicMock, patch

from scripts.spike_multi_bank_pdf import (
    _find_or_download,
    _is_toc_page,
    _section_narrative,
    load_banks,
    main,
)

# ---------------------------------------------------------------------------
# _is_toc_page
# ---------------------------------------------------------------------------


def test_is_toc_page_true_when_many_sections_present() -> None:
    """A page mentioning 3+ section keywords is treated as a TOC."""
    toc_text = (
        "Income statement 10\n"
        "Statement of financial position 12\n"
        "Cash flow statement 14\n"
        "Capital adequacy 60\n"
    )
    assert _is_toc_page(toc_text) is True


def test_is_toc_page_false_for_single_section() -> None:
    """A page mentioning only one section keyword is not a TOC."""
    text = "Income statement\nNet interest income 1,234\nOperating expenses 567\n"
    assert _is_toc_page(text) is False


def test_is_toc_page_false_for_two_sections() -> None:
    """Two section keywords are not enough to flag a TOC."""
    text = "Income statement\nNet interest income 1,234\nCapital adequacy\nCET1 ratio 13.5%\n"
    assert _is_toc_page(text) is False


# ---------------------------------------------------------------------------
# load_banks
# ---------------------------------------------------------------------------


def test_load_banks_returns_list(tmp_path: Path) -> None:
    """load_banks() returns the financial_disclosures banks list."""
    cfg = tmp_path / "config" / "sources.yaml"
    cfg.parent.mkdir()
    cfg.write_text(
        "financial_disclosures:\n"
        "  banks:\n"
        "    - id: testbank\n"
        "      reports:\n"
        "        - period_end: '2024-06-30'\n"
        "          period_type: full_year\n"
        "          url: https://example.com/test.pdf\n"
        "          status: confirmed\n",
        encoding="utf-8",
    )

    with patch("scripts.spike_multi_bank_pdf._CONFIG_PATH", cfg):
        banks = load_banks()

    assert isinstance(banks, list)
    assert banks[0]["id"] == "testbank"


# ---------------------------------------------------------------------------
# _find_or_download
# ---------------------------------------------------------------------------


def _make_bank(reports: list[dict]) -> dict:
    return {"id": "testbank", "reports": reports}


def test_find_or_download_returns_existing_file(tmp_path: Path) -> None:
    """_find_or_download returns immediately if the PDF already exists."""
    pdf = tmp_path / "testbank" / "testbank-disclosure-2024-06-30.pdf"
    pdf.parent.mkdir(parents=True)
    pdf.write_bytes(b"%PDF-1.4")

    bank = _make_bank(
        [{"period_end": "2024-06-30", "url": "https://example.com/test.pdf", "status": "confirmed"}]
    )

    with patch("scripts.spike_multi_bank_pdf._OUTPUT_ROOT", tmp_path):
        result = _find_or_download(bank)

    assert result is not None
    found_path, report = result
    assert found_path == pdf
    assert report["period_end"] == "2024-06-30"


def test_find_or_download_returns_none_when_all_fail(tmp_path: Path) -> None:
    """_find_or_download returns None when all download attempts fail."""
    bank = _make_bank(
        [{"period_end": "2024-06-30", "url": "https://example.com/test.pdf", "status": "confirmed"}]
    )

    with (
        patch("scripts.spike_multi_bank_pdf._OUTPUT_ROOT", tmp_path),
        patch("scripts.spike_multi_bank_pdf.download_pdf", side_effect=RuntimeError("HTTP 403")),
    ):
        result = _find_or_download(bank)

    assert result is None


def test_find_or_download_falls_back_to_older_report(tmp_path: Path) -> None:
    """_find_or_download tries older reports when the newest fails."""
    old_pdf = tmp_path / "testbank" / "testbank-disclosure-2022-12-31.pdf"
    old_pdf.parent.mkdir(parents=True)
    old_pdf.write_bytes(b"%PDF-1.4")

    bank = _make_bank(
        [
            {
                "period_end": "2024-06-30",
                "url": "https://example.com/new.pdf",
                "status": "confirmed",
            },
            {
                "period_end": "2022-12-31",
                "url": "https://example.com/old.pdf",
                "status": "confirmed",
            },
        ]
    )

    call_count = 0

    def _mock_download(url: str, dest: Path) -> None:
        nonlocal call_count
        call_count += 1
        if "new.pdf" in url:
            raise RuntimeError("HTTP 403")
        # old.pdf: do nothing (old_pdf already exists, won't reach here)
        raise RuntimeError("should not reach here")

    with (
        patch("scripts.spike_multi_bank_pdf._OUTPUT_ROOT", tmp_path),
        patch("scripts.spike_multi_bank_pdf.download_pdf", side_effect=_mock_download),
    ):
        result = _find_or_download(bank)

    assert result is not None
    found_path, report = result
    assert found_path == old_pdf
    assert report["period_end"] == "2022-12-31"


def test_find_or_download_no_confirmed_returns_none(tmp_path: Path) -> None:
    """_find_or_download returns None when there are no confirmed reports."""
    bank = _make_bank(
        [{"period_end": "2024-06-30", "url": "https://example.com/test.pdf", "status": "pending"}]
    )

    with patch("scripts.spike_multi_bank_pdf._OUTPUT_ROOT", tmp_path):
        result = _find_or_download(bank)

    assert result is None


# ---------------------------------------------------------------------------
# _section_narrative
# ---------------------------------------------------------------------------


def _mock_page(
    text: str = "",
    tables: list | None = None,
    char_count: int | None = None,
) -> MagicMock:
    page = MagicMock()
    page.extract_text.return_value = text or None
    page.extract_tables.return_value = tables or []
    chars = [MagicMock()] * (char_count if char_count is not None else len(text))
    page.chars = chars
    return page


def test_section_narrative_text_readable() -> None:
    """A page with sufficient text is flagged readable_via_text."""
    text = "Income Statement\n" + "Net interest income  1,234\n" * 30
    page = _mock_page(text=text)
    result = _section_narrative(page)
    assert result["readable_via_text"] is True
    assert result["image_based"] is False


def test_section_narrative_image_based() -> None:
    """A page with zero chars and no tables is flagged image_based."""
    page = _mock_page(text="", tables=[], char_count=0)
    result = _section_narrative(page)
    assert result["image_based"] is True


def test_section_narrative_table_summary_captured() -> None:
    """Table rows are captured in first_table_sample."""
    tables = [[["Net interest income", "1,234"], ["Total assets", "5,678"]]]
    page = _mock_page(text="", tables=tables, char_count=0)
    result = _section_narrative(page)
    assert result["table_count"] == 1
    assert result["first_table_sample"][0] == ["Net interest income", "1,234"]


# ---------------------------------------------------------------------------
# main() integration (mocked)
# ---------------------------------------------------------------------------


def test_main_returns_0_on_success(tmp_path: Path) -> None:
    """main() returns 0 even when some banks are skipped."""
    banks = [
        {
            "id": "testbank",
            "reports": [
                {
                    "period_end": "2024-06-30",
                    "url": "https://example.com/test.pdf",
                    "status": "confirmed",
                }
            ],
        }
    ]

    mock_findings = {
        "bank_id": "testbank",
        "period_end": "2024-06-30",
        "source_url": "https://example.com/test.pdf",
        "inspected_at": "2026-01-01T00:00:00+00:00",
        "total_pages": 10,
        "table_page_count": 0,
        "image_page_count": 0,
        "primary_extraction_method": "extract_text",
        "sections": {},
    }

    pdf_path = tmp_path / "testbank" / "testbank-disclosure-2024-06-30.pdf"
    pdf_path.parent.mkdir(parents=True)
    pdf_path.write_bytes(b"%PDF-1.4")

    with (
        patch("scripts.spike_multi_bank_pdf._CONFIG_PATH", tmp_path / "config" / "sources.yaml"),
        patch("scripts.spike_multi_bank_pdf._OUTPUT_ROOT", tmp_path),
        patch("scripts.spike_multi_bank_pdf.load_banks", return_value=banks),
        patch("scripts.spike_multi_bank_pdf.inspect_pdf", return_value=mock_findings),
    ):
        result = main()

    assert result == 0


def test_main_skips_bank_on_inspection_error(tmp_path: Path) -> None:
    """main() logs a warning and skips a bank when inspection raises."""
    banks = [
        {
            "id": "failbank",
            "reports": [
                {
                    "period_end": "2024-06-30",
                    "url": "https://example.com/fail.pdf",
                    "status": "confirmed",
                }
            ],
        }
    ]

    pdf_path = tmp_path / "failbank" / "failbank-disclosure-2024-06-30.pdf"
    pdf_path.parent.mkdir(parents=True)
    pdf_path.write_bytes(b"%PDF-1.4")

    with (
        patch("scripts.spike_multi_bank_pdf._OUTPUT_ROOT", tmp_path),
        patch("scripts.spike_multi_bank_pdf.load_banks", return_value=banks),
        patch(
            "scripts.spike_multi_bank_pdf.inspect_pdf",
            side_effect=RuntimeError("pdfplumber error"),
        ),
    ):
        result = main()

    assert result == 0
    summary_path = tmp_path / "spike_s0004_cross_bank_summary.json"
    assert summary_path.exists()
    summary = json.loads(summary_path.read_text())
    assert "failbank" in summary["banks_skipped"]
