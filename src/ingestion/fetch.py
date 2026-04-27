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

from html.parser import HTMLParser
from pathlib import Path
from typing import Any
from urllib.parse import urljoin

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


class _IndexPageParser(HTMLParser):
    """Parse an HTML page and collect (row_text, xlsx_hrefs) for each table row.

    Each entry in ``rows`` is a tuple of:
    - row_text: whitespace-joined text content of all ``<td>`` cells in the row.
    - xlsx_hrefs: list of href values from ``<a>`` tags in the row whose href
      ends with ``.xlsx`` (case-insensitive).
    """

    def __init__(self) -> None:
        super().__init__()
        self._in_tr = False
        self._in_cell = False  # inside <td> or <th>
        self._current_text: list[str] = []
        self._current_links: list[str] = []
        self.rows: list[tuple[str, list[str]]] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag == "tr":
            self._in_tr = True
            self._current_text = []
            self._current_links = []
        elif tag in ("td", "th"):
            self._in_cell = True
        elif tag == "a":
            attrs_dict = dict(attrs)
            href = attrs_dict.get("href") or ""
            if href.lower().endswith(".xlsx"):
                self._current_links.append(href)

    def handle_endtag(self, tag: str) -> None:
        if tag == "tr" and self._in_tr:
            self.rows.append((" ".join(self._current_text), list(self._current_links)))
            self._in_tr = False
            self._current_text = []
            self._current_links = []
        elif tag in ("td", "th"):
            self._in_cell = False

    def handle_data(self, data: str) -> None:
        if self._in_cell:
            stripped = data.strip()
            if stripped:
                self._current_text.append(stripped)


def discover_xlsx_url(
    index_page_url: str,
    series_match: str,
    *,
    timeout: float = 30.0,
) -> str | None:
    """Fetch the RBNZ Data File Index Page and return the XLSX URL for a series.

    Scrapes ``index_page_url`` looking for a table row whose text contains
    ``series_match`` (case-insensitive) and that includes an ``.xlsx`` link.
    Relative href values are resolved against ``index_page_url``.

    Parameters
    ----------
    index_page_url:
        URL of the RBNZ Data File Index Page.
    series_match:
        Text to search for in the page table rows. Matched case-insensitively.
    timeout:
        HTTP request timeout in seconds.

    Returns
    -------
    str | None
        Discovered XLSX URL, or ``None`` if not found or if the page cannot
        be fetched.
    """
    try:
        response = httpx.get(
            index_page_url,
            follow_redirects=True,
            timeout=timeout,
            headers=_DEFAULT_HEADERS,
        )
        response.raise_for_status()
    except httpx.HTTPError as exc:
        logger.warning("Could not fetch discovery page %s: %s", index_page_url, exc)
        return None

    parser = _IndexPageParser()
    parser.feed(response.text)

    match_lower = series_match.lower()
    for row_text, xlsx_hrefs in parser.rows:
        if match_lower in row_text.lower() and xlsx_hrefs:
            resolved = urljoin(index_page_url, xlsx_hrefs[0])
            logger.info("Discovered URL for %r: %s", series_match, resolved)
            return resolved

    logger.warning("Series %r not found on discovery page %s", series_match, index_page_url)
    return None


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
        Additional HTTP headers to send with the request.  These are merged
        with ``_DEFAULT_HEADERS``; values supplied here take precedence over
        the defaults.

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
