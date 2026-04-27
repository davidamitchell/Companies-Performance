"""Tests for the ingestion fetch module."""

from __future__ import annotations

from src.ingestion.fetch import enforce_canonical_schema


def test_enforce_canonical_schema_valid_row() -> None:
    rows = [{"entity": "ANZ", "metric": "CET1 Ratio", "value": 13.5, "period": "2024-Q3"}]
    result = enforce_canonical_schema(rows, source="rbnz-dashboard")
    assert len(result) == 1
    row = result[0]
    assert row["entity"] == "ANZ"
    assert row["metric"] == "CET1 Ratio"
    assert row["value"] == 13.5
    assert row["period"] == "2024-Q3"
    assert row["source"] == "rbnz-dashboard"


def test_enforce_canonical_schema_skips_missing_entity() -> None:
    rows = [{"metric": "CET1 Ratio", "value": 13.5, "period": "2024-Q3"}]
    result = enforce_canonical_schema(rows, source="rbnz-dashboard")
    assert result == []


def test_enforce_canonical_schema_skips_missing_metric() -> None:
    rows = [{"entity": "ANZ", "value": 13.5, "period": "2024-Q3"}]
    result = enforce_canonical_schema(rows, source="rbnz-dashboard")
    assert result == []


def test_enforce_canonical_schema_empty_input() -> None:
    assert enforce_canonical_schema([], source="rbnz-dashboard") == []


def test_enforce_canonical_schema_strips_whitespace() -> None:
    rows = [{"entity": "  ASB  ", "metric": " NIM ", "value": 2.1, "period": "2024-Q3"}]
    result = enforce_canonical_schema(rows, source="rbnz-dashboard")
    assert result[0]["entity"] == "ASB"
    assert result[0]["metric"] == "NIM"


def test_enforce_canonical_schema_idempotent() -> None:
    """Running enforce twice on the same input produces the same output."""
    rows = [{"entity": "Westpac", "metric": "NPL Ratio", "value": 0.5, "period": "2024-Q3"}]
    first = enforce_canonical_schema(rows, source="rbnz-dashboard")
    second = enforce_canonical_schema(rows, source="rbnz-dashboard")
    assert first == second


def test_enforce_canonical_schema_does_not_map_arbitrary_keys() -> None:
    """Raw source column names (e.g. 'Bank', 'Metric') are NOT mapped here.
    Column-name mapping is the responsibility of the processing layer
    using config/metrics.yaml (pending spike S-0001).
    """
    rows = [{"Bank": "BNZ", "Metric": "LCR", "Value": 120.0, "Date": "2024-Q3"}]
    result = enforce_canonical_schema(rows, source="rbnz-dashboard")
    assert result == [], "Non-canonical keys must not be silently mapped in the ingestion layer"
