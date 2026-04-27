"""Tests for scripts/fetch_data.py."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

from scripts.fetch_data import main


def _make_sources(
    tmp_path: Path,
    url: str = "https://example.com/data.xlsx",
    *,
    discovery_url: str | None = None,
    series_match: str | None = None,
) -> dict:
    """Return a sources dict with a single RBNZ xlsx source pointing at tmp_path."""
    source: dict = {
        "url": url,
        "name": "Test Source",
        "output_file": str(tmp_path / "raw" / "data.xlsx"),
    }
    if discovery_url is not None:
        source["discovery_url"] = discovery_url
    if series_match is not None:
        source["series_match"] = series_match
    return {"rbnz": {"xlsx_sources": [source]}}


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

    with (
        patch("scripts.fetch_data.load_sources", return_value=sources),
        patch(
            "scripts.fetch_data.download_file",
            side_effect=[OSError("connection refused"), tmp_path / "b.xlsx"],
        ),
    ):
        result = main()

    assert result == 1


def test_main_uses_discovered_url_when_discovery_succeeds(tmp_path: Path) -> None:
    """main() downloads from the discovered URL when discovery returns one."""
    (tmp_path / "raw").mkdir()
    sources = _make_sources(
        tmp_path,
        url="https://fallback.example.com/data.xlsx",
        discovery_url="https://www.rbnz.govt.nz/statistics/series/data-file-index-page",
        series_match="Bank Financial Strength Dashboard",
    )
    discovered = "https://www.rbnz.govt.nz/content/dam/data.xlsx"

    with (
        patch("scripts.fetch_data.load_sources", return_value=sources),
        patch("scripts.fetch_data.discover_xlsx_url", return_value=discovered),
        patch("scripts.fetch_data.download_file") as mock_download,
    ):
        mock_download.return_value = tmp_path / "raw" / "data.xlsx"
        result = main()

    assert result == 0
    args, _ = mock_download.call_args
    assert args[0] == discovered


def test_main_falls_back_to_configured_url_when_discovery_fails(tmp_path: Path) -> None:
    """main() falls back to the configured url when discovery returns None."""
    (tmp_path / "raw").mkdir()
    fallback = "https://fallback.example.com/data.xlsx"
    sources = _make_sources(
        tmp_path,
        url=fallback,
        discovery_url="https://www.rbnz.govt.nz/statistics/series/data-file-index-page",
        series_match="Bank Financial Strength Dashboard",
    )

    with (
        patch("scripts.fetch_data.load_sources", return_value=sources),
        patch("scripts.fetch_data.discover_xlsx_url", return_value=None),
        patch("scripts.fetch_data.download_file") as mock_download,
    ):
        mock_download.return_value = tmp_path / "raw" / "data.xlsx"
        result = main()

    assert result == 0
    args, _ = mock_download.call_args
    assert args[0] == fallback


def test_main_skips_discovery_when_not_configured(tmp_path: Path) -> None:
    """main() downloads directly from the configured url when no discovery fields are set."""
    (tmp_path / "raw").mkdir()
    url = "https://example.com/data.xlsx"
    sources = _make_sources(tmp_path, url=url)

    with (
        patch("scripts.fetch_data.load_sources", return_value=sources),
        patch("scripts.fetch_data.discover_xlsx_url") as mock_discover,
        patch("scripts.fetch_data.download_file") as mock_download,
    ):
        mock_download.return_value = tmp_path / "raw" / "data.xlsx"
        result = main()

    assert result == 0
    mock_discover.assert_not_called()
    args, _ = mock_download.call_args
    assert args[0] == url
