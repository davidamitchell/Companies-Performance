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

## Phase 4: Disclosure Pipeline (Complete)

### W-0015

status: done
created: 2026-04-27
updated: 2026-04-30

### Outcome

`src/processing/extract_disclosures.py` extracts 10 quantitative metrics (Net Interest Income, Total Operating Income, Operating Expenses, Profit After Tax, Total Assets, Net Loans and Advances, Deposits, Equity, CET1 Ratio, Total Capital Ratio) from bank disclosure PDFs using `pdfplumber` text extraction. Normalises values: brackets = negative, comma thousands, NZD thousands scale. Outputs canonical rows (entity | metric | value | period | source). `scripts/process_disclosures.py` writes `data/processed/disclosures.csv` and `docs/data/processed/disclosures.json`. 34 tests in `tests/test_extract_disclosures.py`.

---

## Phase 4.5: Disclosure Data Integration

### W-0024

status: open
created: 2026-04-30
updated: 2026-04-30

### Outcome

`scripts/process_disclosures.py` runs end-to-end across all PDFs in `data/raw/financial_disclosures/` that have a valid `.meta.json` sidecar. Produces `data/processed/disclosures.csv` and `docs/data/processed/disclosure_metrics.json` containing extracted metric rows in the canonical schema (`entity | metric | value | period | source`). A summary of extracted-vs-null counts is logged per bank per period.

### Context

W-0015 built and tested the extraction pipeline against sample PDFs. The full corpus (ANZ ×3, ASB ×15, BNZ ×7, Kiwibank ×14, Rabobank ×4) is committed to the repo. Running end-to-end validates the regex patterns against all committed reports and surfaces any format differences in older documents.

Challenge: Rabobank balance sheet (page 35 of the 2022 report) is image-based — confirmed zero extractable characters by S-0004. Balance sheet metrics (Total Assets, Net Loans, Deposits) will be null for Rabobank. Log WARNING and store null. Do not attempt OCR here — see S-0008 if the gap is later deemed worth closing.

---

### W-0025

status: open
created: 2026-04-30
updated: 2026-04-30

### Outcome

`docs/disclosures.html` (currently an index page showing PDF coverage) gains a chart panel that loads `docs/data/processed/disclosure_metrics.json` and displays key annual metrics (Profit After Tax, Operating Expenses, Total Assets, CET1 Ratio) as line charts per bank. Banks with different fiscal year ends (ANZ/BNZ: Sep, ASB/Kiwibank: Jun, Rabobank: Dec) are rendered on a shared annual axis labelled by `period_end` year. A note on the page explains the differing year-end dates. Period-type filter (Full year / Half year) controls which disclosure periods are shown.

### Context

Disclosure data is annual or half-annual, not quarterly. Merging it into `docs/index.html` alongside the RBNZ quarterly series would create period misalignment. A separate chart panel within the existing `docs/disclosures.html` is the right architectural choice — it re-uses the same Chart.js setup and design tokens without polluting the quarterly view. Depends on W-0024.

---

### W-0026

status: open
created: 2026-04-30
updated: 2026-04-30

### Outcome

A profit waterfall chart on `docs/disclosures.html` shows the income statement progression for each bank's most recent full-year period: Net Interest Income → Other Operating Income → Operating Expenses (negative bar) → Credit Impairment (negative bar) → Tax (negative bar) = Profit After Tax. A bank selector allows comparison of two or three banks side by side. Values in NZDm. The chart makes margin compression and cost drag immediately visible.

### Context

Chart.js 4.x supports floating bar datasets which enable waterfall rendering without extra plugins. Data sourced from `disclosure_metrics.json` (W-0024). Available for all machine-readable banks: ANZ, ASB, BNZ, Kiwibank. Rabobank income statement is text-readable (S-0004 confirmed page 34 fully extractable) so Rabobank NPAT is included — its balance sheet gap does not affect P&L. Requires W-0025.

---

### W-0027

