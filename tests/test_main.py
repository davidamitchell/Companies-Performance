"""Tests for the src.main CLI entry point."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any
from unittest.mock import patch

import pytest

import src.main as main_module

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_sources_cfg(
    sources: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """Build a minimal sources config dict for testing."""
    if sources is None:
        sources = [
            {
                "url": "https://example.com/data.xlsx",
                "name": "Test Source",
                "output_file": "data/raw/test.xlsx",
            }
        ]
    return {"rbnz": {"xlsx_sources": sources}}


# ---------------------------------------------------------------------------
# fetch rbnz — download called with correct args
# ---------------------------------------------------------------------------


def test_fetch_rbnz_calls_download_file(tmp_path: Path) -> None:
    """fetch rbnz should call download_file with the URL and dest from config."""
    dest_path = tmp_path / "data" / "raw" / "test.xlsx"

    cfg = {
        "rbnz": {
            "xlsx_sources": [
                {
                    "url": "https://example.com/data.xlsx",
                    "name": "Test Source",
                    "output_file": str(dest_path),
                }
            ]
        }
    }

    with (
        patch("src.main.load_sources", return_value=cfg) as mock_load,
        patch("src.main.download_file") as mock_dl,
    ):
        # monkeypatch _DEFAULT_RAW_DIR so mkdir doesn't fail
        with patch.object(main_module, "_DEFAULT_RAW_DIR", tmp_path / "data" / "raw"):
            args = argparse.Namespace(dest=None, dry_run=False, fetch_command="rbnz")
            main_module._fetch_rbnz(args)

        mock_load.assert_called_once()
        mock_dl.assert_called_once_with(
            "https://example.com/data.xlsx",
            dest_path,
        )


def test_fetch_rbnz_dest_override(tmp_path: Path) -> None:
    """--dest should override the path in config."""
    override = tmp_path / "custom.xlsx"
    cfg = _make_sources_cfg(
        [
            {
                "url": "https://example.com/data.xlsx",
                "name": "Source",
                "output_file": "data/raw/original.xlsx",
            }
        ]
    )

    with (
        patch("src.main.load_sources", return_value=cfg),
        patch("src.main.download_file") as mock_dl,
        patch.object(main_module, "_DEFAULT_RAW_DIR", tmp_path),
    ):
        args = argparse.Namespace(dest=str(override), dry_run=False, fetch_command="rbnz")
        main_module._fetch_rbnz(args)

        mock_dl.assert_called_once_with("https://example.com/data.xlsx", override)


def test_fetch_rbnz_fallback_dest_when_no_output_file(tmp_path: Path) -> None:
    """When output_file is absent, dest falls back to data/raw/<safe-name>.xlsx."""
    cfg = {
        "rbnz": {
            "xlsx_sources": [
                {
                    "url": "https://example.com/data.xlsx",
                    "name": "My Data Source",
                }
            ]
        }
    }
    raw_dir = tmp_path / "data" / "raw"

    with (
        patch("src.main.load_sources", return_value=cfg),
        patch("src.main.download_file") as mock_dl,
        patch.object(main_module, "_DEFAULT_RAW_DIR", raw_dir),
    ):
        args = argparse.Namespace(dest=None, dry_run=False, fetch_command="rbnz")
        main_module._fetch_rbnz(args)

        expected_dest = raw_dir / "my-data-source.xlsx"
        mock_dl.assert_called_once_with("https://example.com/data.xlsx", expected_dest)


# ---------------------------------------------------------------------------
# --dry-run — download_file must NOT be called
# ---------------------------------------------------------------------------


def test_fetch_rbnz_dry_run_skips_download(tmp_path: Path) -> None:
    """--dry-run must not call download_file."""
    cfg = _make_sources_cfg(
        [
            {
                "url": "https://example.com/data.xlsx",
                "name": "Source",
                "output_file": str(tmp_path / "out.xlsx"),
            }
        ]
    )

    with (
        patch("src.main.load_sources", return_value=cfg),
        patch("src.main.download_file") as mock_dl,
        patch.object(main_module, "_DEFAULT_RAW_DIR", tmp_path),
    ):
        args = argparse.Namespace(dest=None, dry_run=True, fetch_command="rbnz")
        main_module._fetch_rbnz(args)

        mock_dl.assert_not_called()


# ---------------------------------------------------------------------------
# Missing rbnz.xlsx_sources — non-zero exit
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "bad_cfg",
    [
        {"rbnz": {"xlsx_sources": []}},
        {"rbnz": {}},
        {},
    ],
    ids=["empty_list", "no_key", "no_rbnz"],
)
def test_fetch_rbnz_exits_on_missing_sources(tmp_path: Path, bad_cfg: dict[str, Any]) -> None:
    """Non-zero exit when xlsx_sources is absent or empty."""
    with (
        patch("src.main.load_sources", return_value=bad_cfg),
        patch.object(main_module, "_DEFAULT_RAW_DIR", tmp_path),
        pytest.raises(SystemExit) as exc_info,
    ):
        args = argparse.Namespace(dest=None, dry_run=False, fetch_command="rbnz")
        main_module._fetch_rbnz(args)

    assert exc_info.value.code != 0


def test_fetch_rbnz_exits_on_config_error(tmp_path: Path) -> None:
    """Non-zero exit when load_sources raises."""
    with (
        patch("src.main.load_sources", side_effect=FileNotFoundError("no file")),
        patch.object(main_module, "_DEFAULT_RAW_DIR", tmp_path),
        pytest.raises(SystemExit) as exc_info,
    ):
        args = argparse.Namespace(dest=None, dry_run=False, fetch_command="rbnz")
        main_module._fetch_rbnz(args)

    assert exc_info.value.code != 0


# ---------------------------------------------------------------------------
# fetch with no subcommand — exits with error
# ---------------------------------------------------------------------------


def test_dispatch_fetch_no_subcommand_exits() -> None:
    """fetch with no subcommand should print usage and exit non-zero."""
    args = argparse.Namespace(fetch_command=None)
    with pytest.raises(SystemExit) as exc_info:
        main_module._dispatch_fetch(args)

    assert exc_info.value.code != 0


# ---------------------------------------------------------------------------
# main() with no command — prints help and exits cleanly
# ---------------------------------------------------------------------------


def test_main_no_command_exits_zero(monkeypatch: pytest.MonkeyPatch) -> None:
    """main() with no arguments should print help and exit 0."""
    monkeypatch.setattr("sys.argv", ["companies-performance"])
    with pytest.raises(SystemExit) as exc_info:
        main_module.main()
    assert exc_info.value.code == 0


# ---------------------------------------------------------------------------
# Integration: main() fetch rbnz
# ---------------------------------------------------------------------------


def test_main_fetch_rbnz_integration(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """main() dispatches fetch rbnz end-to-end (no real HTTP call)."""
    dest = tmp_path / "data" / "raw" / "test.xlsx"
    cfg = {
        "rbnz": {
            "xlsx_sources": [
                {
                    "url": "https://example.com/data.xlsx",
                    "name": "Test Source",
                    "output_file": str(dest),
                }
            ]
        }
    }

    monkeypatch.setattr("sys.argv", ["companies-performance", "fetch", "rbnz"])

    with (
        patch("src.main.load_sources", return_value=cfg),
        patch("src.main.download_file") as mock_dl,
        patch.object(main_module, "_DEFAULT_RAW_DIR", tmp_path / "data" / "raw"),
    ):
        main_module.main()
        mock_dl.assert_called_once_with("https://example.com/data.xlsx", dest)
