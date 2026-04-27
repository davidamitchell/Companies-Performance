"""Tests for scripts/fetch_data.py."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

from scripts.fetch_data import fetch_all_sources


def _sources_config(output_file: str) -> dict:
    return {
        "rbnz": {
            "xlsx_sources": [
                {
                    "url": "https://example.com/file.xlsx",
                    "name": "Test Source",
                    "output_file": output_file,
                }
            ]
        }
    }


def test_fetch_all_sources_calls_download_file(tmp_path: Path) -> None:
    """fetch_all_sources delegates to download_file for each configured source."""
    dest = str(tmp_path / "raw" / "test.xlsx")
    config = _sources_config(dest)

    with (
        patch("scripts.fetch_data.load_sources", return_value=config),
        patch("scripts.fetch_data.download_file") as mock_dl,
    ):
        mock_dl.return_value = Path(dest)
        result = fetch_all_sources()

    assert result == 0
    mock_dl.assert_called_once_with("https://example.com/file.xlsx", Path(dest), timeout=120.0)


def test_fetch_all_sources_creates_parent_dirs(tmp_path: Path) -> None:
    """fetch_all_sources creates missing parent directories before downloading."""
    dest = str(tmp_path / "deep" / "nested" / "file.xlsx")
    config = _sources_config(dest)

    with (
        patch("scripts.fetch_data.load_sources", return_value=config),
        patch("scripts.fetch_data.download_file") as mock_dl,
    ):
        mock_dl.return_value = Path(dest)
        fetch_all_sources()

    assert (tmp_path / "deep" / "nested").is_dir()


def test_fetch_all_sources_returns_1_on_failure(tmp_path: Path) -> None:
    """fetch_all_sources returns 1 if any download raises an exception."""
    dest = str(tmp_path / "raw" / "test.xlsx")
    config = _sources_config(dest)

    with (
        patch("scripts.fetch_data.load_sources", return_value=config),
        patch("scripts.fetch_data.download_file", side_effect=Exception("network error")),
    ):
        result = fetch_all_sources()

    assert result == 1


def test_fetch_all_sources_empty_sources() -> None:
    """fetch_all_sources returns 0 when there are no configured sources."""
    with patch("scripts.fetch_data.load_sources", return_value={}):
        result = fetch_all_sources()

    assert result == 0


def test_fetch_all_sources_uses_download_file_not_httpx_directly(tmp_path: Path) -> None:
    """fetch_all_sources must not call httpx directly — only via download_file."""
    dest = str(tmp_path / "raw" / "test.xlsx")
    config = _sources_config(dest)

    with (
        patch("scripts.fetch_data.load_sources", return_value=config),
        patch("scripts.fetch_data.download_file") as mock_dl,
        patch("httpx.stream") as mock_httpx,
    ):
        mock_dl.return_value = Path(dest)
        fetch_all_sources()

    mock_dl.assert_called_once()
    mock_httpx.assert_not_called()
