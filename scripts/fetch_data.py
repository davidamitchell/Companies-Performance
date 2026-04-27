"""Entry-point script for the fetch-data workflow.

Downloads all configured data sources from ``config/sources.yaml`` to their
declared ``output_file`` paths under ``data/raw/``.

When a source declares a ``discovery_url``, the script fetches that page first
and extracts the actual XLSX download link from the HTML — this is more robust
than relying on a hardcoded URL that may change.  The hardcoded ``url`` is used
as a fallback if discovery fails.

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
from src.ingestion.fetch import download_file, find_xlsx_url
from src.logger import get_logger

logger = get_logger(__name__)

# Use a real browser User-Agent so servers that block automated clients allow
# the request.  Several New Zealand government sites (including RBNZ) return
# HTTP 403 when the User-Agent is obviously non-browser.
_USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/124.0.0.0 Safari/537.36"
)


def _browser_headers(*, referer: str | None = None) -> dict[str, str]:
    """Return browser-like HTTP request headers.

    Parameters
    ----------
    referer:
        Optional ``Referer`` header value (e.g. the dashboard summary page).
    """
    headers: dict[str, str] = {
        "User-Agent": _USER_AGENT,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
    }
    if referer:
        headers["Referer"] = referer
    return headers


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
        discovery_url: str | None = source.get("discovery_url")
        dest = Path(source["output_file"])
        dest.parent.mkdir(parents=True, exist_ok=True)

        # When a discovery_url is configured, scrape the dashboard page to find
        # the real download link (more robust than a hardcoded URL).
        if discovery_url:
            discovered = find_xlsx_url(discovery_url, headers=_browser_headers())
            if discovered:
                logger.info("Using discovered XLSX URL: %s", discovered)
                url = discovered
            else:
                logger.warning(
                    "Discovery failed for '%s' — falling back to configured URL",
                    source["name"],
                )

        try:
            download_file(
                url,
                dest,
                timeout=120.0,
                headers=_browser_headers(referer=discovery_url),
            )
        except (httpx.HTTPError, OSError) as exc:
            logger.error("Failed to fetch %s: %s", url, exc)
            errors += 1

    return errors


if __name__ == "__main__":
    sys.exit(main())
