"""Tests for the ingestion fetch module."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

from src.ingestion.fetch import (
    _DEFAULT_HEADERS,
    discover_xlsx_url,
    download_file,
    enforce_canonical_schema,
)


def test_enforce_canonical_schema_valid_row() -> None:
    rows = [{"entity": "ANZ", "metric": "CET1 Ratio", "value": 13.5, "period": "2024-Q3"}]
    result = enforce_canonical_schema(rows, source="rbnz-dashboard")
    assert len(result) == 1
    row = result[0]
    assert row["entity"] == "ANZ"
    assert row["metric"] == "CET1 Ratio"
    assert row["value"] == 13.5
    assert row["period"] == "2024-Q3"
    assert row["source"] == "rbnz-dashboard"


def test_enforce_canonical_schema_skips_missing_entity() -> None:
    rows = [{"metric": "CET1 Ratio", "value": 13.5, "period": "2024-Q3"}]
    result = enforce_canonical_schema(rows, source="rbnz-dashboard")
    assert result == []


def test_enforce_canonical_schema_skips_missing_metric() -> None:
    rows = [{"entity": "ANZ", "value": 13.5, "period": "2024-Q3"}]
    result = enforce_canonical_schema(rows, source="rbnz-dashboard")
    assert result == []


def test_enforce_canonical_schema_empty_input() -> None:
    assert enforce_canonical_schema([], source="rbnz-dashboard") == []


def test_enforce_canonical_schema_strips_whitespace() -> None:
    rows = [{"entity": "  ASB  ", "metric": " NIM ", "value": 2.1, "period": "2024-Q3"}]
    result = enforce_canonical_schema(rows, source="rbnz-dashboard")
    assert result[0]["entity"] == "ASB"
    assert result[0]["metric"] == "NIM"


def test_enforce_canonical_schema_idempotent() -> None:
    """Running enforce twice on the same input produces the same output."""
    rows = [{"entity": "Westpac", "metric": "NPL Ratio", "value": 0.5, "period": "2024-Q3"}]
    first = enforce_canonical_schema(rows, source="rbnz-dashboard")
    second = enforce_canonical_schema(rows, source="rbnz-dashboard")
    assert first == second


def test_enforce_canonical_schema_does_not_map_arbitrary_keys() -> None:
    """Raw source column names (e.g. 'Bank', 'Metric') are NOT mapped here.
    Column-name mapping is the responsibility of the processing layer
    using config/metrics.yaml (pending spike S-0001).
    """
    rows = [{"Bank": "BNZ", "Metric": "LCR", "Value": 120.0, "Date": "2024-Q3"}]
    result = enforce_canonical_schema(rows, source="rbnz-dashboard")
    assert result == [], "Non-canonical keys must not be silently mapped in the ingestion layer"


def test_download_file_sends_browser_user_agent(tmp_path: Path) -> None:
    """download_file must send a browser User-Agent, not the httpx default."""
    dest = tmp_path / "test.xlsx"
    dest.write_bytes(b"")  # ensure file exists for stat()

    captured_headers: dict[str, str] = {}

    mock_response = MagicMock()
    mock_response.__enter__ = lambda s: s
    mock_response.__exit__ = MagicMock(return_value=False)
    mock_response.iter_bytes.return_value = iter([])
    mock_response.raise_for_status = MagicMock()

    def fake_stream(
        method: str,
        url: str,
        *,
        follow_redirects: bool = False,
        timeout: float = 60.0,
        headers: dict[str, str] | None = None,
    ) -> MagicMock:
        captured_headers.update(headers or {})
        return mock_response

    with patch("src.ingestion.fetch.httpx.stream", side_effect=fake_stream):
        download_file("https://example.com/file.xlsx", dest)

    assert "User-Agent" in captured_headers
    ua = captured_headers["User-Agent"]
    assert not ua.startswith("python-httpx/"), f"Expected browser UA, got: {ua!r}"
    assert "Mozilla" in ua


def test_download_file_custom_headers_merge_and_override(tmp_path: Path) -> None:
    """Custom headers are merged with defaults; custom values win on conflict."""
    dest = tmp_path / "test.xlsx"
    dest.write_bytes(b"")

    captured_headers: dict[str, str] = {}

    mock_response = MagicMock()
    mock_response.__enter__ = lambda s: s
    mock_response.__exit__ = MagicMock(return_value=False)
    mock_response.iter_bytes.return_value = iter([])
    mock_response.raise_for_status = MagicMock()

    def fake_stream(
        method: str,
        url: str,
        *,
        follow_redirects: bool = False,
        timeout: float = 60.0,
        headers: dict[str, str] | None = None,
    ) -> MagicMock:
        captured_headers.update(headers or {})
        return mock_response

    custom_ua = "MyCustomAgent/1.0"
    custom_headers = {"User-Agent": custom_ua, "X-Custom-Header": "custom-value"}

    with patch("src.ingestion.fetch.httpx.stream", side_effect=fake_stream):
        download_file("https://example.com/file.xlsx", dest, headers=custom_headers)

    # Custom User-Agent must win over the default
    assert captured_headers["User-Agent"] == custom_ua
    # Extra custom header must also be present
    assert captured_headers["X-Custom-Header"] == "custom-value"
    # Default headers that are not overridden by custom headers must still be present
    for key, value in _DEFAULT_HEADERS.items():
        if key not in custom_headers:
            assert captured_headers[key] == value


# ---------------------------------------------------------------------------
# discover_xlsx_url
# ---------------------------------------------------------------------------

_INDEX_PAGE_HTML = """
<html><body>
<table>
  <tbody>
    <tr>
      <td>S10</td>
      <td>Bank Financial Strength Dashboard</td>
      <td><a href="/content/dam/website/docs/datafiles/Bank-Financial-Strength-Dashboard-Data.xlsx">XLSX</a></td>
    </tr>
    <tr>
      <td>B1</td>
      <td>Exchange Rates</td>
      <td><a href="/content/dam/website/docs/datafiles/exchange-rates.xlsx">XLSX</a></td>
    </tr>
  </tbody>
