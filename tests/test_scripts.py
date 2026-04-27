"""Tests for scripts/fetch_data.py."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

from scripts.fetch_data import _USER_AGENT, main


def _make_sources(tmp_path: Path, url: str = "https://example.com/data.xlsx") -> dict:
    """Return a sources dict with a single RBNZ xlsx source pointing at tmp_path."""
    return {
        "rbnz": {
            "xlsx_sources": [
                {
                    "url": url,
                    "name": "Test Source",
                    "output_file": str(tmp_path / "raw" / "data.xlsx"),
                }
            ]
        }
    }


def test_main_success(tmp_path: Path) -> None:
    """main() returns 0 when all downloads succeed."""
    (tmp_path / "raw").mkdir()
    sources = _make_sources(tmp_path)

    with (
        patch("scripts.fetch_data.load_sources", return_value=sources),
        patch("scripts.fetch_data.download_file") as mock_download,
    ):
        mock_download.return_value = tmp_path / "raw" / "data.xlsx"
        result = main()

    assert result == 0
    mock_download.assert_called_once()
    _, kwargs = mock_download.call_args
    assert kwargs.get("headers", {}).get("User-Agent") == _USER_AGENT


def test_main_returns_error_count_on_failure(tmp_path: Path) -> None:
    """main() returns the number of failed downloads."""
    (tmp_path / "raw").mkdir()
    sources = _make_sources(tmp_path)

    with (
        patch("scripts.fetch_data.load_sources", return_value=sources),
        patch("scripts.fetch_data.download_file", side_effect=OSError("connection refused")),
    ):
        result = main()

    assert result == 1


def test_main_creates_output_directory(tmp_path: Path) -> None:
    """main() creates the output directory if it does not exist."""
    # raw/ sub-directory does NOT exist yet
    sources = _make_sources(tmp_path)

    with (
        patch("scripts.fetch_data.load_sources", return_value=sources),
        patch("scripts.fetch_data.download_file") as mock_download,
    ):
        mock_download.return_value = tmp_path / "raw" / "data.xlsx"
        main()

    assert (tmp_path / "raw").is_dir()


def test_main_no_sources(tmp_path: Path) -> None:
    """main() returns 0 when there are no configured sources."""
    with patch("scripts.fetch_data.load_sources", return_value={"rbnz": {}}):
        result = main()

    assert result == 0


def test_main_passes_timeout_to_download(tmp_path: Path) -> None:
    """main() forwards a generous timeout to download_file."""
    (tmp_path / "raw").mkdir()
    sources = _make_sources(tmp_path)

    with (
        patch("scripts.fetch_data.load_sources", return_value=sources),
        patch("scripts.fetch_data.download_file") as mock_download,
    ):
        mock_download.return_value = tmp_path / "raw" / "data.xlsx"
        main()

    _, kwargs = mock_download.call_args
    assert kwargs.get("timeout", 0) >= 60


def test_main_partial_failure_counts_correctly(tmp_path: Path) -> None:
    """main() counts each failed download separately."""
    sources = {
        "rbnz": {
            "xlsx_sources": [
                {
                    "url": "https://example.com/a.xlsx",
                    "name": "Source A",
                    "output_file": str(tmp_path / "a.xlsx"),
                },
                {
                    "url": "https://example.com/b.xlsx",
                    "name": "Source B",
                    "output_file": str(tmp_path / "b.xlsx"),
                },
            ]
        }
    }

    call_count = 0

    def _side_effect(*args, **kwargs):
        nonlocal call_count
        call_count += 1
        if call_count == 1:
            raise OSError("connection refused")
        return tmp_path / "b.xlsx"

    with (
        patch("scripts.fetch_data.load_sources", return_value=sources),
        patch("scripts.fetch_data.download_file", side_effect=_side_effect),
    ):
        result = main()

    assert result == 1
