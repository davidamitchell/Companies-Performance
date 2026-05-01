"""Tests for src/processing/parse.py."""

from __future__ import annotations

import csv
import json
from datetime import datetime
from pathlib import Path
from typing import Any

import pytest

from src.processing.parse import _to_quarter, parse_rbnz_xlsx, write_csv, write_json

# ---------------------------------------------------------------------------
# _to_quarter
# ---------------------------------------------------------------------------


def test_to_quarter_march_is_q1() -> None:
    assert _to_quarter(datetime(2024, 3, 31)) == "2024-Q1"


def test_to_quarter_june_is_q2() -> None:
    assert _to_quarter(datetime(2023, 6, 30)) == "2023-Q2"


def test_to_quarter_september_is_q3() -> None:
    assert _to_quarter(datetime(2022, 9, 30)) == "2022-Q3"


def test_to_quarter_december_is_q4() -> None:
    assert _to_quarter(datetime(2021, 12, 31)) == "2021-Q4"


def test_to_quarter_iso_string() -> None:
    assert _to_quarter("2024-06-30") == "2024-Q2"


def test_to_quarter_unparseable_falls_back_to_str() -> None:
    result = _to_quarter("not-a-date")
    assert result == "not-a-date"


# ---------------------------------------------------------------------------
# write_csv
# ---------------------------------------------------------------------------


def test_write_csv_creates_file(tmp_path: Path) -> None:
    rows = [
        {
            "entity": "ANZ",
            "metric": "CET1 Ratio",
            "value": 13.5,
            "period": "2024-Q3",
            "source": "rbnz-dashboard",
        }
    ]
    dest = tmp_path / "out.csv"
    write_csv(rows, dest)
    assert dest.exists()


def test_write_csv_creates_parent_dir(tmp_path: Path) -> None:
    rows: list[dict[str, Any]] = []
    dest = tmp_path / "deep" / "nested" / "out.csv"
    write_csv(rows, dest)
    assert dest.exists()


