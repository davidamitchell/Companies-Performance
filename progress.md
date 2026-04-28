# Progress

> Session logs and completion notes.
Last updated: 2026-04-28 (process-data pipeline and spike completions)

---

## Current Status

**Phase:** Phase 2 — Automated Data Pipeline (complete)
**Active work:** Phase 3 — Visualisation and Deployment
**Next phase:** Phase 4 — Qualitative Data Extraction (deferred)

---

| Phase | Title | Status |
|---|---|---|
| 1 | Standardisation and Governance | Done |
| 1.5 | Data Modelling and Source Definition | Done |
| 2 | Automated Data Pipeline | Done |
| 2.5 | Discovery / Research Spikes | Done |
| 3 | Visualisation and Deployment | In progress (W-0013 manual step remaining) |
| 4 | Qualitative Data Extraction | Deferred |

---

## Work Log

### 2026-04-28 — Frontend enhancements: default metrics, top 6 banks, historical charts (W-0017, W-0018)

**Completed:**

- **W-0017**: Default KPI metrics updated to Cost to Income Ratio, Return on Equity, Return on Assets, NIM. Top 6 standalone banks (ANZ, ASB, BNZ, Westpac, Kiwibank, Rabobank) set as default view. Cost to Income computed client-side from stored income components.
- **W-0018**: Chart.js 4.x historical time-series charts added (2×2 grid, one per key metric). All 32 quarters (2018-Q1 → 2025-Q4) rendered as line charts per bank with hover tooltips.
- Added three new RBNZ income series to `config/metrics.yaml`: Trading and Hedging Gains (DBB.QIE50), Fees and Commission Income (DBB.QIE55), Other Income (DBB.QIE57).
- Processed data regenerated: **13,900 rows** (was 11,815; +2,085 from 3 new series).
- Glossary updated: Trading and Hedging Gains, Fees and Commission Income, Other Income, Cost to Income Ratio (with ADR-0001 derivation note).
- Bank selector with brand colours, checkbox pills, and quick-select buttons (Top 6 / All / Standalone only).
- Latest Quarter Snapshot comparison table (banks as rows, key metrics as columns, ▲/▼ trend vs previous quarter).

### 2026-04-28 — Process-data pipeline and spike completions (work-through-backlog)

**Completed:**

- **S-0001**: RBNZ XLSX structure fully investigated. Findings in `learnings.md`. 112 metric columns, 22 institutions, 2018-Q1 to 2025-Q4. LCR not available. Series IDs confirmed as stable mapping key.
- **S-0002**: Additional bank disclosure sources (PDFs) assessed. Explicitly deferred — results in `learnings.md`.
- **S-0003**: Metric inconsistencies investigated — group vs. standalone entities, small-bank coverage gaps. No schema changes needed. Documented in ADR-0004 and `learnings.md`.
- **W-0006**: `config/metrics.yaml` populated with 20 RBNZ series ID → canonical metric mappings.
- **W-0008**: ADR-0004 written — formalises canonical schema, XLSX mapping strategy, period format, and missing metric documentation.
- **W-0010**: Full processing pipeline built:
  - `src/processing/parse.py` — XLSX parsing, normalisation (wide→long), duplicate detection, missing-value logging
  - `scripts/process_data.py` — entry-point script with fallback path resolution
  - `.github/workflows/process-data.yml` — workflow triggered manually or after successful fetch
  - 34 new tests added (66 total, all passing)
  - `data/processed/metrics.csv` and `docs/data/processed/metrics.json` generated (11,815 rows)
- **W-0014**: Frontend updated with real data:
  - Fixed `DATA_URL` for GitHub Pages compatibility (`data/processed/metrics.json` relative to `docs/`)
  - KPI tiles with ▲/▼ trend indicators for CET1 Ratio, NIM, Core Funding Ratio (CFR), NPL Ratio
  - Period and entity filter dropdowns
- `glossary.md` extended with 12 new RBNZ-specific metric definitions
- `docs-adr/README.md` index updated with ADR-0004

**Remaining open:**

- W-0013: Configure GitHub Pages in repo settings (one-time manual step)
- W-0016: Validate automated fetch workflow end-to-end against live RBNZ URL

### 2026-04-27 — Initial scaffold (setup-project-as-research-structure)

**Completed:**

- Repository structure initialised following `davidamitchell/Research` conventions
- `.github/skills/` submodule added pointing to `davidamitchell/Skills`
- `.github/copilot-instructions.md` created with language constraints and operational rules
- `backlog.md` populated with all phases and work items
- `progress.md` initialised (this file)
- `learnings.md` initialised with structure
- `glossary.md` created with all KPI categories and definitions
- `docs-adr/README.md` created with index and template
- ADR-0001: Data format decision (CSV for persistence)
- ADR-0002: Directory structure (aligned to Research repo, with documented deviations)
- `config/sources.yaml` populated with RBNZ dashboard XLSX source
- `config/metrics.yaml` created as placeholder
- `pyproject.toml`, `Makefile`, `.python-version`, `requirements.txt` created
- `src/logger.py`, `src/config.py`, `src/ingestion/fetch.py` created
- `tests/test_config.py`, `tests/test_ingestion.py` created — all tests pass
- `.github/workflows/ci.yml` — lint and test on every push/PR
- `.github/workflows/fetch-data.yml` — manual trigger to fetch RBNZ XLSX
- `.github/workflows/deploy-pages.yml` — deploy `docs/` to GitHub Pages
- `docs/index.html` — static frontend that consumes `data/processed/metrics.json`
