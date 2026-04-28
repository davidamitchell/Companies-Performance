# ADR-0004: RBNZ Data Contract — Canonical Schema and XLSX Mapping

**Status:** Accepted
**Date:** 2026-04-28
**Supersedes:** —
**Superseded by:** —

---

## Context

Before the processing pipeline (W-0010) could be built, the canonical data schema and the mapping from raw RBNZ XLSX columns to that schema needed to be formally documented. The RBNZ Bank Financial Strength Dashboard XLSX has a specific "wide" format that must be normalised to the pipeline's canonical "long" format. This ADR records those structural decisions.

---

## Canonical Schema

Every row in `data/processed/metrics.csv` (and `docs/data/processed/metrics.json`) conforms to the following five-field schema:

| Field    | Type    | Description                                                              |
|----------|---------|--------------------------------------------------------------------------|
| `entity` | string  | Institution name as reported by RBNZ (e.g. `ANZ`, `Westpac`)            |
| `metric` | string  | Canonical metric name from `glossary.md` (e.g. `CET1 Ratio`)            |
| `value`  | numeric | Raw value as-is from source; `null` if missing                           |
| `period` | string  | Quarter string derived from quarter-end date (e.g. `2024-Q1`)           |
| `source` | string  | Source identifier: always `rbnz-dashboard` for this source              |

No derived, rounded, or imputed values are stored. If a value is missing in the source, `null` is stored and a `WARNING` is logged.

---

## RBNZ XLSX Structure

The XLSX `Data` sheet uses a **wide format** with the following header rows (0-indexed):

| Row | Content |
|-----|---------|
| 0   | Category group (e.g. `Capital adequacy - ratios & buffer`) |
| 1   | Series name (e.g. `C2. CET1 capital ratio`) |
| 2   | Notes row (label `Notes`) |
| 3   | Unit row (e.g. `%`, `NZDm`) |
| 4   | Series ID row (`Series Id`, `Institution`, `DBB.QIB12`, …) |
| 5+  | Data rows: column 0 = quarter-end date, column 1 = institution name, columns 2+ = metric values |

### Period Format

Quarter-end dates in the XLSX are `datetime` objects (e.g. `2025-12-31`). The processing pipeline converts these to quarter strings:

| Quarter-end month | Quarter label |
|-------------------|---------------|
| March (3)         | Q1            |
| June (6)          | Q2            |
| September (9)     | Q3            |
| December (12)     | Q4            |

Example: `2024-09-30` → `2024-Q3`.

### Institution Coverage

The XLSX covers registered NZ banks from 2018-Q1 through the latest published quarter. Institutions include both standalone entities (e.g. `ANZ`, `Westpac`) and their parent groups (e.g. `ANZ Group`, `WBC Group`). Group-level entities have different regulatory reporting boundaries and are included in the canonical output but should be filtered client-side if a standalone-bank view is needed.

### Metric Mapping

Series IDs (e.g. `DBB.QIB12`) are the stable identifiers for RBNZ series. The mapping from series ID to canonical metric name is defined in `config/metrics.yaml` under the `rbnz-dashboard` key. Only mapped series are included in the processed output; all others are silently ignored.

### Missing Metrics

The following glossary metrics are **not available** in the RBNZ XLSX:

| Glossary metric       | Reason not available                                                    |
|-----------------------|-------------------------------------------------------------------------|
| `LCR`                 | Liquidity Coverage Ratio is not reported in the RBNZ Bank Dashboard   |
| `Provisioning Coverage` | Must be derived (individual provisions ÷ non-performing loans); not stored as a derived value per ADR-0001 |
| `Operating Margin`    | Requires operating income, which is not directly reported as a ratio   |

---

## Decision

1. Use the five-field canonical schema (`entity | metric | value | period | source`) for all processed output.
2. Map RBNZ series by series ID (column row 4 in the XLSX), not by series name — IDs are stable across RBNZ publication updates.
3. Convert quarter-end dates to `YYYY-QN` strings during processing.
4. Include group-level entities (e.g. `ANZ Group`) without filtering; consumers filter as needed.
5. Store `null` for missing values and log a `WARNING`; do not impute.
6. Only process series that are mapped in `config/metrics.yaml`; unmapped series are ignored.

---

## Consequences

- The processing pipeline has a well-defined input schema (RBNZ XLSX) and output schema (canonical CSV/JSON).
- Adding new metrics requires updating both `glossary.md` and `config/metrics.yaml`.
- LCR and derived metrics are deferred — open a backlog item if they are needed.
- Group vs. standalone entity distinction is a consumer concern, not a pipeline concern.
