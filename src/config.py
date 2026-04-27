"""Load and validate configuration from config/sources.yaml and config/metrics.yaml."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml  # type: ignore[import-untyped]

from src.logger import get_logger

logger = get_logger(__name__)

_DEFAULT_SOURCES_PATH = Path(__file__).parent.parent / "config" / "sources.yaml"
_DEFAULT_METRICS_PATH = Path(__file__).parent.parent / "config" / "metrics.yaml"


def load_sources(path: Path | None = None) -> dict[str, Any]:
    """Load and validate the sources configuration.

    Parameters
    ----------
    path:
        Path to the YAML config file. Defaults to ``config/sources.yaml``.

    Returns
    -------
    dict
        Validated configuration dictionary.

    Raises
    ------
    FileNotFoundError
        If the config file does not exist.
    ValueError
        If the config file is missing required keys or has invalid values.
    """
    config_path = path or _DEFAULT_SOURCES_PATH
    if not config_path.exists():
        raise FileNotFoundError(f"Sources config not found: {config_path}")

    with config_path.open(encoding="utf-8") as fh:
        raw: dict[str, Any] = yaml.safe_load(fh) or {}

    _validate_sources(raw, config_path)
    logger.debug("Loaded sources config from %s", config_path)
    return raw


def load_metrics(path: Path | None = None) -> dict[str, Any]:
    """Load the metrics mapping configuration.

    Parameters
    ----------
    path:
        Path to the YAML config file. Defaults to ``config/metrics.yaml``.

    Returns
    -------
    dict
        Metrics mapping dictionary.

    Raises
    ------
    FileNotFoundError
        If the config file does not exist.
    """
    config_path = path or _DEFAULT_METRICS_PATH
    if not config_path.exists():
        raise FileNotFoundError(f"Metrics config not found: {config_path}")

    with config_path.open(encoding="utf-8") as fh:
        raw: dict[str, Any] = yaml.safe_load(fh) or {}

    logger.debug("Loaded metrics config from %s", config_path)
    return raw


def _validate_sources(config: dict[str, Any], path: Path) -> None:
    """Raise ValueError if the sources config structure is invalid."""
    rbnz = config.get("rbnz", {}) or {}
    if not isinstance(rbnz, dict):
        raise ValueError(f"{path}: 'rbnz' must be a mapping, got {type(rbnz).__name__}")

    for i, source in enumerate(rbnz.get("xlsx_sources") or []):
        if not isinstance(source, dict):
            raise ValueError(f"{path}: rbnz.xlsx_sources[{i}] must be a mapping")
        if "url" not in source:
            raise ValueError(f"{path}: rbnz.xlsx_sources[{i}] missing required key 'url'")
        if "name" not in source:
            raise ValueError(f"{path}: rbnz.xlsx_sources[{i}] missing required key 'name'")
