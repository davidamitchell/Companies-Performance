"""Spike script: inspect disclosure statement PDFs across all 6 NZ banks.

Downloads the most recent confirmed disclosure statement PDF for each bank
configured in ``config/sources.yaml`` and inspects each with pdfplumber to
determine:

- Total page count and machine-readability method (tables vs text)
- Which pages hold each key financial statement section
- Narrative text summary of each section (Income Statement, Balance Sheet,
  Cash Flow Statement, Capital Adequacy)
- Whether any pages are image-based (no extractable text or tables)

Per-bank findings are saved under
``data/raw/financial_disclosures/<bank_id>/spike_s0004_multi_findings.json``.
A consolidated cross-bank summary is saved to
``data/raw/financial_disclosures/spike_s0004_cross_bank_summary.json``.

Usage::

    python scripts/spike_multi_bank_pdf.py

Network access failures are logged as WARNING and the bank is skipped;
the script continues to remaining banks and always exits 0.
"""

from __future__ import annotations

import json
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import pdfplumber
import requests
import yaml

from src.logger import get_logger

logger = get_logger(__name__)

_USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/124.0.0.0 Safari/537.36"
)
_CONFIG_PATH = Path("config/sources.yaml")
_OUTPUT_ROOT = Path("data/raw/financial_disclosures")
_DOWNLOAD_TIMEOUT = 180

# Financial section keyword patterns for section detection
_SECTION_KEYWORDS: dict[str, list[str]] = {
    "Income Statement": [
        "income statement",
        "statement of comprehensive income",
        "profit or loss",
    ],
    "Balance Sheet": [
        "statement of financial position",
        "balance sheet",
    ],
    "Cash Flow Statement": [
        "cash flow statement",
        "statement of cash flows",
    ],
    "Capital Adequacy": [
        "capital adequacy",
    ],
}

# Minimum character threshold to treat a page as machine-readable
_MIN_CHARS_TEXT = 200


def load_banks() -> list[dict[str, Any]]:
    """Return bank configs from ``config/sources.yaml``."""
    with _CONFIG_PATH.open(encoding="utf-8") as fh:
        cfg = yaml.safe_load(fh)
    return cfg["financial_disclosures"]["banks"]


def _find_or_download(
    bank: dict[str, Any],
) -> tuple[Path, dict[str, Any]] | None:
    """Return ``(pdf_path, report)`` for the first usable PDF for *bank*.

    Tries confirmed reports newest-first.  A report is "usable" if its PDF is
    already present locally or can be downloaded successfully.  Returns
    ``None`` if no usable report is found.
    """
    bank_id = bank["id"]
    confirmed = sorted(
        [r for r in bank.get("reports", []) if r.get("status") == "confirmed"],
        key=lambda r: r["period_end"],
        reverse=True,
    )
    for report in confirmed:
        period_end = str(report["period_end"])
        url = report["url"]
        safe_id = period_end.replace("/", "-")
        pdf_path = _OUTPUT_ROOT / bank_id / f"{bank_id}-disclosure-{safe_id}.pdf"

        if pdf_path.exists():
            logger.info("%s: PDF already at %s — skipping download", bank_id, pdf_path)
            return pdf_path, report

        try:
            download_pdf(url, pdf_path)
            return pdf_path, report
        except Exception as exc:
            logger.warning(
                "%s: download failed for %s (%s) — trying older report",
                bank_id,
                period_end,
                exc,
            )
    return None


def download_pdf(url: str, dest: Path) -> None:
    """Download *url* to *dest* using a browser User-Agent.

    Raises
    ------
    RuntimeError
        On HTTP error.
    requests.exceptions.RequestException
        On network failure.
    """
    logger.info("Downloading %s", url)
    session = requests.Session()
    session.headers.update({"User-Agent": _USER_AGENT})
    response = session.get(url, timeout=_DOWNLOAD_TIMEOUT, stream=True)
    if response.status_code != 200:
        raise RuntimeError(f"HTTP {response.status_code} for {url}")
    dest.parent.mkdir(parents=True, exist_ok=True)
    with dest.open("wb") as fh:
        for chunk in response.iter_content(chunk_size=65536):
            fh.write(chunk)
    logger.info("Saved %d bytes to %s", dest.stat().st_size, dest)


