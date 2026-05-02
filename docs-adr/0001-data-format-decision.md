---
title: "ADR-0001: Data Format Decision — CSV for Persistence"
status: accepted
date: 2026-04-27
authors: [davidamitchell]
tags: [data-format, csv, json, persistence]
supersedes: null
superseded_by: null
---

# ADR-0001: Data Format Decision — CSV for Persistence

Date: 2026-04-27
Status: Accepted (provisional — subject to revision after spike S-0001)

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
- POS-001: CSV diffs are human-readable in GitHub PR reviews
- POS-002: openpyxl → pandas → CSV is a well-understood pipeline
- POS-003: Works with Excel, Google Sheets, and Python stdlib `csv` module without extra dependencies
- POS-004: Consistent with the canonical schema defined in the operational framework

### Negative / Trade-offs
- NEG-001: CSV cannot represent nested structures; hierarchical data requires flattening
- NEG-002: Type information is lost (all values are strings); consumers must coerce types
- NEG-003: Multiple files needed if data grows beyond a single flat table

### Neutral
- NEU-001: JSON is used for the frontend consumption file; the processing step generates it from CSV
- NEU-002: Future phases may introduce Parquet if file sizes become problematic (document via new ADR)
