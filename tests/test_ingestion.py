"""Tests for the ingestion fetch module."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import httpx

from src.ingestion.fetch import enforce_canonical_schema, find_xlsx_url


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


# ---------------------------------------------------------------------------
# find_xlsx_url tests
# ---------------------------------------------------------------------------


def _mock_response(html: str, status_code: int = 200) -> MagicMock:
    """Return a mock httpx.Response with the given HTML body."""
    resp = MagicMock()
    resp.text = html
    resp.raise_for_status = MagicMock()
    if status_code >= 400:
        resp.raise_for_status.side_effect = httpx.HTTPStatusError(
            message=f"HTTP {status_code}",
            request=MagicMock(),
            response=MagicMock(status_code=status_code),
        )
    return resp


def test_find_xlsx_url_returns_absolute_link() -> None:
    """Returns the absolute XLSX URL when the page contains one."""
    html = '<a href="https://example.com/data.xlsx">Download</a>'
    with patch("src.ingestion.fetch.httpx.get", return_value=_mock_response(html)):
        result = find_xlsx_url("https://example.com/summary")
    assert result == "https://example.com/data.xlsx"


def test_find_xlsx_url_resolves_relative_link() -> None:
    """Resolves relative XLSX hrefs against the page URL."""
    html = '<a href="/datafiles/report.xlsx">Download</a>'
    with patch("src.ingestion.fetch.httpx.get", return_value=_mock_response(html)):
        result = find_xlsx_url("https://example.com/summary")
    assert result == "https://example.com/datafiles/report.xlsx"


def test_find_xlsx_url_returns_none_when_no_xlsx_link() -> None:
    """Returns None when the page contains no XLSX links."""
    html = "<html><body><a href='/page'>No Excel here</a></body></html>"
    with patch("src.ingestion.fetch.httpx.get", return_value=_mock_response(html)):
        result = find_xlsx_url("https://example.com/summary")
    assert result is None


def test_find_xlsx_url_returns_none_on_http_error() -> None:
    """Returns None (with a WARNING) when the discovery page cannot be fetched."""
    with patch(
        "src.ingestion.fetch.httpx.get",
        side_effect=httpx.RequestError("connection refused"),
    ):
        result = find_xlsx_url("https://example.com/summary")
    assert result is None


def test_find_xlsx_url_returns_first_match() -> None:
    """Returns the first XLSX link when the page has several."""
    html = (
        '<a href="https://example.com/first.xlsx">First</a>'
        '<a href="https://example.com/second.xlsx">Second</a>'
    )
    with patch("src.ingestion.fetch.httpx.get", return_value=_mock_response(html)):
        result = find_xlsx_url("https://example.com/summary")
    assert result == "https://example.com/first.xlsx"


def test_find_xlsx_url_handles_single_quoted_href() -> None:
    """find_xlsx_url works with single-quoted href attributes."""
    html = "<a href='/files/data.xlsx'>Download</a>"
    with patch("src.ingestion.fetch.httpx.get", return_value=_mock_response(html)):
        result = find_xlsx_url("https://example.com/summary")
    assert result == "https://example.com/files/data.xlsx"


def test_find_xlsx_url_handles_query_params() -> None:
    """Returns the full URL with decoded query parameters."""
    html = '<a href="https://example.com/data.xlsx?v=3&amp;format=full">Download</a>'
    with patch("src.ingestion.fetch.httpx.get", return_value=_mock_response(html)):
        result = find_xlsx_url("https://example.com/summary")
    assert result == "https://example.com/data.xlsx?v=3&format=full"
