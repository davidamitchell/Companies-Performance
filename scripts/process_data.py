"""Entry-point script for the process-data workflow.

Parses the RBNZ XLSX, normalises rows into the canonical schema, validates
data quality, and writes:

* ``data/processed/metrics.csv``   — canonical CSV (committed to repo)
* ``docs/data/processed/metrics.json`` — JSON for GitHub Pages frontend

Usage::

    python scripts/process_data.py

Exit code is non-zero on failure.
"""

from __future__ import annotations

import logging
import sys
from pathlib import Path

from src.config import load_metrics, load_sources
from src.logger import get_logger
from src.processing.parse import parse_rbnz_xlsx, write_csv, write_json

logger = get_logger(__name__)

_REPO_ROOT = Path(__file__).parent.parent
_CSV_OUTPUT = _REPO_ROOT / "data" / "processed" / "metrics.csv"
_JSON_OUTPUT = _REPO_ROOT / "docs" / "data" / "processed" / "metrics.json"


def _resolve_xlsx_path(source: dict) -> Path | None:
    """Return the XLSX path to use for processing.

    Prefers ``output_file`` (written by the automated fetch workflow) over
    ``committed_file`` (manually committed for development per ADR-0003).
    Returns ``None`` if neither exists.
    """
    raw_path = Path(source.get("output_file", "")) if source.get("output_file") else None
    committed_path = (
        Path(source.get("committed_file", "")) if source.get("committed_file") else None
    )

    if raw_path and raw_path.exists():
        logger.info("Using fetched XLSX: %s", raw_path)
        return raw_path

    if committed_path and committed_path.exists():
        logger.info("Fetched XLSX not found; using manually committed file: %s", committed_path)
        return committed_path

    return None


def main() -> int:
    """Parse and write processed data.

    Returns
    -------
    int
        Exit code: 0 on success, 1 on failure.
    """
    logging.basicConfig(level=logging.INFO)

    try:
        sources = load_sources()
        metrics_config = load_metrics()
    except (FileNotFoundError, ValueError) as exc:
        logger.error("Failed to load configuration: %s", exc)
        return 1

    rbnz = sources.get("rbnz", {})
    xlsx_sources = rbnz.get("xlsx_sources") or []

    if not xlsx_sources:
        logger.error("No rbnz.xlsx_sources configured in config/sources.yaml")
        return 1

    # Process the first (currently only) RBNZ source
    source = xlsx_sources[0]
    xlsx_path = _resolve_xlsx_path(source)

    if xlsx_path is None:
        logger.error(
            "No XLSX file found.  Run the fetch-data workflow first, "
            "or commit the file manually (see ADR-0003)."
        )
        return 1

    try:
        rows = parse_rbnz_xlsx(xlsx_path, metrics_config)
    except (FileNotFoundError, ValueError) as exc:
        logger.error("Failed to parse XLSX: %s", exc)
        return 1

    if not rows:
        logger.error("No rows produced — check metrics.yaml mappings and XLSX structure")
        return 1

    write_csv(rows, _CSV_OUTPUT)
    write_json(rows, _JSON_OUTPUT)

    logger.info(
        "Processing complete: %d rows written to %s and %s",
        len(rows),
        _CSV_OUTPUT,
        _JSON_OUTPUT,
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
