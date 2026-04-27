"""Fetch raw data files from configured sources.

Ingestion layer responsibility: download files only.

Canonical output schema (one dict per row):
    entity  — institution name (e.g. "ANZ")
    metric  — canonical metric name from glossary (e.g. "CET1 Ratio")
    value   — numeric value
    period  — reporting period string (e.g. "2024-Q3")
    source  — source identifier (e.g. "rbnz-dashboard")

Mapping from raw source column names to this schema is the responsibility of
the processing layer (src/processing/) using mappings declared in
config/metrics.yaml. That mapping cannot be defined until spike S-0001
(RBNZ XLSX structure investigation) is complete.
"""

from __future__ import annotations

import re
from html import unescape
from pathlib import Path
from typing import Any
from urllib.parse import urljoin

import httpx

from src.logger import get_logger

logger = get_logger(__name__)

_CHUNK_SIZE = 65_536  # 64 KB

# Matches href attributes whose value contains ".xlsx" (absolute or relative URLs).
_XLSX_HREF_RE = re.compile(r'href=["\']([^"\']*\.xlsx[^"\']*)["\']', re.IGNORECASE)


def download_file(
    url: str,
    dest: Path,
    *,
    timeout: float = 60.0,
    headers: dict[str, str] | None = None,
) -> Path:
    """Download a file from *url* and save it to *dest*.

    Parameters
    ----------
    url:
        Remote URL to download.
    dest:
        Local file path to write to. Parent directories must exist.
    timeout:
        HTTP request timeout in seconds.
    headers:
        Optional HTTP headers to include in the request (e.g. ``User-Agent``).

    Returns
    -------
    Path
        The path of the saved file.

    Raises
    ------
    httpx.HTTPError
        If the HTTP request fails.
    """
    logger.info("Downloading %s -> %s", url, dest)
    with httpx.stream(
        "GET", url, follow_redirects=True, timeout=timeout, headers=headers or {}
    ) as response:
        response.raise_for_status()
        with dest.open("wb") as fh:
            for chunk in response.iter_bytes(chunk_size=_CHUNK_SIZE):
                fh.write(chunk)
    logger.info("Saved %s (%d bytes)", dest, dest.stat().st_size)
    return dest


def find_xlsx_url(
    page_url: str,
    *,
    timeout: float = 30.0,
    headers: dict[str, str] | None = None,
) -> str | None:
    """Fetch *page_url* and return the first XLSX download link found.

    Scrapes the HTML for ``href`` attributes pointing at ``.xlsx`` files.
    Relative links are resolved against *page_url*.

    Parameters
    ----------
    page_url:
        URL of an HTML page that contains a link to an XLSX file
        (e.g. the RBNZ dashboard summary page).
    timeout:
        HTTP request timeout in seconds.
    headers:
        Optional HTTP headers (e.g. ``User-Agent``) to include in the request.

    Returns
    -------
    str | None
        The first XLSX URL found on the page (resolved to an absolute URL),
        or ``None`` if none is found or the request fails.
    """
    logger.info("Discovering XLSX URL from %s", page_url)
    try:
        response = httpx.get(
            page_url, follow_redirects=True, timeout=timeout, headers=headers or {}
        )
        response.raise_for_status()
    except httpx.HTTPError as exc:
        logger.warning("Could not fetch discovery page %s: %s", page_url, exc)
        return None

    matches = _XLSX_HREF_RE.findall(response.text)
    if not matches:
        logger.warning("No XLSX links found on %s", page_url)
        return None

    link = unescape(matches[0])
    return link if link.startswith(("http://", "https://")) else urljoin(page_url, link)


def enforce_canonical_schema(rows: list[dict[str, Any]], source: str) -> list[dict[str, Any]]:
    """Validate that rows already conform to the canonical schema and stamp the source.

    This function does NOT map from arbitrary column names — that is the job of
    the processing layer (src/processing/) using config/metrics.yaml.

    Parameters
    ----------
    rows:
        Rows that must already use canonical keys:
        ``entity``, ``metric``, ``value``, ``period``.
    source:
        Source identifier to stamp on each output row.

    Returns
    -------
    list[dict]
        Rows that passed validation, with ``source`` added.
        Rows missing ``entity`` or ``metric`` are logged as WARNING and skipped.
    """
    canonical: list[dict[str, Any]] = []
    for row in rows:
        entity = str(row.get("entity") or "").strip()
        metric = str(row.get("metric") or "").strip()
        value = row.get("value")
        period = str(row.get("period") or "").strip()
        if not entity or not metric:
            logger.warning("Skipping row with missing entity or metric: %s", row)
            continue
        canonical.append(
            {
                "entity": entity,
                "metric": metric,
                "value": value,
                "period": period,
                "source": source,
            }
        )
    return canonical
