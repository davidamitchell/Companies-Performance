# Backlog

> This file tracks **pipeline and infrastructure** work — data ingestion, processing, visualisation, and governance.
> Discovery spike outputs are recorded in `learnings.md`.

---

## Phase 1: Standardisation and Governance

### W-0001

status: done
created: 2026-04-27
updated: 2026-04-27

### Outcome

Repository scaffold exists: `backlog.md`, `progress.md`, `learnings.md`, `glossary.md`, `.github/copilot-instructions.md`, `docs-adr/README.md`, ADR-0001, ADR-0002.

### Context

Foundation required before any other work can begin.

---

### W-0002

status: done
created: 2026-04-27
updated: 2026-04-27

### Outcome

`docs-adr/` exists with an index file, ADR-0001 (data format), and ADR-0002 (directory structure) following MADR format.

### Context

ADRs capture design decisions before context is lost. Mirrors Research repo convention.

---

### W-0003

status: done
created: 2026-04-27
updated: 2026-04-27

### Outcome

`pyproject.toml`, `requirements.txt`, and `.python-version` are present; `pip install -e ".[dev]"` succeeds and `pytest tests/` passes.

### Context

Python project tooling defined in `pyproject.toml` as the single source of truth.

---

### W-0004

status: done
created: 2026-04-27
updated: 2026-04-27

### Outcome

`.github/skills/` is initialised as a git submodule of `davidamitchell/Skills`. `.gitmodules` is committed.

### Context

Skills submodule aligns agent instruction patterns with the Research repo.

---

### W-0005

status: done
created: 2026-04-27
updated: 2026-04-27

### Outcome

`glossary.md` is populated with KPI placeholders across all four categories: Financial Resilience, Growth Momentum, Structural Moat, Strategic Evolution.

### Context

Foundational definitions required before metrics can be used in code or config.

---

### W-0006

status: done
created: 2026-04-27
updated: 2026-04-28

### Outcome

`config/metrics.yaml` is populated with initial field mappings from RBNZ XLSX series IDs to canonical glossary terms.

### Context

Requires RBNZ XLSX to be fetched and inspected first (see W-0011). Depends on spike S-0001.

---

## Phase 1.5: Data Modelling and Source Definition

### W-0007

status: done
created: 2026-04-27
updated: 2026-04-27

### Outcome

`config/sources.yaml` is populated with the RBNZ dashboard XLSX source URL and output path. `src/config.py` loads and validates the file.

### Context

Canonical source registry before any fetching begins.

---

### W-0008

status: done
created: 2026-04-27
updated: 2026-04-28

### Outcome

ADR-0004 documents the canonical data structure assumptions (`entity | metric | value | period | source`) and the RBNZ XLSX mapping strategy (by series ID). Group vs. standalone entity distinction is documented.

### Context

Temporary data contract must be formalised before the processing pipeline is built. Depends on spike S-0001.

---

## Phase 2: Automated Data Pipeline (GitHub Actions)

### W-0009

status: done
created: 2026-04-27
updated: 2026-04-27

### Outcome

`.github/workflows/fetch-data.yml` exists with a `workflow_dispatch` trigger; running it downloads the RBNZ XLSX to `data/raw/` and commits idempotently.

### Context

Manual trigger only. No polling or scheduling.

---

### W-0010

status: done
created: 2026-04-27
updated: 2026-04-28

### Outcome

`.github/workflows/process-data.yml` exists; running it parses the RBNZ XLSX, normalises rows into the canonical schema, validates data quality (missing values, duplicate detection), and writes `data/processed/metrics.csv` and `docs/data/processed/metrics.json`.

### Context

Depends on W-0009 (raw file present) and W-0006 (metrics mapping populated).

---

### W-0011

status: done
created: 2026-04-27
updated: 2026-04-28

### Outcome

The RBNZ XLSX (`Bank-Financial-Strength-Dashboard-Data.xlsx`) is present in `data/` and available for the processing pipeline.

### Context

The automated fetch workflow (W-0009) was not validated end-to-end before downstream work needed to proceed. The file was manually downloaded from the RBNZ website and committed directly to `data/` to unblock the pipeline. Documented in ADR-0003. Automated fetch must be validated and re-enabled in W-0016.

---

## Phase 2.5: Discovery / Research Spikes

### S-0001

status: done
created: 2026-04-27
updated: 2026-04-28

### Outcome

RBNZ XLSX structure investigated. Findings recorded in `learnings.md`. `config/metrics.yaml` updated with initial mappings. ADR-0004 written. Glossary extended with RBNZ-specific metrics.

### Context

Must result in: backlog update, or ADR, or explicit no-action decision.

---

### S-0002

status: done
created: 2026-04-27
updated: 2026-04-28

### Outcome

