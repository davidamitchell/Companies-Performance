"""Compute per-employee and per-customer productivity metrics.

Reads:
- ``data/processed/metrics.csv``       — canonical RBNZ quarterly rows
- ``data/reference/employees.csv``     — annual FTE counts per bank
- ``data/reference/customers.csv``     — annual active customer estimates per bank

Outputs canonical rows in the schema:

    entity      — institution name (e.g. "ANZ")
    metric      — canonical metric name (see PRODUCTIVITY_METRICS)
    value       — computed value (rounded to 2 dp)
    period      — quarter string (e.g. "2024-Q3")
    source      — "productivity"
    confidence  — "exact" / "triangulated" / "estimated" (from reference data)

The six metrics are:
- Profit per Employee (NZD/FTE, annualised)
- Gross Income per Employee (NZD/FTE, annualised)
- Expenses per Employee (NZD/FTE, annualised)
- Profit per Customer (NZD/customer, annualised)
- Gross Income per Customer (NZD/customer, annualised)
- Expenses per Customer (NZD/customer, annualised)

Annualisation: quarterly NZDm values are multiplied by 4 then divided by the
denominator. The divisor is taken from the most recent annual reference data
point at or before the quarter-end date.

Missing denominators produce a WARNING and no output row for that metric/period.
"""

from __future__ import annotations

import csv
import json
from datetime import date
from pathlib import Path
from typing import Any

from src.logger import get_logger

logger = get_logger(__name__)

_SOURCE_ID = "productivity"

# Canonical metric names produced by this module
PRODUCTIVITY_METRICS = (
    "Profit per Employee",
    "Gross Income per Employee",
    "Expenses per Employee",
    "Profit per Customer",
    "Gross Income per Customer",
    "Expenses per Customer",
)

# Confidence tier ordering (lower index = higher quality)
_CONFIDENCE_RANK = {"exact": 0, "triangulated": 1, "estimated": 2}

# Component metrics required from the RBNZ quarterly data
_PAT_METRIC = "Profit After Tax"
_OPEX_METRIC = "Operating Expenses"
_NII_METRIC = "Net Interest Income"
_TRADING_METRIC = "Trading and Hedging Gains"
_FEES_METRIC = "Fees and Commission Income"
_OTHER_METRIC = "Other Income"

# Quarters per annum for annualisation
_ANNUALISE = 4


def _parse_date(date_str: str) -> date:
    """Parse a YYYY-MM-DD string to a date object."""
    y, m, d = date_str.split("-")
    return date(int(y), int(m), int(d))


def _quarter_end_date(period: str) -> date:
    """Return the quarter-end date for a period string like '2024-Q3'.

    Q1 → Mar 31, Q2 → Jun 30, Q3 → Sep 30, Q4 → Dec 31.
    """
    year_str, q_str = period.split("-")
    year = int(year_str)
    q = int(q_str[1])
    month_end = {1: (3, 31), 2: (6, 30), 3: (9, 30), 4: (12, 31)}
    month, day = month_end[q]
    return date(year, month, day)


