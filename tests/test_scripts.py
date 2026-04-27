"""Tests for scripts/fetch_data.py."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

from scripts.fetch_data import _USER_AGENT, _browser_headers, main


def _make_sources(
    tmp_path: Path,
    url: str = "https://example.com/data.xlsx",
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


# ---------------------------------------------------------------------------
# User-Agent and headers
# ---------------------------------------------------------------------------


def test_user_agent_is_browser_like() -> None:
    """_USER_AGENT must look like a real browser, not a bot identifier."""
    assert _USER_AGENT.startswith("Mozilla/"), (
        f"User-Agent should start with 'Mozilla/', got: {_USER_AGENT!r}"
    )


def test_browser_headers_contains_user_agent() -> None:
    """_browser_headers() always includes User-Agent."""
    h = _browser_headers()
    assert h["User-Agent"] == _USER_AGENT


def test_browser_headers_no_referer_by_default() -> None:
    """_browser_headers() omits Referer when none is given."""
    h = _browser_headers()
    assert "Referer" not in h


def test_browser_headers_includes_referer_when_given() -> None:
    """_browser_headers(referer=...) sets the Referer header."""
    h = _browser_headers(referer="https://example.com/summary")
    assert h["Referer"] == "https://example.com/summary"


# ---------------------------------------------------------------------------
# main() — basic behaviour (no discovery_url)
# ---------------------------------------------------------------------------


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


def test_main_sends_browser_user_agent(tmp_path: Path) -> None:
    """main() passes a browser-like User-Agent to download_file."""
    (tmp_path / "raw").mkdir()
    sources = _make_sources(tmp_path)

    with (
        patch("scripts.fetch_data.load_sources", return_value=sources),
        patch("scripts.fetch_data.download_file") as mock_download,
    ):
        mock_download.return_value = tmp_path / "raw" / "data.xlsx"
        main()

    _, kwargs = mock_download.call_args
    ua = kwargs.get("headers", {}).get("User-Agent", "")
    assert ua.startswith("Mozilla/"), f"Expected browser UA, got: {ua!r}"


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


# ---------------------------------------------------------------------------
# main() — discovery_url behaviour
# ---------------------------------------------------------------------------


def test_main_uses_discovered_url(tmp_path: Path) -> None:
    """When discovery succeeds, main() downloads from the discovered URL."""
    (tmp_path / "raw").mkdir()
    discovered = "https://example.com/discovered.xlsx"
    sources = _make_sources(tmp_path, discovery_url="https://example.com/summary")

    with (
        patch("scripts.fetch_data.load_sources", return_value=sources),
        patch("scripts.fetch_data.find_xlsx_url", return_value=discovered) as mock_find,
        patch("scripts.fetch_data.download_file") as mock_download,
    ):
        mock_download.return_value = tmp_path / "raw" / "data.xlsx"
        result = main()

    assert result == 0
    mock_find.assert_called_once()
    # First positional arg to download_file must be the discovered URL
    args, _ = mock_download.call_args
    assert args[0] == discovered


def test_main_passes_series_match_to_find_xlsx_url(tmp_path: Path) -> None:
    """main() forwards series_match from config to find_xlsx_url."""
    (tmp_path / "raw").mkdir()
    sources = _make_sources(
        tmp_path,
        discovery_url="https://example.com/index",
        series_match="bank financial strength",
    )

    with (
        patch("scripts.fetch_data.load_sources", return_value=sources),
        patch("scripts.fetch_data.find_xlsx_url", return_value=None) as mock_find,
        patch("scripts.fetch_data.download_file") as mock_download,
    ):
        mock_download.return_value = tmp_path / "raw" / "data.xlsx"
        main()

    _, kwargs = mock_find.call_args
    assert kwargs.get("series_match") == "bank financial strength"


def test_main_series_match_none_when_not_configured(tmp_path: Path) -> None:
    """series_match defaults to None when not in config."""
    (tmp_path / "raw").mkdir()
    sources = _make_sources(tmp_path, discovery_url="https://example.com/index")

    with (
        patch("scripts.fetch_data.load_sources", return_value=sources),
        patch("scripts.fetch_data.find_xlsx_url", return_value=None) as mock_find,
        patch("scripts.fetch_data.download_file") as mock_download,
    ):
        mock_download.return_value = tmp_path / "raw" / "data.xlsx"
        main()

    _, kwargs = mock_find.call_args
    assert kwargs.get("series_match") is None


def test_main_falls_back_to_configured_url_when_discovery_fails(tmp_path: Path) -> None:
    """When discovery returns None, main() falls back to the configured URL."""
    (tmp_path / "raw").mkdir()
    configured_url = "https://example.com/data.xlsx"
    sources = _make_sources(
        tmp_path, url=configured_url, discovery_url="https://example.com/summary"
    )

    with (
        patch("scripts.fetch_data.load_sources", return_value=sources),
        patch("scripts.fetch_data.find_xlsx_url", return_value=None),
        patch("scripts.fetch_data.download_file") as mock_download,
    ):
        mock_download.return_value = tmp_path / "raw" / "data.xlsx"
        result = main()

    assert result == 0
    args, _ = mock_download.call_args
    assert args[0] == configured_url


def test_main_sends_referer_from_discovery_url(tmp_path: Path) -> None:
    """When discovery_url is set, download request includes it as Referer."""
    (tmp_path / "raw").mkdir()
    discovery_url = "https://example.com/summary"
    sources = _make_sources(tmp_path, discovery_url=discovery_url)

    with (
        patch("scripts.fetch_data.load_sources", return_value=sources),
        patch("scripts.fetch_data.find_xlsx_url", return_value=None),
        patch("scripts.fetch_data.download_file") as mock_download,
    ):
        mock_download.return_value = tmp_path / "raw" / "data.xlsx"
        main()

    _, kwargs = mock_download.call_args
    assert kwargs.get("headers", {}).get("Referer") == discovery_url


def test_main_discovery_not_called_without_discovery_url(tmp_path: Path) -> None:
    """find_xlsx_url is NOT called when no discovery_url is configured."""
    (tmp_path / "raw").mkdir()
    sources = _make_sources(tmp_path)  # no discovery_url

    with (
        patch("scripts.fetch_data.load_sources", return_value=sources),
        patch("scripts.fetch_data.find_xlsx_url") as mock_find,
        patch("scripts.fetch_data.download_file") as mock_download,
    ):
        mock_download.return_value = tmp_path / "raw" / "data.xlsx"
        main()

    mock_find.assert_not_called()
