"""Tests for scripts/build_disclosures_index.py."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from scripts.build_disclosures_index import load_sidecars, write_index


@pytest.fixture()
def raw_dir(tmp_path: Path) -> Path:
    """Create a minimal sidecar directory tree."""
    for bank_id, period_end, period_type in [
        ("anz", "2024-09-30", "full_year"),
        ("kiwibank", "2024-06-30", "half_year"),
        ("kiwibank", "2024-12-31", "half_year"),
    ]:
        bank_dir = tmp_path / bank_id
        bank_dir.mkdir(exist_ok=True)
        sidecar = {
            "bank_id": bank_id,
            "bank_name": bank_id.title(),
            "period_end": period_end,
            "period_type": period_type,
            "source_url": f"https://example.com/{bank_id}-{period_end}.pdf",
            "downloaded_at": "2026-04-29T00:00:00+00:00",
            "file_size_bytes": 1_000_000,
            "sha256": "abc123",
        }
        (bank_dir / f"{bank_id}-disclosure-{period_end}.meta.json").write_text(json.dumps(sidecar))
    return tmp_path


def test_load_sidecars_count(raw_dir: Path) -> None:
    records = load_sidecars(raw_dir)
    assert len(records) == 3


def test_load_sidecars_sorted(raw_dir: Path) -> None:
    records = load_sidecars(raw_dir)
    keys = [(r["bank_id"], r["period_end"]) for r in records]
    assert keys == sorted(keys)


def test_load_sidecars_fields(raw_dir: Path) -> None:
    records = load_sidecars(raw_dir)
    required = {"bank_id", "bank_name", "period_end", "period_type", "source_url"}
    for rec in records:
        assert required.issubset(rec.keys())


def test_load_sidecars_skips_malformed(raw_dir: Path, tmp_path: Path) -> None:
    bad = raw_dir / "bad"
    bad.mkdir()
    (bad / "bad-disclosure-2024-01-01.meta.json").write_text("not json{{{")
    records = load_sidecars(raw_dir)
    assert len(records) == 3  # malformed sidecar is skipped


def test_write_index_creates_file(raw_dir: Path, tmp_path: Path) -> None:
    records = load_sidecars(raw_dir)
    out = tmp_path / "out" / "disclosures.json"
    write_index(records, out)
    assert out.exists()
    loaded = json.loads(out.read_text())
    assert len(loaded) == 3


def test_write_index_idempotent(raw_dir: Path, tmp_path: Path) -> None:
    records = load_sidecars(raw_dir)
    out = tmp_path / "disclosures.json"
    write_index(records, out)
    first = out.read_text()
    write_index(records, out)
    assert out.read_text() == first


def test_main_returns_zero(raw_dir: Path, tmp_path: Path) -> None:
    from scripts.build_disclosures_index import main

    out = tmp_path / "disclosures.json"
    rc = main(["--raw-dir", str(raw_dir), "--out", str(out)])
    assert rc == 0
    assert json.loads(out.read_text())


def test_main_returns_one_on_empty_dir(tmp_path: Path) -> None:
    from scripts.build_disclosures_index import main

    empty = tmp_path / "empty"
    empty.mkdir()
    out = tmp_path / "disclosures.json"
    rc = main(["--raw-dir", str(empty), "--out", str(out)])
    assert rc == 1
