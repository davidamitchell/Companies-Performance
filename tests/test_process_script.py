"""Tests for scripts/process_data.py."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

from scripts.process_data import _resolve_xlsx_path, main

# ---------------------------------------------------------------------------
# _resolve_xlsx_path
# ---------------------------------------------------------------------------


def test_resolve_xlsx_path_prefers_output_file(tmp_path: Path) -> None:
    raw = tmp_path / "raw.xlsx"
    raw.write_bytes(b"")
    committed = tmp_path / "committed.xlsx"
    committed.write_bytes(b"")

    result = _resolve_xlsx_path({"output_file": str(raw), "committed_file": str(committed)})
    assert result == raw


def test_resolve_xlsx_path_falls_back_to_committed_file(tmp_path: Path) -> None:
    committed = tmp_path / "committed.xlsx"
    committed.write_bytes(b"")

    result = _resolve_xlsx_path(
        {"output_file": str(tmp_path / "raw.xlsx"), "committed_file": str(committed)}
    )
    assert result == committed


def test_resolve_xlsx_path_returns_none_when_neither_exists(tmp_path: Path) -> None:
    result = _resolve_xlsx_path(
        {
            "output_file": str(tmp_path / "raw.xlsx"),
            "committed_file": str(tmp_path / "committed.xlsx"),
        }
    )
    assert result is None


def test_resolve_xlsx_path_handles_missing_keys() -> None:
    result = _resolve_xlsx_path({})
    assert result is None


# ---------------------------------------------------------------------------
# main()
# ---------------------------------------------------------------------------


def _make_config(tmp_path: Path) -> tuple[dict, dict, Path]:
    """Return (sources, metrics_config, xlsx_path) with an existing xlsx file."""
    xlsx_path = tmp_path / "rbnz.xlsx"
    xlsx_path.write_bytes(b"")
    sources = {
        "rbnz": {
            "xlsx_sources": [
                {
                    "name": "Test",
                    "committed_file": str(xlsx_path),
                }
            ]
        }
    }
    metrics_config = {"mappings": {"rbnz-dashboard": {"DBB.QIB12": "CET1 Ratio"}}}
    return sources, metrics_config, xlsx_path


def test_main_returns_zero_on_success(tmp_path: Path) -> None:
    sources, metrics_config, xlsx_path = _make_config(tmp_path)
    rows = [
        {
            "entity": "ANZ",
            "metric": "CET1 Ratio",
            "value": 13.5,
            "period": "2024-Q3",
            "source": "rbnz-dashboard",
        }
    ]

    with (
        patch("scripts.process_data.load_sources", return_value=sources),
        patch("scripts.process_data.load_metrics", return_value=metrics_config),
        patch("scripts.process_data.parse_rbnz_xlsx", return_value=rows),
        patch("scripts.process_data.write_csv"),
        patch("scripts.process_data.write_json"),
        patch("scripts.process_data._CSV_OUTPUT", tmp_path / "metrics.csv"),
        patch("scripts.process_data._JSON_OUTPUT", tmp_path / "metrics.json"),
    ):
        result = main()

    assert result == 0


def test_main_returns_one_on_config_load_failure(tmp_path: Path) -> None:
    with patch("scripts.process_data.load_sources", side_effect=FileNotFoundError("x")):
        result = main()
    assert result == 1


def test_main_returns_one_on_no_sources() -> None:
    with (
        patch("scripts.process_data.load_sources", return_value={"rbnz": {}}),
        patch("scripts.process_data.load_metrics", return_value={}),
    ):
        result = main()
    assert result == 1


def test_main_returns_one_when_no_xlsx_found(tmp_path: Path) -> None:
    sources = {
        "rbnz": {"xlsx_sources": [{"name": "Test", "output_file": str(tmp_path / "missing.xlsx")}]}
    }
    with (
        patch("scripts.process_data.load_sources", return_value=sources),
        patch("scripts.process_data.load_metrics", return_value={}),
    ):
        result = main()
    assert result == 1


def test_main_returns_one_on_empty_parse_output(tmp_path: Path) -> None:
    sources, metrics_config, xlsx_path = _make_config(tmp_path)

    with (
        patch("scripts.process_data.load_sources", return_value=sources),
        patch("scripts.process_data.load_metrics", return_value=metrics_config),
        patch("scripts.process_data.parse_rbnz_xlsx", return_value=[]),
    ):
        result = main()
    assert result == 1


def test_main_returns_one_on_parse_error(tmp_path: Path) -> None:
    sources, metrics_config, xlsx_path = _make_config(tmp_path)

    with (
        patch("scripts.process_data.load_sources", return_value=sources),
        patch("scripts.process_data.load_metrics", return_value=metrics_config),
        patch("scripts.process_data.parse_rbnz_xlsx", side_effect=ValueError("bad xlsx")),
    ):
        result = main()
    assert result == 1
