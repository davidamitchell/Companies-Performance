"""Tests for src/processing/compute_productivity.py."""

from __future__ import annotations

import csv
import json
from datetime import date
from pathlib import Path

from src.processing.compute_productivity import (
    PRODUCTIVITY_METRICS,
    _emit_ratio,
    _load_customers_csv,
    _load_employees_csv,
    _lookup_reference,
    _quarter_end_date,
    compute_productivity,
    write_productivity_csv,
    write_productivity_json,
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _write_metrics_csv(path: Path, rows: list[dict]) -> None:
    fieldnames = ["entity", "metric", "value", "period", "entity_type"]
    with path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def _write_employees_csv(path: Path, rows: list[dict]) -> None:
    fieldnames = ["bank_id", "period_end", "fte", "source", "confidence"]
    with path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def _write_customers_csv(path: Path, rows: list[dict]) -> None:
    fieldnames = [
        "bank_id",
        "period_end",
        "active_customers",
        "unique_customers",
        "estimation_method",
        "confidence",
    ]
    with path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


# ---------------------------------------------------------------------------
# _quarter_end_date
# ---------------------------------------------------------------------------


def test_quarter_end_q1() -> None:
    assert _quarter_end_date("2024-Q1") == date(2024, 3, 31)


def test_quarter_end_q2() -> None:
    assert _quarter_end_date("2024-Q2") == date(2024, 6, 30)


def test_quarter_end_q3() -> None:
    assert _quarter_end_date("2024-Q3") == date(2024, 9, 30)


def test_quarter_end_q4() -> None:
    assert _quarter_end_date("2024-Q4") == date(2024, 12, 31)


# ---------------------------------------------------------------------------
# _load_employees_csv
# ---------------------------------------------------------------------------


def test_load_employees_csv(tmp_path: Path) -> None:
    path = tmp_path / "employees.csv"
    _write_employees_csv(
        path,
        [
            {
                "bank_id": "ANZ",
                "period_end": "2023-09-30",
                "fte": "7300",
                "source": "KPMG",
                "confidence": "exact",
            },
            {
                "bank_id": "ANZ",
                "period_end": "2022-09-30",
                "fte": "7470",
                "source": "KPMG",
                "confidence": "exact",
            },
        ],
    )
    data = _load_employees_csv(path)
    assert "ANZ" in data
    # Should be sorted by period_end ascending
    assert data["ANZ"][0]["period_end"] == date(2022, 9, 30)
    assert data["ANZ"][0]["fte"] == 7470
    assert data["ANZ"][1]["period_end"] == date(2023, 9, 30)
    assert data["ANZ"][1]["fte"] == 7300


def test_load_employees_csv_multiple_banks(tmp_path: Path) -> None:
    path = tmp_path / "employees.csv"
    _write_employees_csv(
        path,
        [
            {
                "bank_id": "ANZ",
                "period_end": "2023-09-30",
                "fte": "7300",
                "source": "KPMG",
                "confidence": "exact",
            },
            {
                "bank_id": "ASB",
                "period_end": "2023-06-30",
                "fte": "4700",
                "source": "KPMG",
                "confidence": "exact",
            },
        ],
    )
    data = _load_employees_csv(path)
    assert "ANZ" in data and "ASB" in data
    assert data["ASB"][0]["fte"] == 4700


# ---------------------------------------------------------------------------
# _load_customers_csv
# ---------------------------------------------------------------------------


def test_load_customers_csv(tmp_path: Path) -> None:
    path = tmp_path / "customers.csv"
    _write_customers_csv(
        path,
        [
            {
                "bank_id": "ANZ",
                "period_end": "2023-09-30",
                "active_customers": "2800000",
                "unique_customers": "3100000",
                "estimation_method": "proxy",
                "confidence": "estimated",
            },
        ],
    )
    data = _load_customers_csv(path)
    assert "ANZ" in data
    assert data["ANZ"][0]["active_customers"] == 2800000
    assert data["ANZ"][0]["confidence"] == "estimated"


# ---------------------------------------------------------------------------
# _lookup_reference
# ---------------------------------------------------------------------------


def test_lookup_reference_exact_match() -> None:
    ref_data = {
        "ANZ": [
            {"period_end": date(2022, 9, 30), "fte": 7470, "confidence": "exact"},
            {"period_end": date(2023, 9, 30), "fte": 7300, "confidence": "exact"},
        ]
    }
    result = _lookup_reference(ref_data, "ANZ", date(2023, 9, 30))
    assert result is not None
    assert result["fte"] == 7300


def test_lookup_reference_before_first_entry() -> None:
    ref_data = {"ANZ": [{"period_end": date(2022, 9, 30), "fte": 7470, "confidence": "exact"}]}
    # Quarter ending before the first reference data point returns None
    result = _lookup_reference(ref_data, "ANZ", date(2021, 9, 30))
    assert result is None


def test_lookup_reference_midyear_quarter() -> None:
    """A Mar-end quarter should use the most recent Sep-end reference data."""
    ref_data = {
        "ANZ": [
            {"period_end": date(2022, 9, 30), "fte": 7470, "confidence": "exact"},
            {"period_end": date(2023, 9, 30), "fte": 7300, "confidence": "exact"},
        ]
    }
    # 2023-Q1 ends Mar 31 2023 — after the 2022 Sep ref, before 2023 Sep ref
    result = _lookup_reference(ref_data, "ANZ", date(2023, 3, 31))
    assert result is not None
    assert result["fte"] == 7470


def test_lookup_reference_unknown_entity() -> None:
    ref_data: dict = {}
    assert _lookup_reference(ref_data, "Nonexistent", date(2023, 9, 30)) is None


# ---------------------------------------------------------------------------
# compute_productivity
# ---------------------------------------------------------------------------

_COMMON_METRICS_ROWS = [
    {
        "entity": "ANZ",
        "metric": "Profit After Tax",
        "value": "100",
        "period": "2023-Q3",
        "entity_type": "standalone",
    },
    {
        "entity": "ANZ",
        "metric": "Net Interest Income",
        "value": "400",
        "period": "2023-Q3",
        "entity_type": "standalone",
    },
    {
        "entity": "ANZ",
        "metric": "Trading and Hedging Gains",
        "value": "20",
        "period": "2023-Q3",
        "entity_type": "standalone",
    },
    {
        "entity": "ANZ",
        "metric": "Fees and Commission Income",
        "value": "30",
        "period": "2023-Q3",
        "entity_type": "standalone",
    },
    {
        "entity": "ANZ",
        "metric": "Other Income",
        "value": "10",
        "period": "2023-Q3",
        "entity_type": "standalone",
    },
    {
        "entity": "ANZ",
        "metric": "Operating Expenses",
        "value": "200",
        "period": "2023-Q3",
        "entity_type": "standalone",
    },
]

_EMPLOYEES_ROW = {
    "bank_id": "ANZ",
    "period_end": "2023-09-30",
    "fte": "7300",
    "source": "KPMG",
    "confidence": "exact",
}

_CUSTOMERS_ROW = {
    "bank_id": "ANZ",
    "period_end": "2023-09-30",
    "active_customers": "2800000",
    "unique_customers": "3100000",
    "estimation_method": "proxy",
    "confidence": "estimated",
}


def test_compute_productivity_basic(tmp_path: Path) -> None:
    metrics_csv = tmp_path / "metrics.csv"
    emp_csv = tmp_path / "employees.csv"
    cust_csv = tmp_path / "customers.csv"
    _write_metrics_csv(metrics_csv, _COMMON_METRICS_ROWS)
    _write_employees_csv(emp_csv, [_EMPLOYEES_ROW])
    _write_customers_csv(cust_csv, [_CUSTOMERS_ROW])

    rows = compute_productivity(metrics_csv, emp_csv, cust_csv)
    assert len(rows) == 8  # 4 per-employee + 4 per-customer

    by_metric = {r["metric"]: r for r in rows}

    # Profit per Employee: 100 NZDm × 4 × 1_000_000 / 7300 = 54794.52...
    ppe = by_metric["Profit per Employee"]
    assert ppe["entity"] == "ANZ"
    assert ppe["period"] == "2023-Q3"
    assert ppe["source"] == "productivity"
    assert ppe["confidence"] == "exact"
    expected_ppe = round((100 * 4 * 1_000_000) / 7300, 2)
    assert abs(ppe["value"] - expected_ppe) < 0.01

    # Gross Income per Employee: (400+20+30+10) NZDm × 4 × 1_000_000 / 7300
    gie = by_metric["Gross Income per Employee"]
    expected_gie = round((460 * 4 * 1_000_000) / 7300, 2)
    assert abs(gie["value"] - expected_gie) < 0.01

    # Expenses per Employee: 200 NZDm × 4 × 1_000_000 / 7300
    epe = by_metric["Expenses per Employee"]
    expected_epe = round((200 * 4 * 1_000_000) / 7300, 2)
    assert abs(epe["value"] - expected_epe) < 0.01

    # Profit per Customer: 100 NZDm × 4 × 1_000_000 / 2_800_000
    ppc = by_metric["Profit per Customer"]
    assert ppc["confidence"] == "estimated"
    expected_ppc = round((100 * 4 * 1_000_000) / 2_800_000, 2)
    assert abs(ppc["value"] - expected_ppc) < 0.01

    # Cost to Income per Employee: (200/460) × 100 = 43.48%
    ctie = by_metric["Cost to Income per Employee"]
    assert ctie["entity"] == "ANZ"
    assert ctie["period"] == "2023-Q3"
    assert ctie["source"] == "productivity"
    assert ctie["confidence"] == "exact"
    expected_ctie = round((200 / 460) * 100, 2)
    assert abs(ctie["value"] - expected_ctie) < 0.01

    # Cost to Income per Customer: same formula as per-employee (denominators cancel)
    ctic = by_metric["Cost to Income per Customer"]
    assert ctic["confidence"] == "estimated"
    expected_ctic = round((200 / 460) * 100, 2)
    assert abs(ctic["value"] - expected_ctic) < 0.01


def test_compute_productivity_no_employee_data(tmp_path: Path) -> None:
    """Missing employee reference → per-employee metrics omitted, per-customer still produced."""
    metrics_csv = tmp_path / "metrics.csv"
    emp_csv = tmp_path / "employees.csv"
    cust_csv = tmp_path / "customers.csv"
    _write_metrics_csv(metrics_csv, _COMMON_METRICS_ROWS)
    _write_employees_csv(emp_csv, [])  # empty
    _write_customers_csv(cust_csv, [_CUSTOMERS_ROW])

    rows = compute_productivity(metrics_csv, emp_csv, cust_csv)
    metrics_found = {r["metric"] for r in rows}
    assert "Profit per Employee" not in metrics_found
    assert "Cost to Income per Employee" not in metrics_found
    assert "Profit per Customer" in metrics_found
    assert "Cost to Income per Customer" in metrics_found


def test_compute_productivity_null_pat(tmp_path: Path) -> None:
    """Null PAT → Profit per Employee/Customer omitted, other metrics still computed."""
    rows_with_null = [
        r if r["metric"] != "Profit After Tax" else {**r, "value": ""} for r in _COMMON_METRICS_ROWS
    ]
    metrics_csv = tmp_path / "metrics.csv"
    emp_csv = tmp_path / "employees.csv"
    cust_csv = tmp_path / "customers.csv"
    _write_metrics_csv(metrics_csv, rows_with_null)
    _write_employees_csv(emp_csv, [_EMPLOYEES_ROW])
    _write_customers_csv(cust_csv, [_CUSTOMERS_ROW])

    rows = compute_productivity(metrics_csv, emp_csv, cust_csv)
    by_metric = {r["metric"] for r in rows}
    assert "Profit per Employee" not in by_metric
    assert "Profit per Customer" not in by_metric
    assert "Expenses per Employee" in by_metric


def test_compute_productivity_group_entity_excluded(tmp_path: Path) -> None:
    """Group entities (entity_type='group') must be excluded from productivity output."""
    group_rows = [
        {**r, "entity": "ANZ Group", "entity_type": "group"} for r in _COMMON_METRICS_ROWS
    ]
    metrics_csv = tmp_path / "metrics.csv"
    emp_csv = tmp_path / "employees.csv"
    cust_csv = tmp_path / "customers.csv"
    _write_metrics_csv(metrics_csv, group_rows)
    _write_employees_csv(
        emp_csv,
        [
            {
                "bank_id": "ANZ Group",
                "period_end": "2023-09-30",
                "fte": "7300",
                "source": "KPMG",
                "confidence": "exact",
            }
        ],
    )
    _write_customers_csv(
        cust_csv,
        [
            {
                "bank_id": "ANZ Group",
                "period_end": "2023-09-30",
                "active_customers": "2800000",
                "unique_customers": "3100000",
                "estimation_method": "proxy",
                "confidence": "estimated",
            }
        ],
    )
    rows = compute_productivity(metrics_csv, emp_csv, cust_csv)
    assert len(rows) == 0


def test_compute_productivity_trading_defaults_to_zero(tmp_path: Path) -> None:
    """Null trading/fees/other should be treated as zero for gross income."""
    minimal_rows = [
        {
            "entity": "ANZ",
            "metric": "Profit After Tax",
            "value": "100",
            "period": "2023-Q3",
            "entity_type": "standalone",
        },
        {
            "entity": "ANZ",
            "metric": "Net Interest Income",
            "value": "400",
            "period": "2023-Q3",
            "entity_type": "standalone",
        },
        {
            "entity": "ANZ",
            "metric": "Operating Expenses",
            "value": "200",
            "period": "2023-Q3",
            "entity_type": "standalone",
        },
        # No trading / fees / other income rows
    ]
    metrics_csv = tmp_path / "metrics.csv"
    emp_csv = tmp_path / "employees.csv"
    cust_csv = tmp_path / "customers.csv"
    _write_metrics_csv(metrics_csv, minimal_rows)
    _write_employees_csv(emp_csv, [_EMPLOYEES_ROW])
    _write_customers_csv(cust_csv, [_CUSTOMERS_ROW])

    rows = compute_productivity(metrics_csv, emp_csv, cust_csv)
    by_metric = {r["metric"]: r for r in rows}
    # Gross income = NII only (400 NZDm)
    expected_gie = round((400 * 4 * 1_000_000) / 7300, 2)
    assert abs(by_metric["Gross Income per Employee"]["value"] - expected_gie) < 0.01
    # Cost to Income per Employee: 200/400 × 100 = 50%
    expected_ctie = round((200 / 400) * 100, 2)
    assert abs(by_metric["Cost to Income per Employee"]["value"] - expected_ctie) < 0.01


# ---------------------------------------------------------------------------
# _emit_ratio
# ---------------------------------------------------------------------------


def test_emit_ratio_basic() -> None:
    """_emit_ratio emits a percentage ratio row."""
    output: list = []
    _emit_ratio(output, "ANZ", "2024-Q1", "Cost to Income per Employee", 200.0, 460.0, "exact")
    assert len(output) == 1
    assert output[0]["metric"] == "Cost to Income per Employee"
    assert abs(output[0]["value"] - round((200 / 460) * 100, 2)) < 0.01
    assert output[0]["source"] == "productivity"
    assert output[0]["confidence"] == "exact"


def test_emit_ratio_null_numerator() -> None:
    """_emit_ratio emits nothing when numerator is None."""
    output: list = []
    _emit_ratio(output, "ANZ", "2024-Q1", "Cost to Income per Employee", None, 460.0, "exact")
    assert len(output) == 0


def test_emit_ratio_null_denominator() -> None:
    """_emit_ratio emits nothing when denominator is None."""
    output: list = []
    _emit_ratio(output, "ANZ", "2024-Q1", "Cost to Income per Employee", 200.0, None, "exact")
    assert len(output) == 0


def test_emit_ratio_zero_denominator() -> None:
    """_emit_ratio emits nothing when denominator is zero."""
    output: list = []
    _emit_ratio(output, "ANZ", "2024-Q1", "Cost to Income per Employee", 200.0, 0.0, "exact")
    assert len(output) == 0


def test_compute_productivity_ratio_null_nii(tmp_path: Path) -> None:
    """Null NII → gross income is None → cost-to-income ratio omitted."""
    rows_no_nii = [r for r in _COMMON_METRICS_ROWS if r["metric"] != "Net Interest Income"]
    metrics_csv = tmp_path / "metrics.csv"
    emp_csv = tmp_path / "employees.csv"
    cust_csv = tmp_path / "customers.csv"
    _write_metrics_csv(metrics_csv, rows_no_nii)
    _write_employees_csv(emp_csv, [_EMPLOYEES_ROW])
    _write_customers_csv(cust_csv, [_CUSTOMERS_ROW])

    rows = compute_productivity(metrics_csv, emp_csv, cust_csv)
    metrics_found = {r["metric"] for r in rows}
    assert "Cost to Income per Employee" not in metrics_found
    assert "Cost to Income per Customer" not in metrics_found


def test_write_productivity_csv(tmp_path: Path) -> None:
    rows = [
        {
            "entity": "ANZ",
            "metric": "Profit per Employee",
            "value": 54794.52,
            "period": "2023-Q3",
            "source": "productivity",
            "confidence": "exact",
        }
    ]
    dest = tmp_path / "productivity.csv"
    write_productivity_csv(rows, dest)
    assert dest.exists()
    with dest.open() as fh:
        reader = csv.DictReader(fh)
        written = list(reader)
    assert len(written) == 1
    assert written[0]["entity"] == "ANZ"
    assert written[0]["metric"] == "Profit per Employee"


def test_write_productivity_json(tmp_path: Path) -> None:
    rows = [
        {
            "entity": "ANZ",
            "metric": "Profit per Employee",
            "value": 54794.52,
            "period": "2023-Q3",
            "source": "productivity",
            "confidence": "exact",
        }
    ]
    dest = tmp_path / "productivity.json"
    write_productivity_json(rows, dest)
    assert dest.exists()
    data = json.loads(dest.read_text())
    assert len(data) == 1
    assert data[0]["value"] == 54794.52


def test_write_productivity_csv_creates_parent(tmp_path: Path) -> None:
    dest = tmp_path / "subdir" / "productivity.csv"
    write_productivity_csv([], dest)
    assert dest.exists()


def test_productivity_metrics_constant() -> None:
    assert "Profit per Employee" in PRODUCTIVITY_METRICS
    assert "Gross Income per Employee" in PRODUCTIVITY_METRICS
    assert "Expenses per Employee" in PRODUCTIVITY_METRICS
    assert "Cost to Income per Employee" in PRODUCTIVITY_METRICS
    assert "Profit per Customer" in PRODUCTIVITY_METRICS
    assert "Gross Income per Customer" in PRODUCTIVITY_METRICS
    assert "Expenses per Customer" in PRODUCTIVITY_METRICS
    assert "Cost to Income per Customer" in PRODUCTIVITY_METRICS
    assert len(PRODUCTIVITY_METRICS) == 8