</table>
</body></html>
"""

_INDEX_PAGE_URL = "https://www.rbnz.govt.nz/statistics/series/data-file-index-page"


def _mock_get_response(html: str, status_code: int = 200) -> MagicMock:
    """Return a MagicMock that looks like an httpx.Response."""
    mock_resp = MagicMock()
    mock_resp.text = html
    if status_code >= 400:
        import httpx

        mock_resp.raise_for_status.side_effect = httpx.HTTPStatusError(
            f"{status_code}",
            request=MagicMock(),
            response=MagicMock(status_code=status_code),
        )
    else:
        mock_resp.raise_for_status = MagicMock()
    return mock_resp


def test_discover_xlsx_url_returns_url_for_matching_series() -> None:
    """discover_xlsx_url returns the resolved XLSX URL when the series is found."""
    with patch("src.ingestion.fetch.httpx.get", return_value=_mock_get_response(_INDEX_PAGE_HTML)):
        result = discover_xlsx_url(_INDEX_PAGE_URL, "Bank Financial Strength Dashboard")

    assert result == (
        "https://www.rbnz.govt.nz"
        "/content/dam/website/docs/datafiles/Bank-Financial-Strength-Dashboard-Data.xlsx"
    )


def test_discover_xlsx_url_case_insensitive_match() -> None:
    """discover_xlsx_url matches series_match case-insensitively."""
    with patch("src.ingestion.fetch.httpx.get", return_value=_mock_get_response(_INDEX_PAGE_HTML)):
        result = discover_xlsx_url(_INDEX_PAGE_URL, "bank financial strength dashboard")

    assert result is not None
    assert result.endswith(".xlsx")


def test_discover_xlsx_url_returns_none_when_series_not_found() -> None:
    """discover_xlsx_url returns None when the series text is not in the page."""
    with patch("src.ingestion.fetch.httpx.get", return_value=_mock_get_response(_INDEX_PAGE_HTML)):
        result = discover_xlsx_url(_INDEX_PAGE_URL, "Nonexistent Series XYZ")

    assert result is None


def test_discover_xlsx_url_returns_none_on_http_error() -> None:
    """discover_xlsx_url returns None (not raises) when the index page returns an error."""
    with patch(
        "src.ingestion.fetch.httpx.get", return_value=_mock_get_response("", status_code=403)
    ):
        result = discover_xlsx_url(_INDEX_PAGE_URL, "Bank Financial Strength Dashboard")

    assert result is None


def test_discover_xlsx_url_resolves_relative_urls() -> None:
    """discover_xlsx_url resolves relative hrefs against the index page URL."""
    html = """<table><tr><td>Dashboard</td>
    <td><a href="/data/file.xlsx">Download</a></td></tr></table>"""
    with patch("src.ingestion.fetch.httpx.get", return_value=_mock_get_response(html)):
        result = discover_xlsx_url("https://example.com/index", "Dashboard")

    assert result == "https://example.com/data/file.xlsx"


def test_discover_xlsx_url_returns_none_on_network_error() -> None:
    """discover_xlsx_url returns None when a network-level error occurs."""
    import httpx

    with patch(
        "src.ingestion.fetch.httpx.get",
        side_effect=httpx.ConnectError("connection refused"),
    ):
        result = discover_xlsx_url(_INDEX_PAGE_URL, "Bank Financial Strength Dashboard")

    assert result is None