def _is_toc_page(text: str) -> bool:
    """Return True if *text* looks like a table of contents page.

    A TOC typically mentions multiple section keywords in short succession and
    has a high ratio of page-number tokens (short numbers at end of lines).
    """
    text_lower = text.lower()
    kw_hits = sum(
        1 for keywords in _SECTION_KEYWORDS.values() if any(kw in text_lower for kw in keywords)
    )
    # If 3+ distinct section types are mentioned it is almost certainly a TOC
    return kw_hits >= 3


def _find_section_pages(pdf: pdfplumber.PDF) -> dict[str, list[int]]:
    """Scan all pages and return page numbers (1-based) for each section.

    Skips table-of-contents pages and prefers pages where the section keyword
    appears in the first 400 characters (i.e., as a page heading).
    """
    found: dict[str, list[int]] = {s: [] for s in _SECTION_KEYWORDS}
    for page_num, page in enumerate(pdf.pages, start=1):
        text = page.extract_text() or ""
        text_lower = text.lower()
        if _is_toc_page(text):
            continue
        for section, keywords in _SECTION_KEYWORDS.items():
            if any(kw in text_lower for kw in keywords):
                found[section].append(page_num)
    return found


def _section_narrative(page: pdfplumber.page.PageBase) -> dict[str, Any]:
    """Return narrative summary data for a single *page*."""
    text = page.extract_text() or ""
    tables = page.extract_tables()
    char_count = len(page.chars)

    image_based = char_count == 0 and not tables
    readable_via_tables = bool(tables) and not text.strip()
    readable_via_text = len(text) >= _MIN_CHARS_TEXT

    # Collect table summary (first table, up to 10 rows)
    table_summary: list[list[str]] = []
    table_dims: list[str] = []
    for tbl in tables:
        table_dims.append(f"{len(tbl)}r x {len(tbl[0]) if tbl else 0}c")
        if not table_summary:
            table_summary = [[str(cell) if cell else "" for cell in row] for row in tbl[:10]]

    return {
        "char_count": char_count,
        "image_based": image_based,
        "readable_via_tables": readable_via_tables,
        "readable_via_text": readable_via_text,
        "table_count": len(tables),
        "table_dims": table_dims,
        "first_table_sample": table_summary,
        "text_sample": text[:1200],
    }


def inspect_pdf(
    pdf_path: Path,
    source_url: str,
    bank_id: str,
    period_end: str,
) -> dict[str, Any]:
    """Inspect *pdf_path* and return structured findings."""
    logger.info("Inspecting %s (%s %s)", bank_id, period_end, pdf_path)

    try:
        pdf = pdfplumber.open(pdf_path)
    except Exception as exc:
        raise RuntimeError(f"pdfplumber cannot open {pdf_path}: {exc}") from exc

    with pdf:
        total_pages = len(pdf.pages)
        logger.info("%s: %d pages", bank_id, total_pages)

        # Count tables and image-based pages
        table_page_count = 0
        image_page_count = 0
        for page in pdf.pages:
            has_text = len(page.chars) >= _MIN_CHARS_TEXT
            has_tables = bool(page.extract_tables())
            if has_tables:
                table_page_count += 1
            if not has_text and not has_tables:
                image_page_count += 1

        section_pages = _find_section_pages(pdf)
        logger.info("%s: sections found: %s", bank_id, list(section_pages.keys()))

        # Build narrative per section
        section_narratives: dict[str, Any] = {}
        for section, pages in section_pages.items():
            if not pages:
                logger.warning("%s: section '%s' not found", bank_id, section)
                section_narratives[section] = {"found": False}
                continue

            # Prefer the first page where the keyword appears near the top
            # (section heading) rather than buried in notes text.
            keywords = _SECTION_KEYWORDS[section]
            best_page_num = pages[0]
            for pg_num in pages:
                page_text = pdf.pages[pg_num - 1].extract_text() or ""
                page_top = page_text[:400].lower()
                if any(kw in page_top for kw in keywords):
                    best_page_num = pg_num
                    break

            logger.info("%s: '%s' -> p%d", bank_id, section, best_page_num)
            narrative = _section_narrative(pdf.pages[best_page_num - 1])
            narrative["page"] = best_page_num
            narrative["all_pages"] = pages
            narrative["found"] = True
            section_narratives[section] = narrative

    return {
        "bank_id": bank_id,
        "period_end": period_end,
        "source_url": source_url,
        "inspected_at": datetime.now(tz=UTC).isoformat(),
        "total_pages": total_pages,
        "table_page_count": table_page_count,
        "image_page_count": image_page_count,
        "primary_extraction_method": (
            "extract_tables" if table_page_count > total_pages // 2 else "extract_text"
        ),
        "sections": section_narratives,
    }


