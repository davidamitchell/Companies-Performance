"""Entry-point script for the fetch-data workflow.

Downloads all configured data sources from ``config/sources.yaml`` to their
declared ``output_file`` paths under ``data/raw/``.

Usage::

    python scripts/fetch_data.py

Exit code is the number of failed downloads (0 = success).
"""

from __future__ import annotations

import logging
import sys
from pathlib import Path

import httpx

from src.config import load_sources
from src.ingestion.fetch import download_file
from src.logger import get_logger

logger = get_logger(__name__)


def main() -> int:
    """Download all configured data sources.

    Returns
    -------
    int
        Number of failed downloads.  0 on full success.
    """
    logging.basicConfig(level=logging.INFO)

    sources = load_sources()
    rbnz = sources.get("rbnz", {})
    errors = 0

    for source in rbnz.get("xlsx_sources", []):
        url: str = source["url"]
        dest = Path(source["output_file"])
        dest.parent.mkdir(parents=True, exist_ok=True)
        try:
            download_file(url, dest, timeout=120.0)
        except (httpx.HTTPError, OSError) as exc:
            logger.error("Failed to fetch %s: %s", url, exc)
            errors += 1

    return errors


if __name__ == "__main__":
    sys.exit(main())
