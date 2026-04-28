# ADR-0003: Manual Initial Load of RBNZ XLSX File

Date: 2026-04-28
Status: Accepted

## Context

The RBNZ Bank Financial Strength Dashboard XLSX is the primary data source for this pipeline. The automated fetch workflow (W-0009, `.github/workflows/fetch-data.yml`) was designed to download this file via `workflow_dispatch`. However, the automated fetch could not be validated end-to-end before the processing pipeline needed to proceed.

The file `Bank-Financial-Strength-Dashboard-Data.xlsx` was manually downloaded from the RBNZ website and committed directly to `data/` to unblock downstream work (spike S-0001, W-0006, W-0010).

## Decision

Accept the manually loaded RBNZ XLSX as the bootstrap copy for the initial pipeline run. The file is committed at `data/Bank-Financial-Strength-Dashboard-Data.xlsx`.

This is a one-time bootstrapping decision. The automated fetch workflow remains in place and must be validated and used for all future updates (see backlog item W-0016).

## Consequences

### Positive
- Downstream work (processing pipeline, metrics mapping, visualisation) can proceed immediately
- No dependency on network access or workflow runner permissions to get started
- File is version-controlled and reproducible

### Negative / Trade-offs
- The file in `data/` is a point-in-time snapshot; it will go stale without a working automated refresh
- Manual loading is not idempotent and not auditable through GitHub Actions logs
- The automated fetch workflow (W-0009) has not been end-to-end validated against the live RBNZ URL

### Neutral
- The `.gitignore` currently excludes `data/raw/*.xlsx`; the manually loaded file lives at `data/` (root of the data directory), so it is not excluded
- A future backlog item (W-0016) must validate and activate the automated fetch to replace the manual step