status: open
created: 2026-04-30
updated: 2026-04-30

### Outcome

A dual-panel chart on `docs/disclosures.html` shows: (1) Operating Expenses in NZDm as lines per bank across all available annual periods; (2) YoY percentage change in Operating Expenses as a bar chart below. The RBNZ quarterly Cost-to-Income Ratio (already in `metrics.json`) is overlaid on a secondary axis for cross-reference. Values normalised to NZDm across banks (Rabobank NZD thousands converted by extraction pipeline).

### Context

Expense discipline is a major focus in NZ banking commentary — analysts regularly cite opex growth as a risk to ROE. The RBNZ quarterly series captures the ratio but not the absolute scale; the disclosure absolute figures add that dimension. The YoY change view is more analytically useful than the absolute level for spotting acceleration or deceleration in cost growth.

Challenge: Personnel vs non-personnel opex breakdown lives in note tables, not the primary income statement page. Extracting note tables is a separate spike. This item uses statement-page totals only — one `Operating Expenses` line per period per bank.

---

### W-0028

status: open
created: 2026-04-30
updated: 2026-04-30

### Outcome

A chart on `docs/disclosures.html` shows CET1 capital (NZDm), Tier 1 capital (NZDm), and Total Capital (NZDm) as grouped bars for each bank per annual period, sourced from disclosure extraction. A companion view shows the corresponding capital ratios (%) from the RBNZ quarterly data for the nearest quarter-end. Banks designated as D-SIBs (ANZ, ASB, BNZ, Westpac) are marked with a ◆ indicator. A static callout explains the D-SIB 1% surcharge.

### Context

Capital ratios express adequacy relative to risk-weighted assets; absolute capital in NZDm tells you the size of the buffer in dollar terms. Both views matter for different audiences. D-SIB status is static — hardcoded from RBNZ public designations (last updated 2017; ANZ, ASB, BNZ, Westpac). Rabobank and Kiwibank are not D-SIBs. Depends on W-0024.

---

### W-0029

status: open
created: 2026-04-30
updated: 2026-04-30

### Outcome

A funding structure chart on `docs/disclosures.html` shows, for each bank's most recent full-year period: Customer Deposits (NZDm), implied Wholesale Funding (Total Liabilities minus Deposits, NZDm), and Equity (NZDm) as a 100% stacked bar. A Loan-to-Deposit Ratio line (Net Loans / Deposits) is overlaid on a secondary axis. Rabobank is omitted from the balance sheet view (image-based page) and noted explicitly.

### Context

Funding mix is a key dimension of bank risk — high wholesale funding reliance creates liquidity risk. All four machine-readable banks (ANZ, ASB, BNZ, Kiwibank) have Deposits and Total Liabilities on their statement pages. Wholesale funding is implied: Total Liabilities minus Deposits. This is a statement-level approximation — granular breakdown (bonds vs interbank vs repos) would require note-table extraction. Depends on W-0024.

---

## Phase 5: Metrics Expansion

### W-0030

status: open
created: 2026-04-30
updated: 2026-04-30

### Outcome

`config/metrics.yaml` is extended with series IDs for: (1) the 1-month liquidity mismatch ratio; (2) the 1-week liquidity mismatch ratio. `scripts/process_data.py` re-run to include these series in `metrics.json`. A Liquidity tab (see W-0042) shows mismatch ratio charts for the top 6 banks alongside the existing Core Funding Ratio. Glossary updated with definitions for both new metrics.

### Context

S-0001 confirmed that both mismatch ratios are present in the RBNZ XLSX Liquidity section. The series IDs must be read from the `Series Id` row (row 4) of the Data sheet — inspect `data/Bank-Financial-Strength-Dashboard-Data.xlsx` directly. These are straightforward additions once the series IDs are confirmed: same extraction path as all other RBNZ series. Credit rating series extraction is deferred to S-0005 (encoding unknown).

---

### W-0031

status: open
created: 2026-04-30
updated: 2026-04-30

