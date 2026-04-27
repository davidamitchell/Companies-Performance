"""Entry-point script for the fetch-data workflow.

Downloads all configured data sources from ``config/sources.yaml`` to their
declared ``output_file`` paths under ``data/raw/``.

For sources that declare a ``discovery_url`` and ``series_match``, the script
first scrapes the RBNZ Data File Index Page to resolve the current download
URL. This is necessary because RBNZ periodically updates their media directory
paths. The ``url`` field in ``sources.yaml`` is used as a fallback only.

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
from src.ingestion.fetch import discover_xlsx_url, download_file
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
        dest = Path(source["output_file"])
        dest.parent.mkdir(parents=True, exist_ok=True)

        # Attempt URL discovery from the RBNZ Data File Index Page.
        # Falls back to the configured url if discovery is not configured or fails.
        url: str = source["url"]
        discovery_url: str | None = source.get("discovery_url")
        series_match: str | None = source.get("series_match")

        if discovery_url and series_match:
            discovered = discover_xlsx_url(discovery_url, series_match)
            if discovered:
                url = discovered
            else:
                logger.warning(
                    "Discovery failed for %r — falling back to configured URL",
                    source["name"],
                )

        try:
            download_file(url, dest, timeout=120.0)
        except (httpx.HTTPError, OSError) as exc:
            logger.error("Failed to fetch %s: %s", url, exc)
            errors += 1

    return errors


if __name__ == "__main__":
    sys.exit(main())
