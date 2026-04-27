"""Tests for canonical row normalisation in the ingestion layer."""

from __future__ import annotations

from src.ingestion.fetch import parse_canonical_rows


def test_parse_canonical_rows_standard_keys() -> None:
    raw = [{"entity": "ANZ", "metric": "CET1 Ratio", "value": 13.5, "period": "2024-Q3"}]
    result = parse_canonical_rows(raw, source="rbnz-dashboard")
    assert len(result) == 1
    row = result[0]
    assert row["entity"] == "ANZ"
    assert row["metric"] == "CET1 Ratio"
    assert row["value"] == 13.5
    assert row["period"] == "2024-Q3"
    assert row["source"] == "rbnz-dashboard"


def test_parse_canonical_rows_alternate_keys() -> None:
    raw = [{"Bank": "BNZ", "Metric": "LCR", "Value": 120.0, "Date": "2024-Q3"}]
    result = parse_canonical_rows(raw, source="rbnz-dashboard")
    assert len(result) == 1
    assert result[0]["entity"] == "BNZ"
    assert result[0]["metric"] == "LCR"


def test_parse_canonical_rows_skips_missing_entity() -> None:
    raw = [{"metric": "CET1 Ratio", "value": 13.5, "period": "2024-Q3"}]
    result = parse_canonical_rows(raw, source="rbnz-dashboard")
    assert result == []


def test_parse_canonical_rows_skips_missing_metric() -> None:
    raw = [{"entity": "ANZ", "value": 13.5, "period": "2024-Q3"}]
    result = parse_canonical_rows(raw, source="rbnz-dashboard")
    assert result == []


def test_parse_canonical_rows_empty_input() -> None:
    assert parse_canonical_rows([], source="rbnz-dashboard") == []


def test_parse_canonical_rows_strips_whitespace() -> None:
    raw = [{"entity": "  ASB  ", "metric": " NIM ", "value": 2.1, "period": "2024-Q3"}]
    result = parse_canonical_rows(raw, source="rbnz-dashboard")
    assert result[0]["entity"] == "ASB"
    assert result[0]["metric"] == "NIM"


def test_parse_canonical_rows_idempotent() -> None:
    """Running parse twice on the same input produces the same output."""
    raw = [{"entity": "Westpac", "metric": "NPL Ratio", "value": 0.5, "period": "2024-Q3"}]
    first = parse_canonical_rows(raw, source="rbnz-dashboard")
    second = parse_canonical_rows(raw, source="rbnz-dashboard")
    assert first == second
