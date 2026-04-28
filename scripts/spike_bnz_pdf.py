"""Spike script: inspect the BNZ September 2024 disclosure statement PDF.

Downloads the BNZ full-year 2024 disclosure statement and inspects it with
pdfplumber to determine:

- Total page count
- Which pages contain tables and how many tables per page
- A sample of the first table found

Findings are saved to
``data/raw/financial_disclosures/bnz/spike_s0004_bnz_findings.json``.

Usage::

    python scripts/spike_bnz_pdf.py

Raises an exception on download failure or if pdfplumber cannot open the file.
"""

from __future__ import annotations

import json
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import pdfplumber
import requests

from src.logger import get_logger

logger = get_logger(__name__)

_USER_AGENT = "Companies-Performance/1.0 (github.com/davidamitchell/Companies-Performance)"
_SOURCE_URL = "https://www.bnz.co.nz/assets/about-us/financials/pdfs/bnz-disclosure-statement-year-ended-30-september-2024.pdf"
_OUTPUT_DIR = Path("data/raw/financial_disclosures/bnz")
_PDF_PATH = _OUTPUT_DIR / "bnz-disclosure-statement-2024-09-30.pdf"
_FINDINGS_PATH = _OUTPUT_DIR / "spike_s0004_bnz_findings.json"
_DOWNLOAD_TIMEOUT = 120


def download_pdf(url: str, dest: Path) -> None:
    """Download a PDF from *url* to *dest*.

    Raises
    ------
    RuntimeError
        If the server returns a non-200 status code.
    OSError
        On network-level failure (propagated from requests).
    """
    logger.info("Downloading %s → %s", url, dest)
    session = requests.Session()
    session.headers.update({"User-Agent": _USER_AGENT})

    response = session.get(url, timeout=_DOWNLOAD_TIMEOUT, stream=True)
    if response.status_code != 200:
        raise RuntimeError(f"Download failed: HTTP {response.status_code} for {url}")

    dest.parent.mkdir(parents=True, exist_ok=True)
    with dest.open("wb") as fh:
        for chunk in response.iter_content(chunk_size=65536):
            fh.write(chunk)

    logger.info("Saved %d bytes to %s", dest.stat().st_size, dest)


def inspect_pdf(path: Path) -> dict[str, Any]:
    """Inspect *path* with pdfplumber and return structured findings.

    Raises
    ------
    RuntimeError
        If pdfplumber cannot open the file.
    """
    logger.info("Inspecting PDF: %s", path)

    try:
        pdf = pdfplumber.open(path)
    except Exception as exc:
        raise RuntimeError(f"pdfplumber could not open {path}: {exc}") from exc

    with pdf:
        total_pages = len(pdf.pages)
        pages_with_tables: list[int] = []
        total_tables_found = 0
        first_table_page: int | None = None
        first_table_rows: list[list[Any]] = []

        for page_number, page in enumerate(pdf.pages, start=1):
            tables = page.extract_tables()
            if tables:
                pages_with_tables.append(page_number)
                total_tables_found += len(tables)
                logger.info("Page %d: %d table(s) detected", page_number, len(tables))
                if first_table_page is None:
                    first_table_page = page_number
                    first_table_rows = tables[0]
                    logger.info(
                        "First table on page %d — %d rows × %d cols",
                        page_number,
                        len(first_table_rows),
                        len(first_table_rows[0]) if first_table_rows else 0,
                    )
            else:
                logger.info("Page %d: no tables", page_number)

    first_table_row_count = len(first_table_rows) if first_table_rows else 0
    first_table_col_count = len(first_table_rows[0]) if first_table_rows else 0
    sample: list[list[Any]] = first_table_rows[:5] if first_table_rows else []

    return {
        "source_url": _SOURCE_URL,
        "downloaded_at": datetime.now(tz=UTC).isoformat(),
        "total_pages": total_pages,
        "pages_with_tables": pages_with_tables,
        "total_tables_found": total_tables_found,
        "first_table_page": first_table_page,
        "first_table_row_count": first_table_row_count,
        "first_table_column_count": first_table_col_count,
        "first_table_sample": sample,
    }


def print_summary(findings: dict[str, Any]) -> None:
    """Print a human-readable summary of the findings."""
    print("\n=== BNZ PDF Spike Findings ===")
    print(f"Source URL : {findings['source_url']}")
    print(f"Total pages: {findings['total_pages']}")
    print(
        f"Tables found: {findings['total_tables_found']} across {len(findings['pages_with_tables'])} page(s)"
    )
    print(f"Pages with tables: {findings['pages_with_tables']}")

    if findings["first_table_page"] is not None:
        print(
            f"\nFirst table on page {findings['first_table_page']} "
            f"({findings['first_table_row_count']} rows × {findings['first_table_column_count']} cols)"
        )
        print("\nFirst 5 rows:")
        for row in findings["first_table_sample"]:
            print("  " + " | ".join(str(cell) for cell in row))


def main() -> int:
    """Run the spike: download, inspect, save findings."""
    import logging

    logging.basicConfig(level=logging.INFO)

    if not _PDF_PATH.exists():
        download_pdf(_SOURCE_URL, _PDF_PATH)
    else:
        logger.info("PDF already present at %s — skipping download", _PDF_PATH)

    findings = inspect_pdf(_PDF_PATH)
    print_summary(findings)

    _FINDINGS_PATH.parent.mkdir(parents=True, exist_ok=True)
    _FINDINGS_PATH.write_text(json.dumps(findings, indent=2), encoding="utf-8")
    logger.info("Findings saved to %s", _FINDINGS_PATH)

    return 0


if __name__ == "__main__":
    sys.exit(main())