def test_write_csv_has_correct_headers(tmp_path: Path) -> None:
    rows = [
        {
            "entity": "ANZ",
            "metric": "NIM",
            "value": 2.1,
            "period": "2024-Q1",
            "source": "rbnz-dashboard",
        }
    ]
    dest = tmp_path / "out.csv"
    write_csv(rows, dest)
    with dest.open(encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        assert reader.fieldnames == ["entity", "entity_type", "metric", "value", "period", "source"]


def test_write_csv_roundtrip(tmp_path: Path) -> None:
    rows = [
        {
            "entity": "ANZ",
            "metric": "CET1 Ratio",
            "value": 13.5,
            "period": "2024-Q3",
            "source": "rbnz-dashboard",
        },
        {
            "entity": "ASB",
            "metric": "NIM",
            "value": 2.1,
            "period": "2024-Q3",
            "source": "rbnz-dashboard",
        },
    ]
    dest = tmp_path / "out.csv"
    write_csv(rows, dest)
    with dest.open(encoding="utf-8") as fh:
        reader = list(csv.DictReader(fh))
    assert len(reader) == 2
    assert reader[0]["entity"] == "ANZ"
    assert reader[1]["metric"] == "NIM"


def test_write_csv_null_value(tmp_path: Path) -> None:
    rows = [
        {
            "entity": "ANZ",
            "metric": "CET1 Ratio",
            "value": None,
            "period": "2024-Q3",
            "source": "rbnz-dashboard",
        }
    ]
    dest = tmp_path / "out.csv"
    write_csv(rows, dest)
    with dest.open(encoding="utf-8") as fh:
        reader = list(csv.DictReader(fh))
    assert reader[0]["value"] == ""  # csv writes None as empty string


def test_write_csv_idempotent(tmp_path: Path) -> None:
    rows = [
        {
            "entity": "BNZ",
            "metric": "NIM",
            "value": 2.0,
            "period": "2024-Q1",
            "source": "rbnz-dashboard",
        }
    ]
    dest = tmp_path / "out.csv"
    write_csv(rows, dest)
    first = dest.read_text(encoding="utf-8")
    write_csv(rows, dest)
    second = dest.read_text(encoding="utf-8")
    assert first == second


# ---------------------------------------------------------------------------
# write_json
# ---------------------------------------------------------------------------


def test_write_json_creates_file(tmp_path: Path) -> None:
    rows = [
        {
            "entity": "ANZ",
            "metric": "CET1 Ratio",
            "value": 13.5,
            "period": "2024-Q3",
            "source": "rbnz-dashboard",
        }
    ]
    dest = tmp_path / "out.json"
    write_json(rows, dest)
    assert dest.exists()


def test_write_json_valid_json(tmp_path: Path) -> None:
    rows = [
        {
            "entity": "ANZ",
            "metric": "CET1 Ratio",
            "value": 13.5,
            "period": "2024-Q3",
            "source": "rbnz-dashboard",
        }
    ]
    dest = tmp_path / "out.json"
    write_json(rows, dest)
    with dest.open(encoding="utf-8") as fh:
        parsed = json.load(fh)
    assert len(parsed) == 1
    assert parsed[0]["entity"] == "ANZ"


def test_write_json_null_value(tmp_path: Path) -> None:
    rows = [
        {
            "entity": "ANZ",
            "metric": "CET1 Ratio",
            "value": None,
            "period": "2024-Q3",
            "source": "rbnz-dashboard",
        }
    ]
    dest = tmp_path / "out.json"
    write_json(rows, dest)
    with dest.open(encoding="utf-8") as fh:
        parsed = json.load(fh)
    assert parsed[0]["value"] is None


def test_write_json_idempotent(tmp_path: Path) -> None:
    rows = [
        {
            "entity": "BNZ",
            "metric": "NIM",
            "value": 2.0,
            "period": "2024-Q1",
            "source": "rbnz-dashboard",
        }
    ]
    dest = tmp_path / "out.json"
    write_json(rows, dest)
    first = dest.read_text(encoding="utf-8")
    write_json(rows, dest)
    second = dest.read_text(encoding="utf-8")
    assert first == second


# ---------------------------------------------------------------------------
# parse_rbnz_xlsx — using a minimal in-memory workbook
# ---------------------------------------------------------------------------


def _make_workbook(data_rows: list[tuple]) -> Any:
    """Create a minimal openpyxl workbook mimicking the RBNZ XLSX structure."""
    import openpyxl

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Data"

    # Row 0: categories
    ws.append((None, None, "Capital adequacy - ratios & buffer"))
    # Row 1: series names
    ws.append((None, None, "C2. CET1 capital ratio"))
    # Row 2: notes
    ws.append(("Notes", None, None))
    # Row 3: units
    ws.append(("Unit", None, "%"))
    # Row 4: series IDs
    ws.append(("Series Id", "Institution", "DBB.QIB12"))
    # Data rows
    for row in data_rows:
        ws.append(row)

    return wb


def _save_and_get_path(wb: Any, tmp_path: Path) -> Path:
    path = tmp_path / "test.xlsx"
    wb.save(str(path))
    return path


def test_parse_rbnz_xlsx_basic(tmp_path: Path) -> None:
    wb = _make_workbook(
        [
            (datetime(2024, 9, 30), "ANZ", 13.5),
            (datetime(2024, 9, 30), "ASB", 14.2),
        ]
    )
    xlsx_path = _save_and_get_path(wb, tmp_path)
    metrics_config = {"mappings": {"rbnz-dashboard": {"DBB.QIB12": "CET1 Ratio"}}}

    rows = parse_rbnz_xlsx(xlsx_path, metrics_config)

    assert len(rows) == 2
    assert rows[0]["entity"] == "ANZ"
    assert rows[0]["metric"] == "CET1 Ratio"
    assert rows[0]["value"] == 13.5
    assert rows[0]["period"] == "2024-Q3"
    assert rows[0]["source"] == "rbnz-dashboard"


def test_parse_rbnz_xlsx_missing_value_recorded(tmp_path: Path) -> None:
    wb = _make_workbook([(datetime(2024, 3, 31), "Heartland", None)])
    xlsx_path = _save_and_get_path(wb, tmp_path)
    metrics_config = {"mappings": {"rbnz-dashboard": {"DBB.QIB12": "CET1 Ratio"}}}

    rows = parse_rbnz_xlsx(xlsx_path, metrics_config)

    assert len(rows) == 1
    assert rows[0]["value"] is None


def test_parse_rbnz_xlsx_duplicate_skipped(tmp_path: Path) -> None:
    wb = _make_workbook(
        [
            (datetime(2024, 3, 31), "ANZ", 13.5),
            (datetime(2024, 3, 31), "ANZ", 13.5),  # duplicate
        ]
    )
    xlsx_path = _save_and_get_path(wb, tmp_path)
    metrics_config = {"mappings": {"rbnz-dashboard": {"DBB.QIB12": "CET1 Ratio"}}}

    rows = parse_rbnz_xlsx(xlsx_path, metrics_config)

    assert len(rows) == 1


def test_parse_rbnz_xlsx_skips_empty_rows(tmp_path: Path) -> None:
    wb = _make_workbook(
        [
            (None, None, None),  # empty date and institution — skip
            (datetime(2024, 3, 31), "ANZ", 13.5),
        ]
    )
    xlsx_path = _save_and_get_path(wb, tmp_path)
    metrics_config = {"mappings": {"rbnz-dashboard": {"DBB.QIB12": "CET1 Ratio"}}}

    rows = parse_rbnz_xlsx(xlsx_path, metrics_config)

    assert len(rows) == 1
    assert rows[0]["entity"] == "ANZ"


def test_parse_rbnz_xlsx_no_mappings_returns_empty(tmp_path: Path) -> None:
    wb = _make_workbook([(datetime(2024, 3, 31), "ANZ", 13.5)])
    xlsx_path = _save_and_get_path(wb, tmp_path)

    rows = parse_rbnz_xlsx(xlsx_path, {"mappings": {}})
    assert rows == []


def test_parse_rbnz_xlsx_unmapped_series_ignored(tmp_path: Path) -> None:
    wb = _make_workbook([(datetime(2024, 3, 31), "ANZ", 13.5)])
    xlsx_path = _save_and_get_path(wb, tmp_path)
    # Mapping for a different series ID — DBB.QIB12 is in the XLSX but not mapped
    metrics_config = {"mappings": {"rbnz-dashboard": {"DBB.OTHER": "Something"}}}

    rows = parse_rbnz_xlsx(xlsx_path, metrics_config)
    assert rows == []


def test_parse_rbnz_xlsx_raises_on_missing_file(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError):
        parse_rbnz_xlsx(tmp_path / "nonexistent.xlsx", {"mappings": {}})


def test_parse_rbnz_xlsx_quarter_periods(tmp_path: Path) -> None:
    dates = [
        datetime(2024, 3, 31),  # Q1
        datetime(2024, 6, 30),  # Q2
        datetime(2024, 9, 30),  # Q3
        datetime(2024, 12, 31),  # Q4
    ]
    wb = _make_workbook([(d, "ANZ", 10.0) for d in dates])
    xlsx_path = _save_and_get_path(wb, tmp_path)
    metrics_config = {"mappings": {"rbnz-dashboard": {"DBB.QIB12": "CET1 Ratio"}}}

    rows = parse_rbnz_xlsx(xlsx_path, metrics_config)
    periods = [r["period"] for r in rows]
    assert periods == ["2024-Q1", "2024-Q2", "2024-Q3", "2024-Q4"]


# ---------------------------------------------------------------------------
# entity_type field (W-0033)
# ---------------------------------------------------------------------------


def test_parse_rbnz_xlsx_standalone_entity_has_entity_type(tmp_path: Path) -> None:
    wb = _make_workbook([(datetime(2024, 3, 31), "ANZ", 13.5)])
    xlsx_path = _save_and_get_path(wb, tmp_path)
    metrics_config = {"mappings": {"rbnz-dashboard": {"DBB.QIB12": "CET1 Ratio"}}}

    rows = parse_rbnz_xlsx(xlsx_path, metrics_config)

    assert rows[0]["entity_type"] == "standalone"


def test_parse_rbnz_xlsx_group_entity_has_entity_type(tmp_path: Path) -> None:
    wb = _make_workbook([(datetime(2024, 3, 31), "ANZ Group", 13.5)])
    xlsx_path = _save_and_get_path(wb, tmp_path)
    metrics_config = {"mappings": {"rbnz-dashboard": {"DBB.QIB12": "CET1 Ratio"}}}

    rows = parse_rbnz_xlsx(xlsx_path, metrics_config)

    assert rows[0]["entity_type"] == "group"


def test_parse_rbnz_xlsx_unknown_entity_defaults_to_standalone(tmp_path: Path) -> None:
    wb = _make_workbook([(datetime(2024, 3, 31), "UnknownBank", 5.0)])
    xlsx_path = _save_and_get_path(wb, tmp_path)
    metrics_config = {"mappings": {"rbnz-dashboard": {"DBB.QIB12": "CET1 Ratio"}}}

    rows = parse_rbnz_xlsx(xlsx_path, metrics_config)

    assert rows[0]["entity_type"] == "standalone"


def test_parse_rbnz_xlsx_all_known_group_entities(tmp_path: Path) -> None:
    groups = [
        "ANZ Group",
        "BOC Group",
        "CBA Group",
        "CCB Group",
        "ICBC Group",
        "Rabo Group",
        "WBC Group",
    ]
    data = [(datetime(2024, 3, 31), g, 10.0) for g in groups]
    wb = _make_workbook(data)
    xlsx_path = _save_and_get_path(wb, tmp_path)
    metrics_config = {"mappings": {"rbnz-dashboard": {"DBB.QIB12": "CET1 Ratio"}}}

    rows = parse_rbnz_xlsx(xlsx_path, metrics_config)

    for row in rows:
        assert row["entity_type"] == "group", f"Expected group, got standalone for {row['entity']}"
