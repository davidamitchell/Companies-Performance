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

from pathlib import Path
from typing import Any

import httpx

from src.logger import get_logger

logger = get_logger(__name__)

_CHUNK_SIZE = 65_536  # 64 KB

_DEFAULT_HEADERS: dict[str, str] = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
}


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
        Additional HTTP headers to send with the request. These are merged with
        ``_DEFAULT_HEADERS`` (which sets a browser-like User-Agent). Values
        provided here take precedence over the defaults.

    Returns
    -------
    Path
        The path of the saved file.

    Raises
    ------
    httpx.HTTPError
        If the HTTP request fails.
    """
    effective_headers = {**_DEFAULT_HEADERS, **(headers or {})}
    logger.info("Downloading %s -> %s", url, dest)
    with httpx.stream(
        "GET", url, follow_redirects=True, timeout=timeout, headers=effective_headers
    ) as response:
        response.raise_for_status()
        with dest.open("wb") as fh:
            for chunk in response.iter_bytes(chunk_size=_CHUNK_SIZE):
                fh.write(chunk)
    logger.info("Saved %s (%d bytes)", dest, dest.stat().st_size)
    return dest


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