Feasibility of additional bank disclosure sources (PDF annual reports) investigated. Findings recorded in `learnings.md`. Deferred pending Phase 3 completion and LLM extraction tooling (W-0015).

### Context

Must result in: backlog update, or ADR, or explicit no-action decision.

---

### S-0003

status: done
created: 2026-04-27
updated: 2026-04-28

### Outcome

Metric inconsistencies across banks investigated. Findings recorded in `learnings.md`: group vs. standalone entities, smaller bank coverage gaps. No schema changes required; consumer filtering is responsible for group/standalone distinction. Documented in ADR-0004.

### Context

Must result in: backlog update, or ADR, or explicit no-action decision.

---

### W-0016

status: wont-do
created: 2026-04-28
updated: 2026-04-30

### Outcome

Won't do: Kiwibank and Westpac CDNs block pipeline downloads (WAF / timeout). Manual intervention required for both; automated fetch not fixable without a change in bank infrastructure. W-0009 already validates the RBNZ XLSX fetch; this item is superseded by that.

---

## Phase 3: Visualisation and Deployment

### W-0012

status: done
created: 2026-04-27
updated: 2026-04-27

### Outcome

`docs/index.html` is a static page that loads `data/processed/metrics.json` and displays basic metrics per bank (entity cards with metric/value/period table). `.github/workflows/deploy-pages.yml` deploys `docs/` to GitHub Pages.

### Context

Minimal viable frontend. No build step. Data consumed from repo-stored JSON.

---

### W-0013

status: open
created: 2026-04-27
updated: 2026-04-27

### Outcome

GitHub Pages is configured in repo settings (Settings → Pages → Deploy from branch: `main` / `docs/`). The site is accessible at the Pages URL.

### Context

One-time manual configuration in repo settings.

---

### W-0014

status: done
created: 2026-04-27
updated: 2026-04-28

### Outcome

Frontend displays real data from the first pipeline run. Key metric tiles with trend indicators (▲/▼) added for CET1 Ratio, NIM, Core Funding Ratio (CFR), and NPL Ratio. Period and entity filters added. DATA_URL fixed for GitHub Pages.

### Context

Depends on W-0010 and W-0013.

---

### W-0017

status: done
created: 2026-04-28
updated: 2026-04-28

### Outcome

Default KPI metrics updated to: Cost to Income Ratio, Return on Equity, Return on Assets, NIM. Default entity view limited to top 6 standalone banks by total assets: ANZ, ASB, BNZ, Westpac, Kiwibank, Rabobank. Cost to Income Ratio computed client-side from stored income component series (NII + Trading + Fees + Other Income) and Operating Expenses.

### Context

Cost to Income Ratio is not a pre-calculated series in the RBNZ XLSX. Three income component series added to `config/metrics.yaml` (Trading and Hedging Gains, Fees and Commission Income, Other Income) to enable client-side derivation. Per ADR-0001, derived values are not stored in the canonical data files; computation is performed in the frontend.

---

### W-0018

status: done
created: 2026-04-28
updated: 2026-04-28

### Outcome

Historical time-series line charts added to the frontend. One chart per key metric (Cost to Income Ratio, Return on Equity, Return on Assets, NIM) showing all visible banks across all available quarters. Chart.js loaded from CDN. Charts are responsive and replace the period-based card view as the primary view.

### Context

Depends on W-0017 and W-0010. Requires processed data to include all 32 quarters.

---

### W-0023

status: done
created: 2026-04-29
updated: 2026-04-29

### Outcome

