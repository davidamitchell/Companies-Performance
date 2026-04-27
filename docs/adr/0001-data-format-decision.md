# ADR-0001: Data Format Decision — CSV for Persistence

Date: 2026-04-27
Status: Accepted

## Context

The pipeline ingests financial data (initially from the RBNZ Bank Financial Strength Dashboard XLSX) and must persist normalised data in the repository. The data must be:

- Human-readable (reviewable in diffs and GitHub UI)
- Machine-readable (consumable by Python and the static frontend)
- Consistently structured (canonical schema: `entity | metric | value | period | source`)
- Compatible with GitHub's file size limits

Two primary candidates are CSV and JSON. A mixed approach (CSV for tabular data, JSON for metadata/indexes) is also feasible.

## Decision

Use **CSV** as the primary persistence format for normalised metric rows.

- Each dataset is a flat CSV file with the canonical schema columns.
- Metadata files (e.g. data manifests, frontend consumption indexes) use JSON.
- Files are stored under `data/processed/`.

The static frontend consumes a JSON representation (`data/processed/metrics.json`) generated from the CSV by the processing step.

## Consequences

### Positive
- CSV diffs are human-readable in GitHub PR reviews
- openpyxl → pandas → CSV is a well-understood pipeline
- Works with Excel, Google Sheets, and Python stdlib `csv` module without extra dependencies
- Consistent with the canonical schema defined in the operational framework

### Negative / Trade-offs
- CSV cannot represent nested structures; hierarchical data requires flattening
- Type information is lost (all values are strings); consumers must coerce types
- Multiple files needed if data grows beyond a single flat table

### Neutral
- JSON is used for the frontend consumption file; the processing step generates it from CSV
- Future phases may introduce Parquet if file sizes become problematic (document via new ADR)