### Outcome

Loan-to-Deposit Ratio (LDR = Net Loans and Advances ÷ Deposits) is computed client-side in `docs/index.html` from the already-stored RBNZ quarterly series. A LDR line chart is added to the Capital tab (see W-0042). LDR is added to the Latest Quarter Snapshot table. `glossary.md` updated with definition and an ADR-0001 derivation note matching the Cost-to-Income Ratio entry.

### Context

Net Loans and Advances (DBB.QIG30) and Deposits (DBB.QIG55) are already mapped in `config/metrics.yaml` and present in `metrics.json`. No new data fetch is needed. LDR is a widely-used funding health indicator that complements the Core Funding Ratio already on the dashboard. Per ADR-0001, derived values are not stored — computation is in the frontend, mirroring Cost-to-Income Ratio.

---

### W-0032

status: open
created: 2026-04-30
updated: 2026-04-30

### Outcome

A capital headroom chart on `docs/index.html` shows, for each bank, CET1 Ratio minus the applicable RBNZ minimum requirement as a "headroom" line over the quarterly history. A horizontal reference band marks the capital conservation buffer zone (2.5 percentage points above the minimum). A config file `config/capital_requirements.yaml` stores the minimum thresholds by year and bank type (standard vs D-SIB), capturing the RBNZ 2019 capital reform phase-in schedule (effective 2023–2028).

### Context

Capital ratios without the minimum context are hard to interpret. A bank at 13% CET1 looks different when the requirement is 4.5% (large buffer) vs 8% (moderate buffer). The RBNZ capital reform phased in higher requirements from July 2023: minimum CET1 rises from 4.5% to 6.5% over five years for non-D-SIBs; D-SIBs face an additional 1–2% surcharge. Hardcoding the published phase-in schedule in YAML is the right approach — these values change rarely and on a known timetable. Research and document the full schedule before coding.

---

### W-0033

status: open
created: 2026-04-30
updated: 2026-04-30

### Outcome

`entity_type` field (`standalone` or `group`) is added to `data/processed/metrics.csv` and `docs/data/processed/metrics.json`. The classification for all 22 RBNZ institutions is hardcoded in `src/processing/parse.py` (static lookup dict — these do not change). The frontend bank selector gains a "Standalone only" quick-select button that filters to standalone entities. ADR-0004 updated to document the schema addition.

### Context

S-0003 identified group vs standalone as a known consumer filtering problem and deferred the field addition. The top-6 default view already excludes group entities by name, but as more entities are added or filtered, a proper `entity_type` field is more maintainable than name-matching. The 22 institution names are fixed in the current RBNZ dataset — the lookup dict will not need frequent updates.

---

### W-0034

status: open
created: 2026-04-30
updated: 2026-04-30

### Outcome

Must result in: `config/metrics.yaml` updated with credit rating series IDs, `metrics.json` regenerated, and a credit rating timeline chart implemented — or an explicit no-action decision recorded in `learnings.md` if the data encoding is unsuitable for visualisation.

### Context

Depends on S-0005 (credit rating series investigation). The RBNZ XLSX has an "Issuer credit ratings" category (confirmed by S-0001). Whether the data is encoded as letter strings (AA-, A+), numeric ordinals, or something else is unknown until the Series Definitions sheet is inspected. If letter strings: map to a numeric axis for charting. If integer-coded: document the mapping table. If the series only records a static current rating with no history: not useful for visualisation.

---

## Phase 6: Advanced Visualisation

### W-0035

status: open
created: 2026-04-30
updated: 2026-04-30

### Outcome

All time-series charts in `docs/index.html` gain vertical annotation lines at quarters where the RBNZ OCR changed by ≥25 bps. Annotations are computed client-side from the already-loaded `ocr.json`: diff consecutive quarterly OCR values and mark quarters where the absolute delta ≥ 0.25. A toggle "Show OCR events" (off by default) controls visibility. Hovering an annotation line shows the cumulative OCR change that quarter (e.g. "+50 bps") in a tooltip.

