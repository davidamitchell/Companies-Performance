"""Tests for the ingestion fetch module."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

from src.ingestion.fetch import _DEFAULT_HEADERS, download_file, enforce_canonical_schema


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
