"""Tests for the ingestion fetch module."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

from src.ingestion.fetch import _DEFAULT_HEADERS, download_file, enforce_canonical_schema


def _make_mock_stream(content: bytes = b"data") -> MagicMock:
    """Return a mock context manager that mimics httpx.stream()."""
    mock_response = MagicMock()
    mock_response.raise_for_status = MagicMock()
    mock_response.iter_bytes.return_value = [content]
    mock_cm = MagicMock()
    mock_cm.__enter__ = MagicMock(return_value=mock_response)
    mock_cm.__exit__ = MagicMock(return_value=False)
    return mock_cm


def test_download_file_sends_browser_user_agent(tmp_path: Path) -> None:
    """download_file sends a browser-like User-Agent instead of the default httpx User-Agent."""
    dest = tmp_path / "file.xlsx"
    captured: dict[str, object] = {}

    def fake_stream(
        method: str,
        url: str,
        *,
        follow_redirects: bool,
        timeout: float,
        headers: dict[str, str],
    ) -> MagicMock:
        captured["headers"] = headers
        return _make_mock_stream()

    with patch("httpx.stream", side_effect=fake_stream):
        download_file("https://example.com/file.xlsx", dest)

    sent_ua: str = captured["headers"]["User-Agent"]  # type: ignore[index]
    assert "python-httpx" not in sent_ua.lower()
    assert "Mozilla" in sent_ua


def test_download_file_uses_default_headers(tmp_path: Path) -> None:
    """download_file passes _DEFAULT_HEADERS to httpx.stream when no custom headers given."""
    dest = tmp_path / "file.xlsx"
    captured: dict[str, object] = {}

    def fake_stream(
        method: str,
        url: str,
        *,
        follow_redirects: bool,
        timeout: float,
        headers: dict[str, str],
    ) -> MagicMock:
        captured["headers"] = headers
        return _make_mock_stream()

    with patch("httpx.stream", side_effect=fake_stream):
        download_file("https://example.com/file.xlsx", dest)

    assert captured["headers"] == _DEFAULT_HEADERS


def test_download_file_custom_headers_merged_and_win(tmp_path: Path) -> None:
    """Custom headers are merged with defaults; custom values take precedence on conflict."""
    dest = tmp_path / "file.xlsx"
    captured: dict[str, object] = {}

    def fake_stream(
        method: str,
        url: str,
        *,
        follow_redirects: bool,
        timeout: float,
        headers: dict[str, str],
    ) -> MagicMock:
        captured["headers"] = headers
        return _make_mock_stream()

    custom = {"User-Agent": "MyCustomAgent/1.0", "X-Custom": "yes"}
    with patch("httpx.stream", side_effect=fake_stream):
        download_file("https://example.com/file.xlsx", dest, headers=custom)

    sent: dict[str, str] = captured["headers"]  # type: ignore[assignment]
    assert sent["User-Agent"] == "MyCustomAgent/1.0", "custom User-Agent must win"
    assert sent["X-Custom"] == "yes", "extra custom header must be present"


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