### Context

OCR movements are the single most important macroeconomic driver of bank NIM — the lag and magnitude of the pass-through is a central analytical question for this dashboard. Annotations make the relationship visually testable without building a separate model. The OCR data is already loaded (W-0019); this item adds only the client-side annotation rendering layer. Many OCR changes happen at multiple RBNZ meetings within one quarter — use the quarterly delta (last OCR value minus prior quarter last value) to capture cumulative movement.

---

### W-0036

status: open
created: 2026-04-30
updated: 2026-04-30

### Outcome

A hardcoded events config (`config/events.yaml`) lists significant NZ and global events affecting bank performance, each with a `period` (YYYY-QN) and a short label (≤20 characters). Initial event set: COVID-19 lockdown (2020-Q1), RBNZ capital reform announced (2019-Q4), OCR dropped to record low 0.25% (2020-Q1), OCR emergency cut to 0.1% (2020-Q3), RBNZ capital reform phase-in begins (2023-Q3), SVB/Credit Suisse stress (2023-Q1), Kiwibank ownership change (2022-Q2). Charts gain a toggle "Show events" (off by default) that draws labelled vertical markers at the relevant quarter. Event labels render at the top of the chart area. Client-side only; no pipeline changes.

### Context

Without event markers, metric movements (e.g. the sharp NIM expansion through 2022–2023) appear as unexplained jumps. Event context is what separates a dashboard from a raw data dump. Hardcoded YAML is the right approach — the event list is finite, curated, and rarely changes. Events reuse the same annotation rendering infrastructure as W-0035, extending it to non-OCR events. Depends on W-0035.

---

### W-0037

status: open
created: 2026-04-30
updated: 2026-04-30

### Outcome