def _load_metrics_csv(path: Path) -> list[dict[str, Any]]:
    """Load the canonical metrics CSV into a list of row dicts."""
    rows: list[dict[str, Any]] = []
    with path.open(newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        for row in reader:
            val = row.get("value", "")
            rows.append(
                {
                    "entity": row["entity"],
                    "metric": row["metric"],
                    "value": float(val) if val not in ("", None) else None,
                    "period": row["period"],
                    "entity_type": row.get("entity_type", ""),
                }
            )
    return rows


def _load_employees_csv(path: Path) -> dict[str, list[dict[str, Any]]]:
    """Load employees.csv and return a dict keyed by bank_id.

    Each value is a list of rows sorted by period_end ascending.
    """
    data: dict[str, list[dict[str, Any]]] = {}
    with path.open(newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        for row in reader:
            bank_id = row["bank_id"]
            data.setdefault(bank_id, []).append(
                {
                    "period_end": _parse_date(row["period_end"]),
                    "fte": int(row["fte"]),
                    "source": row["source"],
                    "confidence": row["confidence"],
                }
            )
    for rows in data.values():
        rows.sort(key=lambda r: r["period_end"])
    return data


def _load_customers_csv(path: Path) -> dict[str, list[dict[str, Any]]]:
    """Load customers.csv and return a dict keyed by bank_id.

    Each value is a list of rows sorted by period_end ascending.
    """
    data: dict[str, list[dict[str, Any]]] = {}
    with path.open(newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        for row in reader:
            bank_id = row["bank_id"]
            data.setdefault(bank_id, []).append(
                {
                    "period_end": _parse_date(row["period_end"]),
                    "active_customers": int(row["active_customers"]),
                    "source": row.get("estimation_method", row.get("source", "")),
                    "confidence": row["confidence"],
                }
            )
    for rows in data.values():
        rows.sort(key=lambda r: r["period_end"])
    return data


def _lookup_reference(
    ref_data: dict[str, list[dict[str, Any]]],
    entity: str,
    quarter_end: date,
) -> dict[str, Any] | None:
    """Find the most recent reference data point for an entity at or before quarter_end.

    Returns None if no matching reference data exists.
    """
    rows = ref_data.get(entity)
    if not rows:
        return None
    # Find the latest row whose period_end is at or before the quarter_end
    best = None
    for row in rows:
        if row["period_end"] <= quarter_end:
            best = row
        else:
            break
    return best


def _build_lookup(rows: list[dict[str, Any]]) -> dict[str, dict[str, dict[str, float | None]]]:
    """Build a nested lookup: entity → period → metric → value."""
    lookup: dict[str, dict[str, dict[str, float | None]]] = {}
    for row in rows:
        entity = row["entity"]
        period = row["period"]
        metric = row["metric"]
        value = row["value"]
        lookup.setdefault(entity, {}).setdefault(period, {})[metric] = value
    return lookup


def _worst_confidence(*confs: str) -> str:
    """Return the lowest-quality (highest rank number) confidence tier."""
    return max(confs, key=lambda c: _CONFIDENCE_RANK.get(c, 99))


def compute_productivity(
    metrics_path: Path,
    employees_path: Path,
    customers_path: Path,
) -> list[dict[str, Any]]:
    """Compute per-employee and per-customer productivity metrics.

    Parameters
    ----------
    metrics_path:
        Path to ``data/processed/metrics.csv``.
    employees_path:
        Path to ``data/reference/employees.csv``.
    customers_path:
        Path to ``data/reference/customers.csv``.

    Returns
    -------
    list[dict]
        Canonical rows with keys: entity, metric, value, period, source, confidence.
    """
    logger.info("Loading metrics from %s", metrics_path)
    all_rows = _load_metrics_csv(metrics_path)

    logger.info("Loading employee reference data")
    employees = _load_employees_csv(employees_path)

    logger.info("Loading customer reference data")
    customers = _load_customers_csv(customers_path)

    lookup = _build_lookup(all_rows)

    # Determine which entities to process.
    # Use standalone entities only if the entity_type column is populated;
    # otherwise fall back to using all entities in the reference data.
    has_entity_type = any(r.get("entity_type") for r in all_rows)
    if has_entity_type:
        standalone_entities = sorted(
            {r["entity"] for r in all_rows if r.get("entity_type", "") == "standalone"}
        )
    else:
        standalone_entities = sorted(employees.keys())

    all_periods = sorted({r["period"] for r in all_rows})
    output: list[dict[str, Any]] = []

    for entity in standalone_entities:
        if entity not in lookup:
            continue

        for period in all_periods:
            period_data = lookup[entity].get(period, {})
            try:
                qend = _quarter_end_date(period)
            except (ValueError, KeyError):
                logger.warning("Cannot parse quarter date for period %r; skipping", period)
                continue

            # --- Gather source metrics ---
            pat = period_data.get(_PAT_METRIC)
            opex = period_data.get(_OPEX_METRIC)
            nii = period_data.get(_NII_METRIC)
            trading = period_data.get(_TRADING_METRIC) or 0.0
            fees = period_data.get(_FEES_METRIC) or 0.0
            other_inc = period_data.get(_OTHER_METRIC) or 0.0

            # Total operating income (NZDm) — same derivation as Cost-to-Income
            gross_income: float | None = None
            if nii is not None:
                gross_income = (nii or 0.0) + trading + fees + other_inc

            # Annualise quarterly NZDm → NZDm per annum
            pat_ann = pat * _ANNUALISE if pat is not None else None
            opex_ann = opex * _ANNUALISE if opex is not None else None
            gross_income_ann = gross_income * _ANNUALISE if gross_income is not None else None

            # --- Employee reference ---
            emp_ref = _lookup_reference(employees, entity, qend)

            if emp_ref is None:
                # Bank not in reference data or no data point before this quarter (expected
                # for smaller institutions and early periods before reference coverage)
                logger.warning(
                    "No employee reference for institution at %s; per-employee skipped", period
                )
            else:
                fte = emp_ref["fte"]
                emp_conf = emp_ref["confidence"]

                # NZDm × 1_000_000 / FTE → NZD per FTE
                _emit_metric(output, entity, period, "Profit per Employee", pat_ann, fte, emp_conf)
                _emit_metric(
                    output,
                    entity,
                    period,
                    "Gross Income per Employee",
                    gross_income_ann,
                    fte,
                    emp_conf,
                )
                _emit_metric(
                    output, entity, period, "Expenses per Employee", opex_ann, fte, emp_conf
                )

            # --- Customer reference ---
            cust_ref = _lookup_reference(customers, entity, qend)

            if cust_ref is None:
                # Bank not in reference data or no data point before this quarter (expected
                # for smaller institutions and early periods before reference coverage)
                logger.warning(
                    "No customer reference for institution at %s; per-customer skipped", period
                )
            else:
                active_cust = cust_ref["active_customers"]
                cust_conf = cust_ref["confidence"]

                # NZDm × 1_000_000 / customers → NZD per customer
                _emit_metric(
                    output, entity, period, "Profit per Customer", pat_ann, active_cust, cust_conf
                )
                _emit_metric(
                    output,
                    entity,
                    period,
                    "Gross Income per Customer",
                    gross_income_ann,
                    active_cust,
                    cust_conf,
                )
                _emit_metric(
                    output,
                    entity,
                    period,
                    "Expenses per Customer",
                    opex_ann,
                    active_cust,
                    cust_conf,
                )

    logger.info("Productivity computation complete: %d rows", len(output))
    return output


def _emit_metric(
    output: list[dict[str, Any]],
    entity: str,
    period: str,
    metric: str,
    numerator_nzdm: float | None,
    denominator: int,
    confidence: str,
) -> None:
    """Compute NZD/unit and append to output if numerator is non-null."""
    if numerator_nzdm is None:
        return
    if denominator == 0:
        logger.warning("Zero denominator for metric=%r %s; skipping", metric, period)
        return
    # Convert NZDm → NZD and divide by denominator
    value = round((numerator_nzdm * 1_000_000) / denominator, 2)
    output.append(
        {
            "entity": entity,
            "metric": metric,
            "value": value,
            "period": period,
            "source": _SOURCE_ID,
            "confidence": confidence,
        }
    )


def write_productivity_csv(rows: list[dict[str, Any]], dest: Path) -> None:
    """Write productivity rows to a CSV file."""
    dest.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = ["entity", "metric", "value", "period", "source", "confidence"]
    with dest.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({k: row.get(k, "") for k in fieldnames})
    logger.info("Written %d rows to %s", len(rows), dest)


def write_productivity_json(rows: list[dict[str, Any]], dest: Path) -> None:
    """Write productivity rows to a JSON file for frontend consumption."""
    dest.parent.mkdir(parents=True, exist_ok=True)
    with dest.open("w", encoding="utf-8") as fh:
        json.dump(rows, fh, separators=(",", ":"))
    logger.info("Written %d rows to %s", len(rows), dest)
