"""Shared pytest fixtures."""

from __future__ import annotations

import pytest


@pytest.fixture
def data_dir(tmp_path):
    """Create a temporary data directory structure."""
    (tmp_path / "raw").mkdir()
    (tmp_path / "processed").mkdir()
    return tmp_path
