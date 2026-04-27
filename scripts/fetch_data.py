"""Fetch all configured data sources and write them to data/raw/.

Usage:
    python scripts/fetch_data.py

Reads source definitions from config/sources.yaml and downloads each XLSX
file using :func:`src.ingestion.fetch.download_file`. Idempotent — re-running
overwrites the existing file with the latest version.
"""

from __future__ import annotations

import logging
import sys
from pathlib import Path

from src.config import load_sources
from src.ingestion.fetch import download_file
from src.logger import get_logger

logger = get_logger(__name__)


def fetch_all_sources() -> int:
    """Download every configured source.

    Returns
    -------
    int
        0 on success, 1 if any download failed.
    """
    sources = load_sources()
    rbnz = sources.get("rbnz", {})
    failed = 0
    for source in rbnz.get("xlsx_sources", []):
        url: str = source["url"]
        dest = Path(source["output_file"])
        dest.parent.mkdir(parents=True, exist_ok=True)
        try:
            download_file(url, dest, timeout=120.0)
        except Exception as exc:
            logger.error("Failed to download %s: %s", url, exc)
            failed += 1
    return 1 if failed else 0


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    sys.exit(fetch_all_sources())
