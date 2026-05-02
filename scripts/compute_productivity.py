"""Entry-point script for the compute-productivity workflow.

Reads the canonical metrics CSV and reference data files, computes
per-employee and per-customer productivity metrics, and writes:

* ``data/processed/productivity.csv``       — canonical CSV (committed to repo)
* ``docs/data/processed/productivity.json`` — JSON for GitHub Pages frontend

Usage::

    python scripts/compute_productivity.py

Exit code is non-zero on failure.
"""

from __future__ import annotations

import logging
import sys
from pathlib import Path

from src.logger import get_logger
from src.processing.compute_productivity import (
    compute_productivity,
    write_productivity_csv,
    write_productivity_json,
)

logger = get_logger(__name__)

_REPO_ROOT = Path(__file__).parent.parent
_METRICS_CSV = _REPO_ROOT / "data" / "processed" / "metrics.csv"
_EMPLOYEES_CSV = _REPO_ROOT / "data" / "reference" / "employees.csv"
_CUSTOMERS_CSV = _REPO_ROOT / "data" / "reference" / "customers.csv"
_CSV_OUTPUT = _REPO_ROOT / "data" / "processed" / "productivity.csv"
_JSON_OUTPUT = _REPO_ROOT / "docs" / "data" / "processed" / "productivity.json"


def main() -> int:
    """Compute and write productivity metrics.

    Returns
    -------
    int
        Exit code: 0 on success, 1 on failure.
    """
    logging.basicConfig(level=logging.INFO)

    for path in (_METRICS_CSV, _EMPLOYEES_CSV, _CUSTOMERS_CSV):
        if not path.exists():
            logger.error("Required input file not found: %s", path)
            return 1

    try:
        rows = compute_productivity(_METRICS_CSV, _EMPLOYEES_CSV, _CUSTOMERS_CSV)
    except Exception as exc:  # noqa: BLE001
        logger.error("Productivity computation failed: %s", exc)
        return 1

    if not rows:
        logger.warning("No productivity rows produced — check reference data and metrics.csv")
        return 0

    write_productivity_csv(rows, _CSV_OUTPUT)
    write_productivity_json(rows, _JSON_OUTPUT)

    logger.info(
        "Productivity pipeline complete: %d rows written to %s and %s",
        len(rows),
        _CSV_OUTPUT,
        _JSON_OUTPUT,
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