def log_bank_summary(findings: dict[str, Any]) -> None:
    """Log a human-readable summary for one bank's findings."""
    logger.info(
        "--- %s (%s) | %d pages | %d table-pages | %d image-pages | method: %s ---",
        findings["bank_id"],
        findings["period_end"],
        findings["total_pages"],
        findings["table_page_count"],
        findings["image_page_count"],
        findings["primary_extraction_method"],
    )
    for section, info in findings["sections"].items():
        if not info.get("found"):
            logger.warning("  [%s]: NOT FOUND", section)
            continue
        pg = info["page"]
        image = " [IMAGE-BASED]" if info.get("image_based") else ""
        via = "tables" if info.get("readable_via_tables") else "text"
        logger.info("  [%s] p%d via %s%s", section, pg, via, image)


def main() -> int:
    """Run the multi-bank spike."""
    import logging

    logging.basicConfig(level=logging.INFO)

    banks = load_banks()
    all_findings: list[dict[str, Any]] = []
    skipped: list[str] = []

    for bank in banks:
        bank_id = bank["id"]

        result = _find_or_download(bank)
        if result is None:
            logger.warning("%s: no usable PDF found — skipping", bank_id)
            skipped.append(bank_id)
            continue

        pdf_path, report = result
        period_end = str(report["period_end"])
        url = report["url"]

        # Inspect
        try:
            findings = inspect_pdf(pdf_path, url, bank_id, period_end)
        except Exception as exc:
            logger.warning("%s: inspection failed (%s) — skipping", bank_id, exc)
            skipped.append(bank_id)
            continue

        log_bank_summary(findings)
        all_findings.append(findings)

        # Write per-bank findings
        per_bank_path = _OUTPUT_ROOT / bank_id / "spike_s0004_multi_findings.json"
        per_bank_path.parent.mkdir(parents=True, exist_ok=True)
        per_bank_path.write_text(json.dumps(findings, indent=2), encoding="utf-8")
        logger.info("%s: findings saved to %s", bank_id, per_bank_path)

    # Cross-bank summary
    summary = {
        "generated_at": datetime.now(tz=UTC).isoformat(),
        "banks_inspected": [f["bank_id"] for f in all_findings],
        "banks_skipped": skipped,
        "findings": all_findings,
    }
    summary_path = _OUTPUT_ROOT / "spike_s0004_cross_bank_summary.json"
    summary_path.parent.mkdir(parents=True, exist_ok=True)
    summary_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    logger.info("Cross-bank summary saved to %s", summary_path)
    logger.info(
        "Done: %d banks inspected, %d skipped",
        len(all_findings),
        len(skipped),
    )

    return 0


if __name__ == "__main__":
    sys.exit(main())
