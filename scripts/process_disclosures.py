"""Entry-point script for the process-disclosures workflow.

Extracts quantitative metrics from bank disclosure PDFs, then writes:

* ``data/processed/disclosures.csv``        — canonical CSV (committed to repo)
* ``docs/data/processed/disclosures.json``  — JSON for GitHub Pages frontend

Usage::

    python scripts/process_disclosures.py

Exit code is non-zero on failure.
"""

from __future__ import annotations

import csv
import json
import logging
import sys
from pathlib import Path

from src.config import load_sources
from src.logger import get_logger
from src.processing.extract_disclosures import extract_disclosures

logger = get_logger(__name__)

_REPO_ROOT = Path(__file__).parent.parent
_RAW_DISCLOSURES_DIR = _REPO_ROOT / "data" / "raw" / "financial_disclosures"
_CSV_OUTPUT = _REPO_ROOT / "data" / "processed" / "disclosures.csv"
_JSON_OUTPUT = _REPO_ROOT / "docs" / "data" / "processed" / "disclosures.json"

_FIELDNAMES = ["entity", "metric", "value", "period", "source"]


def main() -> int:
    """Extract disclosure metrics and write processed data.

    Returns
    -------
    int
        Exit code: 0 on success, 1 on failure.
    """
    logging.basicConfig(level=logging.INFO)

    try:
        sources = load_sources()
    except (FileNotFoundError, ValueError) as exc:
        logger.error("Failed to load configuration: %s", exc)
        return 1

    if not _RAW_DISCLOSURES_DIR.exists():
        logger.error("Disclosures directory not found: %s", _RAW_DISCLOSURES_DIR)
        return 1

    rows = extract_disclosures(_RAW_DISCLOSURES_DIR, sources)

    if not rows:
        logger.warning(
            "No rows extracted — check that PDFs have .meta.json sidecars "
            "and that pdfplumber can read them."
        )
        # Not a hard failure: write empty output files so idempotency is maintained
    else:
        # Log per-bank counts
        counts: dict[str, int] = {}
        for row in rows:
            src = row.get("source", "unknown")
            counts[src] = counts.get(src, 0) + 1
        for src, count in sorted(counts.items()):
            logger.info("  %s: %d rows", src, count)

    _write_csv(rows, _CSV_OUTPUT)
    _write_json(rows, _JSON_OUTPUT)

    logger.info(
        "Processing complete: %d rows written to %s and %s",
        len(rows),
        _CSV_OUTPUT,
        _JSON_OUTPUT,
    )
    return 0


def _write_csv(rows: list[dict], dest: Path) -> None:
    """Write canonical rows to CSV, overwriting any existing file."""
    dest.parent.mkdir(parents=True, exist_ok=True)
    with dest.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=_FIELDNAMES, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)
    logger.info("Wrote %d rows to %s", len(rows), dest)


def _write_json(rows: list[dict], dest: Path) -> None:
    """Write canonical rows to JSON, overwriting any existing file."""
    dest.parent.mkdir(parents=True, exist_ok=True)
    with dest.open("w", encoding="utf-8") as fh:
        json.dump(rows, fh)
    logger.info("Wrote %d rows to %s", len(rows), dest)


if __name__ == "__main__":
    sys.exit(main())
