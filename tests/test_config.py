"""Tests for config loading and validation."""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from src.config import load_metrics, load_sources


def _write_sources(tmp_path: Path, content: dict) -> Path:
    p = tmp_path / "sources.yaml"
    p.write_text(yaml.dump(content), encoding="utf-8")
    return p


def test_load_sources_valid_file(tmp_path: Path) -> None:
    cfg = _write_sources(
        tmp_path,
        {
            "rbnz": {
                "xlsx_sources": [
                    {
                        "url": "https://example.com/data.xlsx",
                        "name": "Test Source",
                    }
                ]
            }
        },
    )
    result = load_sources(cfg)
    assert result["rbnz"]["xlsx_sources"][0]["url"] == "https://example.com/data.xlsx"


def test_load_sources_empty_sections_valid(tmp_path: Path) -> None:
    cfg = _write_sources(tmp_path, {"rbnz": {}})
    result = load_sources(cfg)
    assert "rbnz" in result


def test_load_sources_raises_on_missing_file() -> None:
    with pytest.raises(FileNotFoundError):
        load_sources(Path("/nonexistent/sources.yaml"))


def test_load_sources_raises_on_missing_url(tmp_path: Path) -> None:
    cfg = _write_sources(
        tmp_path,
        {"rbnz": {"xlsx_sources": [{"name": "Missing URL"}]}},
    )
    with pytest.raises(ValueError, match="missing required key 'url'"):
        load_sources(cfg)


def test_load_sources_raises_on_missing_name(tmp_path: Path) -> None:
    cfg = _write_sources(
        tmp_path,
        {"rbnz": {"xlsx_sources": [{"url": "https://example.com/data.xlsx"}]}},
    )
    with pytest.raises(ValueError, match="missing required key 'name'"):
        load_sources(cfg)


def test_load_sources_accepts_real_sources_yaml() -> None:
    """The committed config/sources.yaml must be valid."""
    result = load_sources()
    assert "rbnz" in result


def test_load_metrics_raises_on_missing_file() -> None:
    with pytest.raises(FileNotFoundError):
        load_metrics(Path("/nonexistent/metrics.yaml"))


def test_load_metrics_accepts_real_metrics_yaml() -> None:
    """The committed config/metrics.yaml must be loadable."""
    result = load_metrics()
    assert isinstance(result, dict)
