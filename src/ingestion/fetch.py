"""Fetch raw data files from configured sources.

Canonical output schema (one dict per row):
    entity  — institution name (e.g. "ANZ")
    metric  — canonical metric name from glossary (e.g. "CET1 Ratio")
    value   — numeric value
    period  — reporting period string (e.g. "2024-Q3")
    source  — source identifier (e.g. "rbnz-dashboard")
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import httpx

from src.logger import get_logger

logger = get_logger(__name__)

_CHUNK_SIZE = 65_536  # 64 KB


def download_file(url: str, dest: Path, *, timeout: float = 60.0) -> Path:
    """Download a file from *url* and save it to *dest*.

    Parameters
    ----------
    url:
        Remote URL to download.
    dest:
        Local file path to write to. Parent directories must exist.
    timeout:
        HTTP request timeout in seconds.

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
    with httpx.stream("GET", url, follow_redirects=True, timeout=timeout) as response:
        response.raise_for_status()
        with dest.open("wb") as fh:
            for chunk in response.iter_bytes(chunk_size=_CHUNK_SIZE):
                fh.write(chunk)
    logger.info("Saved %s (%d bytes)", dest, dest.stat().st_size)
    return dest


def parse_canonical_rows(raw_rows: list[dict[str, Any]], source: str) -> list[dict[str, Any]]:
    """Normalise a list of raw row dicts into the canonical schema.

    Parameters
    ----------
    raw_rows:
        Rows extracted from the source file, each with arbitrary keys.
    source:
        Source identifier to stamp on each output row.

    Returns
    -------
    list[dict]
        Rows conforming to the canonical schema:
        ``entity | metric | value | period | source``.
    """
    canonical: list[dict[str, Any]] = []
    for row in raw_rows:
        entity = row.get("entity") or row.get("Bank") or row.get("Institution") or ""
        metric = row.get("metric") or row.get("Metric") or row.get("Indicator") or ""
        value = row.get("value") or row.get("Value")
        period = row.get("period") or row.get("Period") or row.get("Date") or ""
        if not entity or not metric:
            logger.warning("Skipping row with missing entity or metric: %s", row)
            continue
        canonical.append(
            {
                "entity": str(entity).strip(),
                "metric": str(metric).strip(),
                "value": value,
                "period": str(period).strip(),
                "source": source,
            }
        )
    return canonical
