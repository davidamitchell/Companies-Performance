"""Entry-point script for the process-ocr workflow.

Parses the RBNZ B2 Official Cash Rate XLSX, converts monthly observations
to quarterly, and writes:

* ``data/processed/ocr.csv``        — canonical CSV (committed to repo)
* ``docs/data/processed/ocr.json``  — JSON for GitHub Pages frontend

Usage::

    python scripts/process_ocr.py

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
from src.processing.parse_ocr import parse_ocr

logger = get_logger(__name__)

_REPO_ROOT = Path(__file__).parent.parent
_CSV_OUTPUT = _REPO_ROOT / "data" / "processed" / "ocr.csv"
_JSON_OUTPUT = _REPO_ROOT / "docs" / "data" / "processed" / "ocr.json"

_FIELDNAMES = ["entity", "metric", "value", "period", "source"]


def main() -> int:
    """Parse OCR XLSX and write processed data.

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

    raw_dir = _REPO_ROOT / "data" / "raw"

    try:
        rows = parse_ocr(sources_config=sources, raw_dir=raw_dir)
    except FileNotFoundError as exc:
        logger.error("OCR XLSX not found: %s", exc)
        return 1
    except ValueError as exc:
        logger.error("Failed to parse OCR XLSX: %s", exc)
        return 1

    if not rows:
        logger.warning("No OCR rows extracted — check the XLSX structure.")
        return 1

    logger.info("Extracted %d quarterly OCR rows", len(rows))

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