All time-series charts gain a toggleable "Sector avg" line (dashed, light grey) computed client-side as the mean of all currently-visible standalone banks for each period. When fewer than 2 banks are selected the sector average is hidden. A "Sector avg" checkbox sits alongside the bank selector. The average excludes null values (banks with missing data for a period are omitted from that period's average, not treated as zero).

### Context

A sector average reference line makes individual bank outperformance or underperformance immediately readable without requiring the user to mentally average several lines. Standalone-only is the correct base for the average (group entities like ANZ Group distort the figures). Depends on W-0033 (entity_type field) for a clean standalone filter; until then the current top-6 default selection is an acceptable proxy.

---

### W-0038

status: open
created: 2026-04-30
updated: 2026-04-30

### Outcome

Six static bank detail pages (`docs/bank/anz.html`, `asb.html`, `bnz.html`, `westpac.html`, `kiwibank.html`, `rabobank.html`) each show: (1) a header card with bank name, latest-period snapshot values for the 4 key KPIs, and trend direction; (2) sparkline charts for all 20 mapped RBNZ metrics across the full history; (3) a disclosure metrics table (if `disclosure_metrics.json` available, W-0024) showing annual P&L and balance sheet figures; (4) a link to the most recent disclosure PDF from `config/sources.yaml`. Clicking a bank pill or name on `docs/index.html` navigates to the bank's detail page.

### Context

The main dashboard is a cross-bank comparison view — it does not support deep inspection of a single bank. Six static pages avoids a build step and keeps the architecture purely client-side. All data is already in `metrics.json` filtered by entity name. The sparkline layout (small charts, one per metric) gives an at-a-glance health check across every dimension simultaneously. Westpac has no disclosure PDF data (WAF block) — show RBNZ quarterly data only and note the gap.

---

### W-0039

status: open
created: 2026-04-30
updated: 2026-04-30

### Outcome

Twenty static metric detail pages (`docs/metric/nim.html`, `cet1-ratio.html`, etc. — one per mapped RBNZ metric) each show: (1) the full metric definition from `glossary.md`; (2) the RBNZ series ID and unit; (3) a full-history line chart with all banks; (4) a cross-bank ranking table for the latest quarter; (5) a trailing-12Q trend direction per bank (improving / stable / deteriorating). Clicking a chart title on `docs/index.html` navigates to the metric detail page.

### Context

Metric drill-down is the complement to bank drill-down (W-0038). It answers "how does this specific metric compare across all banks, and over time?" Glossary content (W-0021) is the source of truth for definitions — the metric page embeds the full definition, not a summary. Static HTML with inline JS filtering `metrics.json` by metric name. The metric slug in the URL should match the canonical metric name lowercased and hyphenated for linking consistency.

---

### W-0040

status: open
created: 2026-04-30
updated: 2026-04-30

### Outcome

A toggle "Indexed (base = 100)" above the chart grid rebases all series to 100 at the earliest available data point for each bank, then renders relative change over time. The toggle state persists in `localStorage["chartMode"]`. Restoring to "Absolute" returns to normal values. An explanatory note under the toggle states "Each bank's first available value = 100."

### Context

Indexed mode is essential for balance sheet metrics (Total Assets, Net Loans, Deposits, Equity) where ANZ ($200bn) and Kiwibank ($37bn) operate at very different absolute scales — absolute comparison is not meaningful for trajectory analysis. Pure client-side transform of chart datasets before Chart.js render. No new data required.

---

### W-0041

status: open
created: 2026-04-30
updated: 2026-04-30

### Outcome

Each chart card gains a download icon (↓) in its top-right corner alongside the fullscreen button (W-0020). Clicking it saves the chart as a PNG named `{metric-slug}-{YYYY-MM-DD}.png` using `canvas.toDataURL('image/png')`. The dark background (`#0d0d0d`) is preserved in the export. No server component.

### Context

Users sharing charts via screenshots loses resolution and metadata. Native canvas export is a one-function addition using Chart.js's built-in canvas API. Pairs naturally with W-0020 (fullscreen) — the export button should be available in both normal and fullscreen modes.

---

### W-0042

status: open
created: 2026-04-30
updated: 2026-04-30

### Outcome

The chart grid on `docs/index.html` is reorganised into four tab categories: **profitability** (NIM, ROE, ROA, Cost-to-Income), **capital** (CET1, Tier 1, Total Capital Ratio, Capital Headroom, LDR), **asset quality** (NPL Ratio, Total Non-Performing Loans), **liquidity** (Core Funding Ratio, 1-month mismatch, 1-week mismatch). The active tab persists in `localStorage["activeTab"]`. Bank selector and date-range filter apply across all tabs. A tab showing zero mapped metrics is hidden until data is available.

### Context

The current single-grid layout works for 4 charts but will become unmanageable as capital, liquidity, and funding metrics are added (W-0030, W-0031, W-0032). Tab categories match the RBNZ XLSX groupings (Capital adequacy, Profitability, Asset quality, Liquidity), which is the logical taxonomy users of this data already know. No navigation to new pages — tab switching is purely client-side visibility toggling.

---

### W-0043

status: open
created: 2026-04-30
updated: 2026-04-30

### Outcome

The Latest Quarter Snapshot table gains: (1) click-to-sort on any column header (ascending/descending toggle, sort direction indicated by ▲/▼); (2) best/worst colour coding per column — teal text for the best-performing bank on each metric, muted red text for the worst; (3) a period selector dropdown allowing the user to choose any historical quarter, not just the latest. Sort state and selected period persist in `localStorage`.

### Context

The snapshot table currently renders in entity-name order with no sorting. For a ranking/comparison use case, sortable columns are a baseline expectation. Colour coding by best/worst replaces the need to mentally scan each column for the extremes. The period selector enables point-in-time historical comparison — "what did the sector look like in 2020-Q2?" — without changing the main chart date range filter.

---

## Phase 7: Insights and Narrative

### W-0044

status: open
created: 2026-04-30
updated: 2026-04-30

### Outcome

A NIM pass-through analysis panel on `docs/index.html` (Profitability tab) shows: (1) NIM and OCR overlaid on a shared time axis with aligned quarter labels — extending the existing W-0019 overlay; (2) below it, a scatter chart of OCR change (x-axis, bps per quarter) vs NIM change two quarters later (y-axis, bps) — one data point per bank per OCR-change event — with a best-fit trend line per bank. A tooltip on each scatter point shows the bank, the quarter, and the OCR move.

### Context

The lag relationship between OCR changes and bank NIM is the central empirical question this dashboard can answer that no existing RBNZ publication addresses directly. The scatter chart requires: identifying OCR-change quarters from `ocr.json` (delta ≥ 25 bps, same logic as W-0035), looking up NIM at t+2 quarters for each visible bank, computing the NIM change from t-1. All client-side computation from loaded JSON. The two-quarter lag is an empirically common finding for NZ retail banks — the chart will confirm or refute it per bank. Depends on W-0035.

---

### W-0045

status: open
created: 2026-04-30
updated: 2026-04-30

### Outcome

Each time-series chart gains an optional shaded band between the minimum and maximum value across all visible banks for each period. The band uses a semi-transparent teal fill (opacity 0.08). A "Show range" checkbox beside the sector-average toggle (W-0037) controls visibility. The band narrows where banks converge and widens where they diverge, making dispersion visible without adding individual lines.

### Context

The range band is a low-effort, high-insight addition for understanding sector-wide spread. It is especially useful for NIM (where banks have traditionally moved in lockstep but diverged post-COVID) and for NPL Ratio (where Kiwibank and smaller banks show different credit quality trajectories). Implemented as a Chart.js `fill` between two hidden datasets (min-per-period and max-per-period arrays), computed client-side. Depends on W-0037 (shares the toggle UI infrastructure).

---

### W-0046

status: open
created: 2026-04-30
updated: 2026-04-30

### Outcome

A ranking section on `docs/index.html` (below the snapshot table) shows a compact heat-map table: rows = banks, columns = KPIs, cells = rank (1 = best) colour-coded by quartile (deep teal for rank 1, white for middle, muted red for last). A toggle switches between "Rank view" and "Value view" (showing actual metric values). The ranking updates with the bank selection and date range filter.

### Context

Rankings make sector-relative performance immediately readable — "ANZ ranks 1st on Cost-to-Income, 3rd on ROE" is the kind of summary that analysts publish in reports. The quartile colour coding (not binary best/worst) gives more nuance than the snapshot table's teal/red extremes (W-0043). Purely client-side computation over `metrics.json` for the selected period.

---

### W-0047

status: open
created: 2026-04-30
updated: 2026-04-30

### Outcome

A "Sector narrative" panel beneath the chart grid renders 4–6 auto-generated bullet points for the most recent available quarter. Each bullet follows a fixed template: e.g. "Sector NIM averaged X.X%, [up/down] Y bps from the prior quarter — [the highest/lowest] since [period]." / "[Bank] posted the [highest/lowest] ROE at X.X%." / "CET1 ratios [improved/declined] across [N of 6] banks." Templates handle null gracefully (sentence is skipped if the required metric is absent). Generation is client-side from `metrics.json` on page load — no LLM or external service.

### Context

Template-based narrative generation is more auditable and lower-risk than LLM commentary: every sentence traces directly to a data value with a defined template. It gives non-analytical users an entry point without requiring them to interpret the charts. The approach mirrors what financial journalists do manually each quarter. The narrative section carries a small disclaimer: "Auto-generated from RBNZ data — verify before citing."

---

### W-0048

status: open
created: 2026-04-30
updated: 2026-04-30

### Outcome

Each time-series chart's most recent data point is annotated with a "trend flag": a small coloured dot (teal = improving over last 4Q, grey = stable, red = deteriorating) derived from the trailing linear slope of the series for the currently-visible date range. The flag is shown in the chart legend alongside the bank name. Thresholds: slope magnitude below 0.05 standard deviations per quarter = stable; above = improving or deteriorating based on direction. The metric's "good direction" (higher-is-better vs lower-is-better) is read from a static config map.

### Context

Trend flags make the snapshot table row (▲/▼ vs prior quarter only) more robust by using a 4-quarter slope rather than a single-quarter delta, which is noisy. The "good direction" config (e.g. ROE: higher-is-better; NPL Ratio: lower-is-better; Cost-to-Income: lower-is-better) is a small static lookup — 20 entries. Client-side computation over the date-filtered chart data.

---

## Phase 8: Transparency and Governance

### W-0049

status: open
created: 2026-04-30
updated: 2026-04-30

### Outcome

`docs-adr/0005-pdf-extraction-approach.md` documents: (1) the hybrid `extract_tables()` + `extract_text()` strategy and when each is used; (2) the two extraction patterns — `first_value` (income statement / balance sheet) and `second_pct` (capital ratios, where column 1 is the regulatory minimum and column 2 is the bank's actual ratio); (3) unit normalisation rules (NZDm vs NZD thousands, detected from first 3000 chars of document text); (4) known data gaps — Rabobank balance sheet image-based, Westpac inaccessible via WAF; (5) the decision not to adopt OCR at this stage and the condition under which it would be reconsidered. `docs-adr/README.md` updated with the new entry.

### Context

The extraction approach was spike-driven (S-0004) and implementation decisions are recorded in `learnings.md` and `progress.md`. Formalising as an ADR makes the decisions discoverable and reviewable independently of the session logs. Should be completed before the disclosure integration phase (W-0024–W-0029) to avoid accumulating undocumented decisions on top of an informal foundation.

---

### W-0050

status: open
created: 2026-04-30
updated: 2026-04-30

### Outcome

`docs/coverage.html` — a data coverage matrix page. Two sections: (1) RBNZ quarterly coverage — a grid of bank × quarter cells, coloured teal where data is present and empty where null, for each mapped metric; (2) Disclosure annual coverage — a grid of bank × period showing which of the 10 extracted metrics were successfully extracted (teal) and which are null (empty, with reason: "image-based page", "PDF inaccessible", "metric not on statement page"). Clicking a teal cell links to the source URL. Footnotes explain each gap category. Navigation link added to the site header.

### Context

Data gaps are unavoidable but must be transparent. Users citing figures from this dashboard need to know whether a null means "bank didn't report" or "pipeline couldn't extract". The coverage page also serves as a living audit — when new PDFs are added or the extraction pipeline is updated, the coverage grid will reflect improvements automatically (generated client-side from `metrics.json` and `disclosure_metrics.json`). Westpac absence from the disclosure section is explained by the WAF block; Rabobank balance sheet nulls are explained by the image-based page.

---

### W-0051

status: open
created: 2026-04-30
updated: 2026-04-30

### Outcome

`docs/methodology.html` (part of W-0021) is extended with a section documenting the RBNZ capital reform phase-in schedule: the 2019 announcement, the July 2023 implementation start, the full schedule of rising CET1 minimums through 2028, the D-SIB surcharges, and the impact on capital headroom calculations (W-0032). Sources are cited with RBNZ publication URLs. The section is static prose — no pipeline changes.

### Context

The capital headroom chart (W-0032) will be confusing without this explanatory context. The 2019 capital reform is the defining regulatory event of the period covered by this dashboard (2018–2025). Its phase-in schedule is publicly documented by RBNZ but not widely understood. Embedding it in the methodology page ensures users interpret capital trends correctly.

---

## Phase 9: Research Spikes

### S-0005

status: open
created: 2026-04-30
updated: 2026-04-30

### Outcome

Must result in: series IDs identified and W-0034 opened with encoding details — or an explicit no-action decision recorded in `learnings.md` if the data is not useful for visualisation.

### Context

S-0001 confirmed the RBNZ XLSX has an "Issuer credit ratings" category. The exact series IDs and value encoding are unknown. Inspect the `Series Definitions` sheet of `data/Bank-Financial-Strength-Dashboard-Data.xlsx` to determine: the series IDs for S&P (and any Moody's/Fitch) ratings; whether values are stored as letter strings (AA-, A+), numeric ordinals, or integer codes; whether the series tracks rating history or only a current snapshot; and which institutions have non-null values. If ratings are coded as integers, document the mapping. If tracking history: W-0034 is viable. If only a current snapshot: not useful for time-series visualisation — explicitly defer.

---

### S-0006

status: open
created: 2026-04-30
updated: 2026-04-30

### Outcome

Must result in: backlog items opened for feasible external data sources — or an explicit no-action decision for each source assessed.

### Context

Economic context enriches bank performance interpretation. Candidate sources: (1) NZ house price index — RBNZ C31 series (monthly XLSX, same domain as OCR data); (2) NZ GDP growth — Stats NZ Infoshare (quarterly, CSV or API); (3) NZ unemployment rate — Stats NZ Household Labour Force Survey (quarterly CSV); (4) NZ housing credit growth — RBNZ C5 series (monthly XLSX). For each, assess: URL accessibility without a WAF block, data format (XLSX/CSV/API/paywall), update frequency alignment with quarterly bank data, and whether the pipeline can handle it with minimal new code. Stats NZ Infoshare uses a query API that requires registration — if so, note it explicitly and do not open a pipeline item.

Challenge: External data sources carry ongoing maintenance risk. Only open pipeline items for sources that are (a) machine-readable via a stable URL, (b) updated at least quarterly, and (c) RBNZ or Stats NZ hosted (not third-party). Overlay on charts should be optional and clearly labelled as external context, not bank performance data.

---

### S-0007

status: open
created: 2026-04-30
updated: 2026-04-30

### Outcome

Must result in: confirmed NZX API URLs for Westpac disclosure PDFs and W-0015 re-run item opened — or an explicit no-action decision if Westpac remains inaccessible via all channels.

### Context

Westpac is the fourth-largest NZ bank by assets and its absence from the disclosure extraction is a material gap. The WAF at `westpac.co.nz` blocks all pipeline download attempts. The NZX API workaround was used successfully for Kiwibank (the 2024 report was retrieved via `api.nzx.com/public/announcement/436602/attachment/425238/436602-425238.pdf`). Westpac NZ is also NZX-listed and files half-year and full-year disclosure statements as NZX announcements. Investigate: (1) search NZX announcements for "Westpac New Zealand" disclosure statement filings; (2) extract the announcement IDs for the most recent 4 periods; (3) verify the PDF URLs are accessible from the pipeline; (4) validate that the downloaded PDFs are machine-readable via `pdfplumber`. If successful, update `config/sources.yaml` and open a targeted W-0015 extension item.

---

### S-0008

status: open
created: 2026-04-30
updated: 2026-04-30

### Outcome

Must result in: a decision on whether to add OCR capability for Rabobank balance sheet extraction — documented in `learnings.md`. If feasible: open an implementation item and ADR-0006 for the OCR dependency. If not: explicitly close the gap with a note that Rabobank balance sheet data remains unavailable.

### Context

S-0004 confirmed that Rabobank's 2022 disclosure statement balance sheet (page 35) is image-based — zero extractable characters, no PDF table objects. Total Assets for Rabobank cannot be extracted without OCR. Rabobank is NZ's sixth-largest bank and has a significant agricultural lending portfolio; its balance sheet scale matters for sector completeness. Investigate: (1) whether `pytesseract` + `tesseract` (system package) can extract the image-based page; (2) whether more recent Rabobank reports (2023, 2024) also have image-based balance sheets or have moved to text-based layouts; (3) the cost-benefit — adding a system-level OCR dependency for one bank's balance sheet. If newer Rabobank reports have text-based balance sheets, update `config/sources.yaml` with the newer URLs and test extraction before committing to an OCR dependency.

---