The GitHub Pages site (`docs/`) is styled to match the davidamitchell design system used in
[Research](https://davidamitchell.github.io/Research/) and
[Latest-developments](https://davidamitchell.github.io/Latest-developments-/).
Visual language: dark background (`#0d0d0d`), IBM Plex Mono typeface (from Google Fonts),
teal (`#00C3A5`) accent, border-only cards (no box-shadow, no border-radius), fixed top nav.
Shared design tokens extracted to `docs/css/theme.css`. Chart.js charts updated to dark mode defaults.

### Context

Site was previously styled with light background and system UI fonts, inconsistent with
the design system used across other davidamitchell GitHub Pages sites.

---

## Phase 3.5: Frontend Enhancements

### W-0019

status: done
created: 2026-04-28
updated: 2026-04-30

### Outcome

`src/processing/parse_ocr.py` parses the RBNZ B2 XLSX (monthly OCR) and outputs quarterly canonical rows. `scripts/process_ocr.py` writes `data/processed/ocr.csv` and `docs/data/processed/ocr.json`. `docs/index.html` loads `ocr.json` and overlays the OCR as a teal dashed line on the NIM chart with a right-side y-axis. Graceful degradation: NIM chart renders normally if `ocr.json` is absent.

---

### W-0020

status: open
created: 2026-04-28
updated: 2026-04-28

### Outcome

Each chart in the frontend can be expanded to full-screen. A focus/zoom button (e.g. ⛶) is rendered in the top-right corner of every Chart.js canvas. Clicking it opens the chart in a modal overlay that fills the viewport, re-rendering the chart at the larger size. Pressing Escape or clicking outside the modal closes it. No additional dependencies beyond Chart.js (already loaded).

### Context

Charts are currently small within the responsive grid. Full-screen mode allows detailed inspection of individual series without leaving the page. The implementation should be purely client-side JS within `docs/index.html`; no build step.

---

### W-0021

status: open
created: 2026-04-28
updated: 2026-04-28

### Outcome

The static site gains three additional pages alongside `docs/index.html`:
- `docs/glossary.html` — renders all metric definitions from `glossary.md`, linking back to the main dashboard.
- `docs/methodology.html` — explains how each KPI is calculated, which RBNZ series IDs are used, and which metrics are derived vs. stored (referencing ADR-0001).
- `docs/lineage.html` — documents the data model (canonical schema `entity | metric | value | period | source`), the pipeline stages (fetch → process → publish), and the source-to-output file lineage.

Navigation links to all three pages are added to the header/footer of `docs/index.html`.

### Context

Transparency pages are a prerequisite for external users to trust the data. Content is sourced from `glossary.md`, `docs-adr/`, and `learnings.md`; no new data pipeline work is required. All pages must be static HTML with no build step.

---

### W-0022

status: done
created: 2026-04-28
updated: 2026-04-30

### Outcome

Date-range filter bar added above charts in `docs/index.html`. Four presets: `Last 4Q`, `Last 8Q`, `Last 16Q`, `All` (default). Active preset styled with teal border (`#00C3A5`). Clicking a preset filters ALL charts and the snapshot table simultaneously (client-side on already-loaded JSON). Selected preset persists in `localStorage` key `"rangePreset"` and is restored on page load. Entity filter operates independently.

---

## Phase 4: Qualitative Data Extraction (Deferred)

### W-0015

status: done
created: 2026-04-27
updated: 2026-04-30

### Outcome

`src/processing/extract_disclosures.py` extracts 10 quantitative metrics (Net Interest Income, Total Operating Income, Operating Expenses, Profit After Tax, Total Assets, Net Loans and Advances, Deposits, Equity, CET1 Ratio, Total Capital Ratio) from bank disclosure PDFs using `pdfplumber` text extraction. Normalises values: brackets = negative, comma thousands, NZD thousands scale. Outputs canonical rows (entity | metric | value | period | source). `scripts/process_disclosures.py` writes `data/processed/disclosures.csv` and `docs/data/processed/disclosures.json`. 34 tests in `tests/test_extract_disclosures.py`.

---

## Phase 5: Labour and Customer Productivity Metrics

### S-0005

status: open
created: 2026-05-01
updated: 2026-05-01

### Outcome

FTE employee count data sourcing investigated for the six major NZ banks (ANZ, ASB, BNZ, Westpac, Kiwibank, Rabobank). Findings recorded in `learnings.md`. A reference employee table committed to `data/reference/employees.csv` with columns `bank_id | period_end | fte | source | confidence` (confidence: `exact` / `triangulated` / `estimated`). Backlog updated with any follow-on implementation items.

### Context

Per-employee productivity metrics (W-0025) cannot be computed without reliable FTE data. This spike establishes which banks disclose FTE in their General Disclosure Statements and where triangulation is required. Sources to assess:
1. General Disclosure Statements / annual reports — FTE disclosed as a note or in the operational section.
2. Stats NZ Business Demography — employee bands (linked via NZBN); provides a floor/ceiling range.
3. KPMG FIPS annual banking survey — typically reports system-wide and per-bank FTE.
4. NZBA benchmarks — aggregate ~29,000 FTE (majors ~26,000); useful for sanity checks.
5. Historical public estimates: ANZ NZ ~9,000; ASB ~6,000; BNZ ~5,000; Westpac NZ ~5,000; Kiwibank ~2,500; Rabobank ~400.

Must result in: `data/reference/employees.csv`, `learnings.md` update, backlog update or explicit no-action.

---

### S-0006

status: open
created: 2026-05-01
updated: 2026-05-01

### Outcome

Active retail customer count estimation investigated for the six major NZ banks. Findings recorded in `learnings.md`. A reference customer table committed to `data/reference/customers.csv` with columns `bank_id | period_end | active_customers | unique_customers | estimation_method | confidence`. Backlog updated with any follow-on implementation items.

### Context

Per-customer productivity metrics (W-0026) require an active customer denominator. No single authoritative public source exists; estimation is required. Sources to assess in order of reliability:
1. NZBA Retail Banking Insights — industry-level unique retail customers (~10M as at H2 2024; ~9.97M).
2. Individual bank General Disclosure Statements — some disclose retail customers, active digital users, or account volumes.
3. Account-to-customer proxy: total accounts ÷ 2–4 (typical accounts-per-customer ratio for NZ banks).
4. Deposit proxy: retail deposits ÷ assumed average deposit per customer ($10k–$30k range) — macro sanity check only.
5. Active adjustment: apply 75–90% of unique customer count to approximate "transacted within 90–180 days" definition.
6. Published customer figures: Kiwibank >1M; majors each typically 0.8M–2M+ active retail.

Must result in: `data/reference/customers.csv`, `learnings.md` update, backlog update or explicit no-action.

---

### W-0024

status: open
created: 2026-05-01
updated: 2026-05-01

### Outcome

`data/reference/` directory created with two canonical reference files:
- `data/reference/employees.csv` — FTE employee counts per bank per period (output of S-0005).
- `data/reference/customers.csv` — active retail customer estimates per bank per period (output of S-0006).

Both files follow the canonical schema extension: `bank_id | period_end | value | source | confidence`. A `config/reference.yaml` file documents each reference file's schema, provenance, and update cadence. Reference files are committed to git (not gitignored) and updated manually when new bank reports are published.

### Context

Depends on S-0005 and S-0006. Reference files are static inputs to the processing pipeline (W-0025, W-0026); they are not fetched automatically because no machine-readable public API exists for FTE or active-customer data.

---

### W-0025

status: open
created: 2026-05-01
updated: 2026-05-01

### Outcome

`src/processing/compute_productivity.py` reads the canonical metrics output (`data/processed/metrics.csv`) and the reference files (`data/reference/employees.csv`, `data/reference/customers.csv`) and computes six productivity metrics per bank per period:

- Profit per Employee = Profit After Tax ÷ FTE Employees (NZD/FTE, annualised)
- Gross Income per Employee = Total Operating Income ÷ FTE Employees (NZD/FTE, annualised)
- Expenses per Employee = Operating Expenses ÷ FTE Employees (NZD/FTE, annualised)
- Profit per Customer = Profit After Tax ÷ Active Retail Customers (NZD/customer, annualised)
- Gross Income per Customer = Total Operating Income ÷ Active Retail Customers (NZD/customer, annualised)
- Expenses per Customer = Operating Expenses ÷ Active Retail Customers (NZD/customer, annualised)

Output rows follow the canonical schema (`entity | metric | value | period | source`). Where the employee or customer denominator is triangulated or estimated, the output row includes a `confidence` column (`exact` / `triangulated` / `estimated`). Missing denominators produce a `WARNING` log and no row (no imputation). `scripts/compute_productivity.py` writes `data/processed/productivity.csv` and `docs/data/processed/productivity.json`. Tests in `tests/test_compute_productivity.py`.

### Context

Depends on W-0024 (reference files populated), W-0010 (metrics.csv present), and S-0005/S-0006 (denominators validated). Annualisation: half-year values × 2; quarterly values × 4. Half-year is the standard NZ bank disclosure period, so most values will use ×2 annualisation. Log a `WARNING` if annualisation factor cannot be determined from the period string.

---

### W-0026

status: open
created: 2026-05-01
updated: 2026-05-01

### Outcome

`.github/workflows/compute-productivity.yml` added. The workflow runs after `process-data.yml` succeeds (or can be triggered manually with `workflow_dispatch`). It runs `python scripts/compute_productivity.py` and commits `data/processed/productivity.csv` and `docs/data/processed/productivity.json` idempotently (using `git diff --cached --quiet` guard).

### Context

Depends on W-0025. Follows the same idempotent commit pattern as `process-data.yml` and `fetch-data.yml`.

---

### W-0027

status: open
created: 2026-05-01
updated: 2026-05-01

### Outcome

Frontend `docs/index.html` gains a new **Productivity** tab alongside the existing metric categories. The tab displays two chart groups:

- **Per-employee charts**: Profit per Employee, Gross Income per Employee, Expenses per Employee — one line chart per metric, all six banks, all available periods.
- **Per-customer charts**: Profit per Customer, Gross Income per Customer, Expenses per Customer — same layout.

Charts follow the existing dark-mode Chart.js pattern (IBM Plex Mono, teal accent, `#252b33` border). A confidence badge (🔵 Exact / 🟡 Triangulated / 🔴 Estimated) is shown per bank per period in tooltips, sourced from the `confidence` field in `productivity.json`. If `productivity.json` is absent or all denominators for a bank are missing, that bank's series is silently omitted from productivity charts (graceful degradation). A data-sources note is added below the charts explaining triangulation methodology and linking to `docs/methodology.html`.

### Context

Depends on W-0026 (productivity.json published) and W-0023 (shared design system in place). Consistent with W-0021 (methodology page) which should reference the triangulation approach documented in S-0005 and S-0006.

---
