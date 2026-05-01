# Backlog

> This file tracks **pipeline and infrastructure** work — data ingestion, processing, visualisation, and governance.
> Discovery spike outputs are recorded in `learnings.md`.

---

## Guiding Policy

**Diagnostic**: RBNZ publishes detailed quarterly bank performance data as Excel files. The data is accurate and public but inaccessible — it requires manual downloading, has no time-series comparison across banks, and carries no interpretive context. The same gap applies to bank General Disclosure Statements: machine-readable PDFs, but no tool to extract and compare them.

**Policy**: Build and maintain a zero-cost, fully static dashboard that surfaces sector-wide insights from public regulatory data. No backend. No paid APIs. No LLM inference at runtime. No proprietary data sources.

**Explicit trade-offs — what this project does not do:**
- No real-time or intraday data (quarterly batch refresh is the cadence)
- No user authentication or personalisation
- No paid data sources (Stats NZ API, Bloomberg, CoreLogic)
- No dynamic server-side rendering (static HTML + JSON only)
- No mobile-first design (research tool, desktop-primary)
- No coverage of non-bank financial institutions (insurance, wealth management)

**Primary users**: Financial analysts, researchers, and journalists who want to compare NZ bank performance without downloading Excel files.

---

## Priority Stack

Recommended sequencing for open items. Reflects: (1) items that unblock other items, (2) data-coverage gaps before UI polish, (3) low-effort high-value additions before complex builds.

**Now — unblock downstream work:**
1. W-0049 — ADR-0005 for PDF extraction (governance gate before disclosure integration)
2. W-0024 — Run disclosure extraction end-to-end (unblocks W-0025 through W-0029)
3. W-0033 — Add entity_type field (unblocks W-0037 sector average)
4. S-0005 — Credit rating encoding (unblocks W-0034)
5. S-0007 — Westpac via NZX API (if successful, closes the major disclosure gap)

**Next — data expansion (config-only or client-side, no new dependencies):**
6. W-0030 — Mismatch ratios + credit concentration (YAML-only, series IDs confirmed)
7. W-0052 — RWA, RORWA, risk density (YAML + client-side derivation)
8. W-0053 — Provisioning coverage (YAML + client-side derivation)
9. W-0031 — Loan-to-Deposit Ratio (client-side, all data already present)
10. W-0054 — Credit concentration series (YAML-only, IDs confirmed)

**Then — UI foundation (required before adding more charts):**
11. W-0042 — Tab categories (prevents chart grid overload)
12. W-0035 — OCR event annotations (unblocks W-0036, W-0044)
13. W-0036 — Event overlay with config/events.yaml
14. W-0020 — Fullscreen charts
15. W-0060 — Data freshness badge

**Then — disclosure integration:**
16. W-0025 — Disclosure charts in disclosures.html
17. W-0026 — Profit waterfall
18. W-0027 — Opex chart
19. W-0028 — Capital components
20. W-0029 — Funding structure

**Then — deeper insights:**
21. W-0037 — Sector average line
22. W-0043 — Snapshot table sorting + colour coding
23. W-0032 — Capital headroom chart
24. W-0021 — Transparency pages
25. W-0047 — Auto-narrative panel
26. W-0062 — URL state sharing

**Later — polish and depth:**
27–onwards: drill-downs (W-0038, W-0039), advanced analytics (W-0044, W-0065), export (W-0041, W-0063), pipeline automation (W-0059, W-0061)

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

status: ready
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

status: done
created: 2026-04-28
updated: 2026-05-01

### Outcome

Each chart in the frontend can be expanded to full-screen. A focus/zoom button (e.g. ⛶) is rendered in the top-right corner of every Chart.js canvas. Clicking it opens the chart in a modal overlay that fills the viewport, re-rendering the chart at the larger size. Pressing Escape or clicking outside the modal closes it. No additional dependencies beyond Chart.js (already loaded).

### Context

Charts are currently small within the responsive grid. Full-screen mode allows detailed inspection of individual series without leaving the page. The implementation should be purely client-side JS within `docs/index.html`; no build step.

---

### W-0021

status: ready
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

status: done
created: 2026-04-30
updated: 2026-05-01

### Outcome

`scripts/process_disclosures.py` runs end-to-end across all PDFs in `data/raw/financial_disclosures/` that have a valid `.meta.json` sidecar. Produces `data/processed/disclosures.csv` and `docs/data/processed/disclosure_metrics.json` (distinct from the existing `disclosures.json` disclosure index) containing extracted metric rows in the canonical schema (`entity | metric | value | period | source`). A summary of extracted-vs-null counts is logged per bank per period. The existing `docs/data/processed/disclosures.json` (PDF index file built by `build_disclosures_index.py`) remains unchanged.

### Context

W-0015 built and tested the extraction pipeline against sample PDFs. The full corpus (ANZ ×3, ASB ×15, BNZ ×7, Kiwibank ×14, Rabobank ×4) is committed to the repo. Running end-to-end validates the regex patterns against all committed reports and surfaces any format differences in older documents.

Challenge: Rabobank balance sheet (page 35 of the 2022 report) is image-based — confirmed zero extractable characters by S-0004. Balance sheet metrics (Total Assets, Net Loans, Deposits) will be null for Rabobank. Log WARNING and store null. Do not attempt OCR here — see S-0008 if the gap is later deemed worth closing.

---

### W-0025

status: done
created: 2026-04-30
updated: 2026-05-01

### Outcome

`docs/disclosures.html` (currently an index page showing PDF coverage) gains a chart panel that loads `docs/data/processed/disclosure_metrics.json` and displays key annual metrics (Profit After Tax, Operating Expenses, Total Assets, CET1 Ratio) as line charts per bank. Banks with different fiscal year ends (ANZ/BNZ: Sep, ASB/Kiwibank: Jun, Rabobank: Dec) are rendered on a shared annual axis labelled by `period_end` year. A note on the page explains the differing year-end dates. Period-type filter (Full year / Half year) controls which disclosure periods are shown.

### Context

Disclosure data is annual or half-annual, not quarterly. Merging it into `docs/index.html` alongside the RBNZ quarterly series would create period misalignment. A separate chart panel within the existing `docs/disclosures.html` is the right architectural choice — it re-uses the same Chart.js setup and design tokens without polluting the quarterly view. Depends on W-0024.

---

### W-0026

status: done
created: 2026-04-30
updated: 2026-05-01

### Outcome

A profit waterfall chart on `docs/disclosures.html` shows the income statement progression for each bank's most recent full-year period: Net Interest Income → Other Operating Income → Operating Expenses (negative bar) → Credit Impairment (negative bar) → Tax (negative bar) = Profit After Tax. A bank selector allows comparison of two or three banks side by side. Values in NZDm. The chart makes margin compression and cost drag immediately visible.

### Context

Chart.js 4.x supports floating bar datasets which enable waterfall rendering without extra plugins. Data sourced from `disclosure_metrics.json` (W-0024). Available for all machine-readable banks: ANZ, ASB, BNZ, Kiwibank. Rabobank income statement is text-readable (S-0004 confirmed page 34 fully extractable) so Rabobank NPAT is included — its balance sheet gap does not affect P&L. Requires W-0025.

---

### W-0027

status: done
created: 2026-04-30
updated: 2026-05-01

### Outcome

A dual-panel chart on `docs/disclosures.html` shows: (1) Operating Expenses in NZDm as lines per bank across all available annual periods; (2) YoY percentage change in Operating Expenses as a bar chart below. The RBNZ quarterly Cost-to-Income Ratio (already in `metrics.json`) is overlaid on a secondary axis for cross-reference. Values normalised to NZDm across banks (Rabobank NZD thousands converted by extraction pipeline).

### Context

Expense discipline is a major focus in NZ banking commentary — analysts regularly cite opex growth as a risk to ROE. The RBNZ quarterly series captures the ratio but not the absolute scale; the disclosure absolute figures add that dimension. The YoY change view is more analytically useful than the absolute level for spotting acceleration or deceleration in cost growth.

Challenge: Personnel vs non-personnel opex breakdown lives in note tables, not the primary income statement page. Extracting note tables is a separate spike. This item uses statement-page totals only — one `Operating Expenses` line per period per bank.

---

### W-0028

status: done
created: 2026-04-30
updated: 2026-05-01

### Outcome

A chart on `docs/disclosures.html` shows CET1 capital (NZDm), Tier 1 capital (NZDm), and Total Capital (NZDm) as grouped bars for each bank per annual period, sourced from disclosure extraction. A companion view shows the corresponding capital ratios (%) from the RBNZ quarterly data for the nearest quarter-end. Banks designated as D-SIBs (ANZ, ASB, BNZ, Westpac) are marked with a ◆ indicator. A static callout explains the D-SIB 1% surcharge.

### Context

Capital ratios express adequacy relative to risk-weighted assets; absolute capital in NZDm tells you the size of the buffer in dollar terms. Both views matter for different audiences. D-SIB status is static — hardcoded from RBNZ public designations (last updated 2017; ANZ, ASB, BNZ, Westpac). Rabobank and Kiwibank are not D-SIBs. Depends on W-0024.

---

### W-0029

status: done
created: 2026-04-30
updated: 2026-05-01

### Outcome

A funding structure chart on `docs/disclosures.html` shows, for each bank's most recent full-year period: Customer Deposits (NZDm), implied Wholesale Funding (Total Liabilities minus Deposits, NZDm), and Equity (NZDm) as a 100% stacked bar. A Loan-to-Deposit Ratio line (Net Loans / Deposits) is overlaid on a secondary axis. Rabobank is omitted from the balance sheet view (image-based page) and noted explicitly.

### Context

Funding mix is a key dimension of bank risk — high wholesale funding reliance creates liquidity risk. All four machine-readable banks (ANZ, ASB, BNZ, Kiwibank) have Deposits and Total Liabilities on their statement pages. Wholesale funding is implied: Total Liabilities minus Deposits. This is a statement-level approximation — granular breakdown (bonds vs interbank vs repos) would require note-table extraction. Depends on W-0024.

---

## Phase 5: Metrics Expansion

### W-0030

status: done
created: 2026-04-30
updated: 2026-05-01

### Outcome

`config/metrics.yaml` is extended with confirmed series IDs: `DBB.QIH10` (1-month mismatch ratio) and `DBB.QIH20` (1-week mismatch ratio). Additionally, three credit concentration series are mapped: `DBB.QIJ10` (top 5 non-bank credit exposures / CET1), `DBB.QIJ30` (top 5 bank exposures / CET1), `DBB.QIJ40` (bank exposures ≥10% of CET1). `scripts/process_data.py` re-run to include all five new series in `metrics.json`. A Liquidity tab (W-0042) shows mismatch and concentration charts alongside Core Funding Ratio. Glossary updated with definitions for all five new metrics.

### Context

Series IDs confirmed by direct XLSX inspection. The mismatch ratios are in the Liquidity section (QIH); the concentration metrics are in the Credit concentration section (QIJ) and are particularly useful for understanding interbank exposure risk. All five use the same extraction path as existing RBNZ series — no pipeline changes needed, only `config/metrics.yaml` additions.

---

### W-0031

status: done
created: 2026-04-30
updated: 2026-05-01

### Outcome

Loan-to-Deposit Ratio (LDR = Net Loans and Advances ÷ Deposits) is computed client-side in `docs/index.html` from the already-stored RBNZ quarterly series. A LDR line chart is added to the Capital tab (see W-0042). LDR is added to the Latest Quarter Snapshot table. `glossary.md` updated with definition and an ADR-0001 derivation note matching the Cost-to-Income Ratio entry.

### Context

Net Loans and Advances (DBB.QIG30) and Deposits (DBB.QIG55) are already mapped in `config/metrics.yaml` and present in `metrics.json`. No new data fetch is needed. LDR is a widely-used funding health indicator that complements the Core Funding Ratio already on the dashboard. Per ADR-0001, derived values are not stored — computation is in the frontend, mirroring Cost-to-Income Ratio.

---

### W-0032

status: ready
created: 2026-04-30
updated: 2026-04-30

### Outcome

A capital headroom chart on `docs/index.html` shows, for each bank, CET1 Ratio minus the applicable RBNZ minimum requirement as a "headroom" line over the quarterly history. A horizontal reference band marks the capital conservation buffer zone (2.5 percentage points above the minimum). A config file `config/capital_requirements.yaml` stores the minimum thresholds by year and bank type (standard vs D-SIB), capturing the RBNZ 2019 capital reform phase-in schedule (effective 2023–2028).

### Context

Capital ratios without the minimum context are hard to interpret. A bank at 13% CET1 looks different when the requirement is 4.5% (large buffer) vs 8% (moderate buffer). The RBNZ capital reform phased in higher requirements from July 2023: minimum CET1 rises from 4.5% to 6.5% over five years for non-D-SIBs; D-SIBs face an additional 1–2% surcharge. Hardcoding the published phase-in schedule in YAML is the right approach — these values change rarely and on a known timetable. Research and document the full schedule before coding.

---

### W-0033

status: done
created: 2026-04-30
updated: 2026-05-01

### Outcome

`entity_type` field (`standalone` or `group`) is added to `data/processed/metrics.csv` and `docs/data/processed/metrics.json`. The classification for all 22 RBNZ institutions is hardcoded in `src/processing/parse.py` (static lookup dict — these do not change). The frontend bank selector gains a "Standalone only" quick-select button that filters to standalone entities. ADR-0004 updated to document the schema addition.

### Context

S-0003 identified group vs standalone as a known consumer filtering problem and deferred the field addition. The top-6 default view already excludes group entities by name, but as more entities are added or filtered, a proper `entity_type` field is more maintainable than name-matching. The 22 institution names are fixed in the current RBNZ dataset — the lookup dict will not need frequent updates.

---

### W-0034

status: ready
created: 2026-04-30
updated: 2026-04-30

### Outcome

`config/metrics.yaml` updated with `DBB.QIA10` (S&P), `DBB.QIA20` (Fitch), `DBB.QIA30` (Moody's). `metrics.json` regenerated. A credit rating timeline chart is added to the bank detail pages (W-0038): a step-line chart on a categorical y-axis (AAA → AA+ → AA → AA- → A+ → A → A- → BBB+) showing each rating agency's assessment over time. Changes in rating are annotated with the new rating label. Chart rendered on `docs/bank/[bank].html` (not the main dashboard, as most banks have stable ratings and the chart adds little to the quarterly view).

### Context

Series IDs confirmed: `DBB.QIA10` (S&P), `DBB.QIA20` (Fitch), `DBB.QIA30` (Moody's). Encoding format (letter strings vs numeric) determined by S-0005 — if integer-coded, a mapping table is added to `config/metrics.yaml`. The chart uses a step interpolation mode (ratings don't change continuously). A rating downgrade is the most analytically significant event; the chart makes historical downgrades immediately visible. Depends on S-0005 for encoding details and W-0038 for the bank detail page structure.

---

## Phase 6: Advanced Visualisation

### W-0035

status: done
created: 2026-04-30
updated: 2026-05-01

### Outcome

All time-series charts in `docs/index.html` gain vertical annotation lines at quarters where the RBNZ OCR changed by ≥25 bps. Annotations are computed client-side from the already-loaded `ocr.json`: diff consecutive quarterly OCR values and mark quarters where the absolute delta ≥ 0.25. A toggle "Show OCR events" (off by default) controls visibility. Hovering an annotation line shows the cumulative OCR change that quarter (e.g. "+50 bps") in a tooltip.

### Context

OCR movements are the single most important macroeconomic driver of bank NIM — the lag and magnitude of the pass-through is a central analytical question for this dashboard. Annotations make the relationship visually testable without building a separate model. The OCR data is already loaded (W-0019); this item adds only the client-side annotation rendering layer. Many OCR changes happen at multiple RBNZ meetings within one quarter — use the quarterly delta (last OCR value minus prior quarter last value) to capture cumulative movement.

---

### W-0036

status: done
created: 2026-04-30
updated: 2026-05-01

### Outcome

A hardcoded events config (`config/events.yaml`) lists significant NZ and global events affecting bank performance, each with a `period` (YYYY-QN), a short label (≤20 characters), and an optional `category` (`monetary`, `regulatory`, `macro`, `market`). Initial event set:

| Period | Label | Category |
|---|---|---|
| 2019-Q4 | RBNZ capital reform | regulatory |
| 2020-Q1 | COVID-19 lockdown | macro |
| 2020-Q1 | OCR → 0.25% | monetary |
| 2020-Q3 | OCR → 0.10% (floor) | monetary |
| 2020-Q4 | FLP launched | monetary |
| 2021-Q1 | LVR restrictions removed | regulatory |
| 2021-Q3 | OCR hiking cycle begins | monetary |
| 2021-Q4 | LVR restrictions reinstated | regulatory |
| 2022-Q2 | Kiwibank govt buyback | market |
| 2023-Q1 | SVB / Credit Suisse | market |
| 2023-Q3 | OCR peaks at 5.50% | monetary |
| 2023-Q3 | RBNZ capital reform begins | regulatory |
| 2024-Q3 | OCR easing cycle begins | monetary |

Category determines the marker colour (teal = monetary, amber = regulatory, grey = macro/market). Charts gain a toggle "Show events" (off by default). Event labels render at the top of the chart area. Client-side only; no pipeline changes.

### Context

Without event markers, metric movements (e.g. the sharp NIM expansion through 2022–2023, the sudden credit provisioning spike in 2020-Q1) appear as unexplained jumps. The FLP (Funding for Lending Programme, Nov 2020) significantly depressed bank funding costs through 2021 — it is one of the most important explanatory events for NIM trajectory. LVR restriction cycles drove housing credit volume. The OCR peak at 5.50% (May 2023) and the start of cuts (Aug 2024) define the two ends of the rate cycle visible in this dataset. Hardcoded YAML is the right approach — the event list is finite, curated, and changes only when new significant events occur. Events reuse the annotation rendering infrastructure from W-0035. Depends on W-0035.

---

### W-0037

status: done
created: 2026-04-30
updated: 2026-05-01

### Outcome

All time-series charts gain a toggleable "Sector avg" line (dashed, light grey) computed client-side as the mean of all currently-visible standalone banks for each period. When fewer than 2 banks are selected the sector average is hidden. A "Sector avg" checkbox sits alongside the bank selector. The average excludes null values (banks with missing data for a period are omitted from that period's average, not treated as zero).

### Context

A sector average reference line makes individual bank outperformance or underperformance immediately readable without requiring the user to mentally average several lines. Standalone-only is the correct base for the average (group entities like ANZ Group distort the figures). Depends on W-0033 (entity_type field) for a clean standalone filter; until then the current top-6 default selection is an acceptable proxy.

---

### W-0038

status: ready
created: 2026-04-30
updated: 2026-04-30

### Outcome

Six static bank detail pages (`docs/bank/anz.html`, `asb.html`, `bnz.html`, `westpac.html`, `kiwibank.html`, `rabobank.html`) each show: (1) a header card with bank name, latest-period snapshot values for the 4 key KPIs, and trend direction; (2) sparkline charts for all 20 mapped RBNZ metrics across the full history; (3) a disclosure metrics table (if `disclosure_metrics.json` available, W-0024) showing annual P&L and balance sheet figures; (4) a link to the most recent disclosure PDF from `config/sources.yaml`. Clicking a bank pill or name on `docs/index.html` navigates to the bank's detail page.

### Context

The main dashboard is a cross-bank comparison view — it does not support deep inspection of a single bank. Six static pages avoids a build step and keeps the architecture purely client-side. All data is already in `metrics.json` filtered by entity name. The sparkline layout (small charts, one per metric) gives an at-a-glance health check across every dimension simultaneously. Westpac has no disclosure PDF data (WAF block) — show RBNZ quarterly data only and note the gap.

---

### W-0039

status: ready
created: 2026-04-30
updated: 2026-04-30

### Outcome

Twenty static metric detail pages (`docs/metric/nim.html`, `cet1-ratio.html`, etc. — one per mapped RBNZ metric) each show: (1) the full metric definition from `glossary.md`; (2) the RBNZ series ID and unit; (3) a full-history line chart with all banks; (4) a cross-bank ranking table for the latest quarter; (5) a trailing-12Q trend direction per bank (improving / stable / deteriorating). Clicking a chart title on `docs/index.html` navigates to the metric detail page.

### Context

Metric drill-down is the complement to bank drill-down (W-0038). It answers "how does this specific metric compare across all banks, and over time?" Glossary content (W-0021) is the source of truth for definitions — the metric page embeds the full definition, not a summary. Static HTML with inline JS filtering `metrics.json` by metric name. The metric slug in the URL should match the canonical metric name lowercased and hyphenated for linking consistency.

---

### W-0040

status: ready
created: 2026-04-30
updated: 2026-04-30

### Outcome

A toggle "Indexed (base = 100)" above the chart grid rebases all series to 100 at the earliest available data point for each bank, then renders relative change over time. The toggle state persists in `localStorage["chartMode"]`. Restoring to "Absolute" returns to normal values. An explanatory note under the toggle states "Each bank's first available value = 100."

### Context

Indexed mode is essential for balance sheet metrics (Total Assets, Net Loans, Deposits, Equity) where ANZ ($200bn) and Kiwibank ($37bn) operate at very different absolute scales — absolute comparison is not meaningful for trajectory analysis. Pure client-side transform of chart datasets before Chart.js render. No new data required.

---

### W-0041

status: done
created: 2026-04-30
updated: 2026-05-01

### Outcome

Each chart card gains a download icon (↓) in its top-right corner alongside the fullscreen button (W-0020). Clicking it saves the chart as a PNG named `{metric-slug}-{YYYY-MM-DD}.png` using `canvas.toDataURL('image/png')`. The dark background (`#0d0d0d`) is preserved in the export. No server component.

### Context

Users sharing charts via screenshots loses resolution and metadata. Native canvas export is a one-function addition using Chart.js's built-in canvas API. Pairs naturally with W-0020 (fullscreen) — the export button should be available in both normal and fullscreen modes.

---

### W-0042

status: done
created: 2026-04-30
updated: 2026-05-01

### Outcome

The chart grid on `docs/index.html` is reorganised into four tab categories: **profitability** (NIM, ROE, ROA, Cost-to-Income), **capital** (CET1, Tier 1, Total Capital Ratio, Capital Headroom, LDR), **asset quality** (NPL Ratio, Total Non-Performing Loans), **liquidity** (Core Funding Ratio, 1-month mismatch, 1-week mismatch). The active tab persists in `localStorage["activeTab"]`. Bank selector and date-range filter apply across all tabs. A tab showing zero mapped metrics is hidden until data is available.

### Context

The current single-grid layout works for 4 charts but will become unmanageable as capital, liquidity, and funding metrics are added (W-0030, W-0031, W-0032). Tab categories match the RBNZ XLSX groupings (Capital adequacy, Profitability, Asset quality, Liquidity), which is the logical taxonomy users of this data already know. No navigation to new pages — tab switching is purely client-side visibility toggling.

---

### W-0043

status: done
created: 2026-04-30
updated: 2026-05-01

### Outcome

The Latest Quarter Snapshot table gains: (1) click-to-sort on any column header (ascending/descending toggle, sort direction indicated by ▲/▼); (2) best/worst colour coding per column — teal text for the best-performing bank on each metric, muted red text for the worst; (3) a period selector dropdown allowing the user to choose any historical quarter, not just the latest. Sort state and selected period persist in `localStorage`.

### Context

The snapshot table currently renders in entity-name order with no sorting. For a ranking/comparison use case, sortable columns are a baseline expectation. Colour coding by best/worst replaces the need to mentally scan each column for the extremes. The period selector enables point-in-time historical comparison — "what did the sector look like in 2020-Q2?" — without changing the main chart date range filter.

---

## Phase 7: Insights and Narrative

### W-0044

status: ready
created: 2026-04-30
updated: 2026-04-30

### Outcome

A NIM pass-through analysis panel on `docs/index.html` (Profitability tab) shows: (1) NIM and OCR overlaid on a shared time axis with aligned quarter labels — extending the existing W-0019 overlay; (2) below it, a scatter chart of OCR change (x-axis, bps per quarter) vs NIM change two quarters later (y-axis, bps) — one data point per bank per OCR-change event — with a best-fit trend line per bank. A tooltip on each scatter point shows the bank, the quarter, and the OCR move.

### Context

The lag relationship between OCR changes and bank NIM is the central empirical question this dashboard can answer that no existing RBNZ publication addresses directly. The scatter chart requires: identifying OCR-change quarters from `ocr.json` (delta ≥ 25 bps, same logic as W-0035), looking up NIM at t+2 quarters for each visible bank, computing the NIM change from t-1. All client-side computation from loaded JSON. The two-quarter lag is an empirically common finding for NZ retail banks — the chart will confirm or refute it per bank. Depends on W-0035.

---

### W-0045

status: ready
created: 2026-04-30
updated: 2026-04-30

### Outcome

Each time-series chart gains an optional shaded band between the minimum and maximum value across all visible banks for each period. The band uses a semi-transparent teal fill (opacity 0.08). A "Show range" checkbox beside the sector-average toggle (W-0037) controls visibility. The band narrows where banks converge and widens where they diverge, making dispersion visible without adding individual lines.

### Context

The range band is a low-effort, high-insight addition for understanding sector-wide spread. It is especially useful for NIM (where banks have traditionally moved in lockstep but diverged post-COVID) and for NPL Ratio (where Kiwibank and smaller banks show different credit quality trajectories). Implemented as a Chart.js `fill` between two hidden datasets (min-per-period and max-per-period arrays), computed client-side. Depends on W-0037 (shares the toggle UI infrastructure).

---

### W-0046

status: ready
created: 2026-04-30
updated: 2026-04-30

### Outcome

A ranking section on `docs/index.html` (below the snapshot table) shows a compact heat-map table: rows = banks, columns = KPIs, cells = rank (1 = best) colour-coded by quartile (deep teal for rank 1, white for middle, muted red for last). A toggle switches between "Rank view" and "Value view" (showing actual metric values). The ranking updates with the bank selection and date range filter.

### Context

Rankings make sector-relative performance immediately readable — "ANZ ranks 1st on Cost-to-Income, 3rd on ROE" is the kind of summary that analysts publish in reports. The quartile colour coding (not binary best/worst) gives more nuance than the snapshot table's teal/red extremes (W-0043). Purely client-side computation over `metrics.json` for the selected period.

---

### W-0047

status: ready
created: 2026-04-30
updated: 2026-04-30

### Outcome

A "Sector narrative" panel beneath the chart grid renders 4–6 auto-generated bullet points for the most recent available quarter. Each bullet follows a fixed template: e.g. "Sector NIM averaged X.X%, [up/down] Y bps from the prior quarter — [the highest/lowest] since [period]." / "[Bank] posted the [highest/lowest] ROE at X.X%." / "CET1 ratios [improved/declined] across [N of 6] banks." Templates handle null gracefully (sentence is skipped if the required metric is absent). Generation is client-side from `metrics.json` on page load — no LLM or external service.

### Context

Template-based narrative generation is more auditable and lower-risk than LLM commentary: every sentence traces directly to a data value with a defined template. It gives non-analytical users an entry point without requiring them to interpret the charts. The approach mirrors what financial journalists do manually each quarter. The narrative section carries a small disclaimer: "Auto-generated from RBNZ data — verify before citing."

---

### W-0048

status: ready
created: 2026-04-30
updated: 2026-04-30

### Outcome

Each time-series chart's most recent data point is annotated with a "trend flag": a small coloured dot (teal = improving over last 4Q, grey = stable, red = deteriorating) derived from the trailing linear slope of the series for the currently-visible date range. The flag is shown in the chart legend alongside the bank name. Thresholds: slope magnitude below 0.05 standard deviations per quarter = stable; above = improving or deteriorating based on direction. The metric's "good direction" (higher-is-better vs lower-is-better) is read from a static config map.

### Context

Trend flags make the snapshot table row (▲/▼ vs prior quarter only) more robust by using a 4-quarter slope rather than a single-quarter delta, which is noisy. The "good direction" config (e.g. ROE: higher-is-better; NPL Ratio: lower-is-better; Cost-to-Income: lower-is-better) is a small static lookup — 20 entries. Client-side computation over the date-filtered chart data.

---

## Phase 8: Transparency and Governance

### W-0049

status: done
created: 2026-04-30
updated: 2026-05-01

### Outcome

`docs-adr/0005-pdf-extraction-approach.md` documents: (1) the hybrid `extract_tables()` + `extract_text()` strategy and when each is used; (2) the two extraction patterns — `first_value` (income statement / balance sheet) and `second_pct` (capital ratios, where column 1 is the regulatory minimum and column 2 is the bank's actual ratio); (3) unit normalisation rules (NZDm vs NZD thousands, detected from first 3000 chars of document text); (4) known data gaps — Rabobank balance sheet image-based, Westpac inaccessible via WAF; (5) the decision not to adopt OCR at this stage and the condition under which it would be reconsidered. `docs-adr/README.md` updated with the new entry.

### Context

The extraction approach was spike-driven (S-0004) and implementation decisions are recorded in `learnings.md` and `progress.md`. Formalising as an ADR makes the decisions discoverable and reviewable independently of the session logs. Should be completed before the disclosure integration phase (W-0024–W-0029) to avoid accumulating undocumented decisions on top of an informal foundation.

---

### W-0050

status: ready
created: 2026-04-30
updated: 2026-04-30

### Outcome

`docs/coverage.html` — a data coverage matrix page. Two sections: (1) RBNZ quarterly coverage — a grid of bank × quarter cells, coloured teal where data is present and empty where null, for each mapped metric; (2) Disclosure annual coverage — a grid of bank × period showing which of the 10 extracted metrics were successfully extracted (teal) and which are null (empty, with reason: "image-based page", "PDF inaccessible", "metric not on statement page"). Clicking a teal cell links to the source URL. Footnotes explain each gap category. Navigation link added to the site header.

### Context

Data gaps are unavoidable but must be transparent. Users citing figures from this dashboard need to know whether a null means "bank didn't report" or "pipeline couldn't extract". The coverage page also serves as a living audit — when new PDFs are added or the extraction pipeline is updated, the coverage grid will reflect improvements automatically (generated client-side from `metrics.json` and `disclosure_metrics.json`). Westpac absence from the disclosure section is explained by the WAF block; Rabobank balance sheet nulls are explained by the image-based page.

---

### W-0051

status: ready
created: 2026-04-30
updated: 2026-04-30

### Outcome

`docs/methodology.html` (part of W-0021) is extended with a section documenting the RBNZ capital reform phase-in schedule: the 2019 announcement, the July 2023 implementation start, the full schedule of rising CET1 minimums through 2028, the D-SIB surcharges, and the impact on capital headroom calculations (W-0032). Sources are cited with RBNZ publication URLs. The section is static prose — no pipeline changes.

### Context

The capital headroom chart (W-0032) will be confusing without this explanatory context. The 2019 capital reform is the defining regulatory event of the period covered by this dashboard (2018–2025). Its phase-in schedule is publicly documented by RBNZ but not widely understood. Embedding it in the methodology page ensures users interpret capital trends correctly.

---

## Phase 9: Research Spikes

### S-0005

status: needing_refinement
created: 2026-04-30
updated: 2026-04-30

### Outcome

Must result in: encoding confirmed and W-0034 updated with implementation details — or an explicit no-action decision recorded in `learnings.md` if the data is not useful for visualisation.

### Context

Series IDs are now confirmed by direct XLSX inspection: `DBB.QIA10` (S&P Global), `DBB.QIA20` (Fitch), `DBB.QIA30` (Moody's). The remaining unknowns are encoding and coverage. Inspect the `Series Definitions` sheet and the `Data` sheet rows for these three series to determine: whether values are stored as letter strings (AA-, A+), numeric ordinals, or integer codes; whether the series tracks historical changes or only the current snapshot; and which institutions have non-null values. If ratings are coded as integers, document the mapping table. If historical: W-0034 is viable. If only a static snapshot: not useful for time-series visualisation — explicitly defer with the reason.

---

### S-0006

status: needing_refinement
created: 2026-04-30
updated: 2026-04-30

### Outcome

Must result in: backlog items opened for feasible external data sources — or an explicit no-action decision for each source assessed.

### Context

Economic context enriches bank performance interpretation. Candidate sources, in priority order:

1. **RBNZ B3 / C6 — Mortgage and deposit rates** (monthly XLSX, `rbnz.govt.nz`): shows average 1-year fixed mortgage rate and 6-month term deposit rate — directly relevant to NIM pass-through analysis alongside W-0044. Highest priority.
2. **RBNZ C5 — Housing credit growth** (monthly XLSX, `rbnz.govt.nz`): shows housing lending growth rate. Directly explains loan growth in balance sheet metrics.
3. **RBNZ C31 / CoreLogic HPI** — NZ house price index. RBNZ publishes its own HPI as part of the C31 series (monthly XLSX). Relevant for credit risk context.
4. **Stats NZ — GDP growth**: Quarterly XLSX or CSV download from `stats.govt.nz`. May require navigating the Infoshare API.
5. **Stats NZ — Unemployment rate**: Quarterly HLFS survey. Same channel as GDP.

For each: assess URL accessibility (no WAF), data format, update frequency alignment with quarterly bank periods, and pipeline integration cost. Stats NZ sources may require API registration — if so, flag explicitly and do not open a pipeline item. RBNZ-hosted XLSX sources (items 1–3) are the same pattern as the existing OCR pipeline and are strongly preferred.

Only open pipeline items for sources that are (a) machine-readable via a stable URL, (b) updated at least quarterly, and (c) RBNZ or Stats NZ hosted. Overlays must be toggleable and clearly labelled as macroeconomic context, not bank performance data.

---

### S-0007

status: needing_refinement
created: 2026-04-30
updated: 2026-04-30

### Outcome

Must result in: confirmed NZX API URLs for Westpac disclosure PDFs and W-0015 re-run item opened — or an explicit no-action decision if Westpac remains inaccessible via all channels.

### Context

Westpac is the fourth-largest NZ bank by assets and its absence from the disclosure extraction is a material gap. The WAF at `westpac.co.nz` blocks all pipeline download attempts. The NZX API workaround was used successfully for Kiwibank (the 2024 report was retrieved via `api.nzx.com/public/announcement/436602/attachment/425238/436602-425238.pdf`). Westpac NZ is also NZX-listed and files half-year and full-year disclosure statements as NZX announcements. Investigate: (1) search NZX announcements for "Westpac New Zealand" disclosure statement filings; (2) extract the announcement IDs for the most recent 4 periods; (3) verify the PDF URLs are accessible from the pipeline; (4) validate that the downloaded PDFs are machine-readable via `pdfplumber`. If successful, update `config/sources.yaml` and open a targeted W-0015 extension item.

---

### S-0008

status: needing_refinement
created: 2026-04-30
updated: 2026-04-30

### Outcome

Must result in: a decision on whether to add OCR capability for Rabobank balance sheet extraction — documented in `learnings.md`. If feasible: open an implementation item and ADR-0006 for the OCR dependency. If not: explicitly close the gap with a note that Rabobank balance sheet data remains unavailable.

### Context

S-0004 confirmed that Rabobank's 2022 disclosure statement balance sheet (page 35) is image-based — zero extractable characters, no PDF table objects. Total Assets for Rabobank cannot be extracted without OCR. Rabobank is NZ's sixth-largest bank and has a significant agricultural lending portfolio; its balance sheet scale matters for sector completeness. Investigate: (1) whether `pytesseract` + `tesseract` (system package) can extract the image-based page; (2) whether more recent Rabobank reports (2023, 2024) also have image-based balance sheets or have moved to text-based layouts; (3) the cost-benefit — adding a system-level OCR dependency for one bank's balance sheet. If newer Rabobank reports have text-based balance sheets, update `config/sources.yaml` with the newer URLs and test extraction before committing to an OCR dependency.

---

## Phase 10: Additional Metrics (RBNZ Data)

### W-0052

status: done
created: 2026-04-30
updated: 2026-05-01

### Outcome

`config/metrics.yaml` extended with `DBB.QIB90` (Total Risk-Weighted Assets, NZDm). `metrics.json` regenerated. Two derived metrics added client-side in `docs/index.html`: (1) RORWA (Return on Risk-Weighted Assets = annualised Profit After Tax ÷ RWA, expressed as %) added to the Capital tab; (2) Risk Density (RWA ÷ Net Loans and Advances, expressed as %) shown as a secondary line on the balance sheet chart. Both added to the Latest Quarter Snapshot table. Glossary updated with RORWA and Risk Density definitions.

### Context

RWA (`DBB.QIB90`) is confirmed present in the RBNZ XLSX. Both derived metrics require data already in `metrics.json` (Profit After Tax: `DBB.QIE90`; Net Loans: `DBB.QIG30`). RORWA is often preferred over ROE by analysts because it is capital-structure-neutral — it measures how efficiently a bank generates profit from its risk exposure. Risk Density measures how risky a loan book is relative to its gross size (a rising density means the portfolio is accumulating higher-risk exposures even if loan growth is flat). Per ADR-0001, both are computed in the frontend, not stored.

---

### W-0053

status: done
created: 2026-04-30
updated: 2026-05-01

### Outcome

`config/metrics.yaml` extended with `DBB.QIC60` (Individual Provisions, NZDm) and `DBB.QIC70` (Collective Provisions, NZDm). `metrics.json` regenerated. Provisioning Coverage (Individual + Collective Provisions ÷ Total Non-Performing Loans, expressed as %) is computed client-side and added to the Asset Quality tab (W-0042). A Provision Charge trend chart (quarterly change in total provisions, as a % of Net Loans) is also added — this is the credit cycle indicator. Glossary updated with all three new metrics.

### Context

Provisioning series (`DBB.QIC60`, `DBB.QIC70`) confirmed present in the RBNZ XLSX. Total Non-Performing Loans (`DBB.QIC50`) is already mapped. Provisioning Coverage tells you whether banks are adequately reserved against known bad loans. The quarterly provision charge (delta of total provisions) is the credit cycle metric — it spikes in downturns (COVID-Q1 2020 was a significant provisioning event) and releases in recoveries. Both are high-signal for credit risk assessment.

---

### W-0054

status: done
created: 2026-04-30
updated: 2026-05-01

### Outcome

`config/metrics.yaml` extended with `DBB.QIJ10` (top 5 non-bank credit exposures / CET1, %), `DBB.QIJ30` (top 5 bank counterparty exposures / CET1, %), `DBB.QIJ40` (bank exposures ≥10% of CET1, number). `metrics.json` regenerated. A Credit Concentration panel is added to the Liquidity tab (W-0042): a line chart of QIJ10 and QIJ30 over time, plus a bar chart of QIJ40 (count of large bank exposures). Glossary updated.

### Context

Credit concentration series confirmed in RBNZ XLSX (QIJ section). These metrics reveal systemic interconnectedness — how exposed each bank is to a small number of large counterparties. QIJ40 (count of bank exposures above 10% of CET1) is particularly useful: a value of zero means no individual bank counterparty represents more than 10% of CET1 capital; values above zero signal concentration risk. Context is important — NZ's small market means some concentration is structural.

---

## Phase 11: Derived Profit and Efficiency Metrics

### W-0055

status: ready
created: 2026-04-30
updated: 2026-04-30

### Outcome

A Pre-Provision Profit (PPP) line chart is added to the Profitability tab (W-0042). PPP = Net Interest Income + Trading and Hedging Gains + Fees and Commission Income + Other Income − Operating Expenses (all already in `metrics.json`). PPP in NZDm per quarter, per bank. A secondary view shows PPP as a % of Average Total Assets (pre-provision ROA). Both computed client-side. Glossary updated with Pre-Provision Profit definition.

### Context

Pre-Provision Profit isolates underlying operating performance from the credit cycle. During COVID (2020) and any future downturn, banks may post sharply lower NPAT due to provisioning, even while their operating engine is healthy. Conversely, provision releases can inflate NPAT in good times. PPP strips both effects and gives a cleaner read on fee income and cost management. All five component series are already in `metrics.json` — no new data required.

---

### W-0056

status: ready
created: 2026-04-30
updated: 2026-04-30

### Outcome

An income diversification chart is added to the Profitability tab: a 100% stacked area chart showing the composition of total operating income over time for each bank — Net Interest Income, Trading and Hedging Gains, Fees and Commission Income, Other Income. A secondary line shows Non-Interest Income as % of Total Operating Income (income diversification ratio). Computed client-side from already-mapped series. Glossary updated with Income Diversification Ratio definition.

### Context

NZ retail banks are heavily NII-dependent (typically 80–90% of operating income). The non-interest income share is a structural moat indicator — banks with higher fee and trading income are less sensitive to rate cycles. The 100% stacked area chart makes the composition shift visible over time. All four income component series are already in `metrics.json` (mapped in W-0017). No new data.

---

### W-0057

status: ready
created: 2026-04-30
updated: 2026-04-30

### Outcome

An impairment charge trend chart is added to the Asset Quality tab (W-0042). The chart shows the quarterly credit impairment charge as a % of average Net Loans and Advances — derived client-side from the delta of Total Non-Performing Loans (`DBB.QIC50`) divided by Net Loans (`DBB.QIG30`). A shaded band marks the long-run average. An event annotation (W-0036 infrastructure) marks the COVID provisioning spike (2020-Q1 and 2020-Q2). Glossary updated with Credit Impairment Rate definition.

### Context

The impairment charge as % of loans is the cleanest indicator of where the credit cycle is. NZ banks provisioned heavily in early 2020 (COVID) then released provisions through 2021–2022 as defaults did not materialise. The current level (post-rate-hike cycle) is worth monitoring — rising mortgage arrears could drive provisioning up again. The delta of Total NPLs is an approximation for the gross impairment charge; the exact figure requires the disclosure income statement (Credit Impairment Charge line, W-0026 data source). Both approaches should be shown with a note on the approximation.

---

### W-0058

status: ready
created: 2026-04-30
updated: 2026-04-30

### Outcome

An opex intensity metric — Operating Expenses ÷ Total Assets (expressed as basis points of assets per annum) — is computed client-side and added to the Profitability tab alongside Cost-to-Income Ratio. A chart shows opex intensity as lines per bank over the full quarterly history. Glossary updated with Opex Intensity definition.

### Context

Cost-to-Income Ratio captures efficiency relative to revenue; opex intensity captures efficiency relative to asset scale. A bank growing its balance sheet rapidly may see its Cost-to-Income ratio improve even if absolute costs are rising — opex intensity would reveal this. The two metrics together give a complete picture. Operating Expenses (`DBB.QIE60`) and Total Assets (`DBB.QIG10`) are already in `metrics.json`. No new data.

---

## Phase 12: Pipeline Maturity

### W-0059

status: ready
created: 2026-04-30
updated: 2026-04-30

### Outcome

`scripts/download_disclosures.py` is extended (or a new script created) to batch-download all disclosure PDFs with `status: confirmed` in `config/sources.yaml`, saving each to the correct `output_dir` path with its `.meta.json` sidecar. The script is idempotent (skips already-downloaded files). A GitHub Actions workflow `download-disclosures.yml` with `workflow_dispatch` trigger runs the script. Download failures are logged as `WARNING` (not `ERROR`) — a failed URL does not abort the entire batch.

### Context

Currently PDFs are committed to the repo individually. Automating downloads means new disclosure periods can be added to `config/sources.yaml` and downloaded with a single workflow run, without committing binaries. Westpac and any other WAF-blocked banks will fail gracefully with a WARNING. The script reuses the existing `src/ingestion/fetch.py` HTTP client. Tests in `tests/test_download_disclosures.py` already exist — extend them for batch mode.

---

### W-0060

status: done
created: 2026-04-30
updated: 2026-05-01

### Outcome

A data freshness badge is added to the site header showing "RBNZ data as at: YYYY-QN" and "Disclosures as at: [most recent period_end]". The values are read from `metrics.json` (max period value) and `disclosure_metrics.json` (max period_end value) on page load. The badge text is teal-coloured and updates automatically as new data is published.

### Context

Users need to know whether they are looking at current data. The RBNZ publishes the dashboard quarterly — if a user visits several weeks after a new quarter's data is available, a stale badge would reveal the data needs refreshing. The values are fully derivable client-side from loaded JSON (max period across all rows). No pipeline changes needed.

---

### W-0061

status: ready
created: 2026-04-30
updated: 2026-04-30

### Outcome

`.github/workflows/fetch-data.yml` gains a `schedule` trigger: `cron: '0 6 1 * *'` (6am UTC on the 1st of each month). When triggered automatically, the workflow checks whether the RBNZ XLSX has changed since the last committed version (SHA comparison or file-size check); if unchanged, it exits without committing. If changed, it downloads, commits, and triggers the process-data workflow. A `[skip ci]` flag is NOT used — the process pipeline should run on the auto-commit.

### Context

The RBNZ updates the dashboard quarterly (approximately March, June, September, December). A monthly check is a reasonable polling frequency — it will miss no quarterly publication and wastes minimal Actions minutes. The existing `fetch-data.yml` has only a `workflow_dispatch` trigger. The idempotency requirement (ADR from W-0009) is already satisfied by the overwrite-at-fixed-path pattern. No code changes needed — only workflow YAML.

---

## Phase 13: Cross-Linking and Navigation

### W-0062

status: ready
created: 2026-04-30
updated: 2026-04-30

### Outcome

The site URL encodes current filter state as a hash fragment: `#banks=ANZ,ASB&range=Last+8Q&tab=profitability`. Any change to the bank selector, date range, or active tab updates the URL hash client-side (using `history.replaceState`). On page load, if a hash is present, its values override the `localStorage` defaults. Sharing the URL reproduces the exact view. A "Copy link" button (📋) beside the date range bar copies the current URL to the clipboard.

### Context

Shareable URLs are a basic requirement for a research tool used collaboratively. The current implementation persists state in `localStorage` only — useful for returning users but not for sharing a specific view. Hash-based routing requires no server and no build step. The state encoding is minimal (bank list, range preset name, tab name) and backward-compatible — a URL without a hash loads with defaults as before.

---

### W-0063

status: ready
created: 2026-04-30
updated: 2026-04-30

### Outcome

A "Download data" button is added to the dashboard header. Clicking it downloads a CSV of the currently-filtered data (active banks, date range, all metrics) using the Blob API. The CSV follows the canonical schema (`entity,metric,value,period,source`) with a header row. File named `nz-bank-performance-[date-range].csv`.

### Context

Power users (analysts, researchers) need raw data access to run their own calculations. The canonical `metrics.json` is already fully accessible in the repo, but a filtered CSV export removes friction for non-technical users. Pure client-side: filter the in-memory data, serialize to CSV string, create a Blob URL, trigger a download link. No server, no pipeline changes.

---

### W-0064

status: ready
created: 2026-04-30
updated: 2026-04-30

### Outcome

A period/quarter snapshot page `docs/snapshot.html` shows all key metrics for a single selected quarter: a card grid (one card per bank, columns = KPIs) and a bar chart per metric showing all banks side by side. A quarter selector (dropdown of all available periods) controls the view. The page is linked from the snapshot table header on `docs/index.html` ("Full snapshot →"). Default period is the most recent available quarter.

### Context

The snapshot table on `docs/index.html` is compact by design. A dedicated snapshot page gives the point-in-time view more space — useful for quarterly reporting ("what did the sector look like at end-2024?"). This complements the time-series focus of the main dashboard. Sourced entirely from `metrics.json` filtered by period client-side. No new data.

---

## Phase 14: Insights Enhancements

### W-0065

status: ready
created: 2026-04-30
updated: 2026-04-30

### Outcome

The snapshot table and ranking table (W-0046) gain anomaly flags: a ⚠ icon on any metric value that deviates more than 2 standard deviations from that bank's own trailing 8-quarter history. Hovering the flag shows: "X.X% — [N]σ above/below trailing 8Q average of Y.Y%". The flag uses the currently-selected date range for the trailing window. Computed client-side from `metrics.json`.

### Context

Anomaly flags direct analyst attention to the most significant data points without requiring manual comparison. A 2σ threshold against a bank's own history (not cross-sectional) is the right benchmark — it captures unusual movement for that specific bank, accounting for structural differences between banks. The 8-quarter trailing window is long enough to be stable but short enough to be responsive to structural shifts. False positives are acceptable — the flag invites investigation, not alarm.

---

### W-0066

status: ready
created: 2026-04-30
updated: 2026-04-30

### Outcome

A "Peer group" filter is added to the bank detail pages (W-0038). Rather than comparing a bank to all 6 top banks, the user can select a peer group: "Big 4" (ANZ, ASB, BNZ, Westpac), "NZ-owned" (Kiwibank), "All standalone". On each bank detail page, the sector average line (W-0037) recalculates using only the selected peer group. The peer group selection persists in `localStorage["peerGroup"]`.

### Context

Kiwibank and Rabobank operate very differently from the Big 4 — comparing them to ANZ directly is misleading for some metrics (NIM, cost base, capital ratios). Peer group filtering lets users make contextually appropriate comparisons. Big 4 peer group excludes Kiwibank and Rabobank from the average on a bank detail page where those banks are less relevant comparators.

---

## Phase 15: Skills Submodule and Governance

### W-0067

status: done
created: 2026-04-30
updated: 2026-04-30

### Outcome

`.github/skills/` submodule is initialised: `git submodule update --init --remote` pulls the content of `davidamitchell/Skills`. The skills files are confirmed present in the directory. `copilot-instructions.md` is updated to reference any relevant skill files by name.

### Context

The submodule is registered in `.gitmodules` (pointing to `davidamitchell/Skills`) but the directory is currently empty — the submodule has not been initialised in this environment. Skills files in the submodule contain agent instruction patterns that align AI-assisted development across davidamitchell repositories. Without initialisation, agent sessions cannot use those patterns. This is a one-command fix. No code changes required.

> **Note to agent**: Do not run `git submodule update --init` without confirming network access to `github.com` is available in the current environment. The previous session (W-0016) confirmed that some CDNs are blocked; test with a `git ls-remote` check first.

---

### W-0068

status: ready
created: 2026-04-30
updated: 2026-04-30

### Outcome

A structured `CHANGELOG.md` is added to the repo root, tracking significant data pipeline changes and schema updates by date. Initial entries cover: W-0010 (first processed data), W-0015 (disclosure extraction), W-0019 (OCR overlay), the metrics.yaml additions in W-0017, and the upcoming W-0030 and W-0052–W-0054 metric additions. Format: `## YYYY-MM-DD — [change summary]` with bullet points per change.

### Context

As the schema evolves (new metrics mapped, new sources added), users who have downloaded CSVs or built analyses on top of `metrics.json` need to know what changed and when. A changelog is lower overhead than a full versioning scheme and appropriate for this stage. It is maintained manually alongside each schema-affecting backlog item — add a CHANGELOG entry as part of the "done" definition for any item that modifies `config/metrics.yaml` or the canonical schema.

---

## Phase 16: Research Spikes (Additional)

### S-0009

status: needing_refinement
created: 2026-04-30
updated: 2026-04-30

### Outcome

Must result in: RBNZ C6 (or equivalent) mortgage and deposit rate series confirmed accessible and a pipeline item opened — or an explicit no-action decision.

### Context

The RBNZ publishes average mortgage rates (1-year fixed, 2-year fixed) and term deposit rates monthly as part of its B3 or C6 statistical series. These are directly relevant to the NIM pass-through analysis (W-0044): the gap between the OCR and the retail mortgage/deposit rate is where bank margin lives. If accessible (same RBNZ domain as the OCR series), adding mortgage and deposit rate overlays to the NIM chart would make the margin decomposition visible without any modelling. Assess URL, format, and column structure using the same approach as the OCR series spike.

---

### S-0010

status: needing_refinement
created: 2026-04-30
updated: 2026-04-30

### Outcome

Must result in: a decision on whether to extract note-table data from bank disclosure PDFs — backlog item opened if feasible, or explicit deferral with reason.

### Context

S-0004 confirmed that statement-page extraction (income statement, balance sheet) is working. However, several high-value metrics are only available in note tables: personnel vs non-personnel opex breakdown (Note to Operating Expenses), interest income by product class (Note 2 in Kiwibank, Note 4 in Rabobank), agricultural lending exposure (capital adequacy notes), and RWA by exposure class from the IRB approach tables. Extracting note tables requires `extract_tables()` for most banks (ANZ, ASB, Kiwibank use table-based notes) and `extract_text()` for BNZ and Rabobank. Assess: (1) can the existing extraction framework be extended to target specific note numbers? (2) what is the structural consistency of note tables across years and banks? (3) what specific metrics would be unlocked and are they worth the added fragility? Focus on personnel opex and agricultural exposure as the highest-priority targets.

---

### S-0011

status: needing_refinement
created: 2026-04-30
updated: 2026-04-30

### Outcome

Must result in: understanding of what agricultural lending data exists across RBNZ and disclosure sources — and a backlog item if a viable extraction path exists, or explicit no-action.

### Context

NZ banking is materially exposed to agricultural lending — ANZ, BNZ, and Rabobank have significant agri books (Rabobank is almost exclusively agricultural). Agricultural lending is more cyclical and weather-dependent than retail mortgages, and is a distinct risk factor. The RBNZ XLSX may contain agricultural lending sub-series in the asset quality section (beyond the total NPL/total loans figures already mapped). Disclosure capital adequacy notes (RWA by exposure class) also include agricultural/rural exposure. Investigate: (1) whether RBNZ series QIC or QIG have agricultural sub-series; (2) whether disclosure note tables can provide agricultural NPL or loan volume data; (3) whether RBNZ publishes standalone agricultural lending statistics in a separate series. The goal is to add an agricultural exposure lens to the Asset Quality tab.

---

## Phase 17: Engineering Quality (from Skills Review)

### W-0069

status: needing_refinement
created: 2026-04-30
updated: 2026-04-30

### Outcome

The client-side JavaScript in `docs/index.html` and related static pages has a unit test suite covering: date-range filter logic, bank selector state, chart dataset computation (Cost-to-Income derivation, LDR derivation, sector average calculation, indexed-mode rebase), and the OCR event detection algorithm. Tests run without a browser using a DOM mock (jsdom via Jest or equivalent). The test suite is added to `package.json` and invoked from `.github/workflows/ci.yml`.

### Context

The `tdd` skill surfaces a structural gap: the frontend contains non-trivial algorithmic logic (derived metric computation, filter state management, OCR delta detection) with zero automated test coverage. This logic has no feedback loop shorter than manual browser testing. The gap costs most for the derived metrics (Cost-to-Income, LDR, RORWA, Provisioning Coverage) where a formula error is invisible without tests. No build step is required for the production site; the test toolchain is development-only and does not affect the static output.

Challenge: The project has no `package.json` or Node tooling. Adding Jest introduces a new runtime dependency for development. Assess whether `vitest` (lighter, no config) or plain `node --test` (no extra dependency) is sufficient before committing to Jest. Document the choice in an ADR if it introduces new dev tooling.

---

### W-0070

status: ready
created: 2026-04-30
updated: 2026-04-30

### Outcome

All existing ADRs in `docs-adr/` (ADR-0001 through ADR-0004) gain YAML front matter (`title`, `status`, `date`, `authors`, `tags`, `supersedes`, `superseded_by`) and coded bullet identifiers (POS-001, NEG-001, ALT-001, IMP-001, REF-001) in the Consequences, Alternatives, Implementation Notes, and References sections. The format matches the `adr` skill standard. `docs-adr/README.md` index is updated. All future ADRs (starting with ADR-0005 from W-0049) use this format from the start.

### Context

The `adr` skill defines a richer format than the MADR format currently in use. The additions are not cosmetic: YAML front matter enables machine parsing and cross-referencing; coded bullet IDs make individual consequences citable across items; `superseded_by` fields preserve the audit trail when decisions change. The existing four ADRs cover load-bearing decisions (data format, directory structure, manual RBNZ file, data contract) and are worth upgrading.

---

### W-0071

status: ready
created: 2026-04-30
updated: 2026-04-30

### Outcome

A code review standard is added to `.github/copilot-instructions.md` under a new `## Code Review Standard` section. The checklist covers: correctness (output matches stated outcome), data accuracy (metric values sourced, not edited), test coverage (every new Python function has a test; every new derived metric formula has a client-side test once W-0069 is done), security (no credentials or raw data in `docs/`), idempotency (workflows produce the same result on re-run), and ADR compliance (new architectural choices have an ADR before merging). The standard applies to all PRs before merging.

### Context

The `code-review` skill defines a systematic multi-dimensional review process. The project has no documented PR review standard. Embedding the checklist in `copilot-instructions.md` means agent sessions working on PRs apply it automatically. It does not replace human review but raises the baseline for agent-authored PRs, which currently represent all PRs.

---

### W-0072

status: ready
created: 2026-04-30
updated: 2026-04-30

### Outcome

The auto-narrative panel templates (W-0047) pass a `plain-language` review before the feature ships: each generated sentence is at or below a Year 10 reading level, financial terms are either defined inline or linked to the glossary, and the output is readable by a non-specialist without additional context. Five example narrative outputs (one per bank selection scenario) are documented alongside the template strings as test fixtures. The glossary definitions on `docs/glossary.html` receive the same review pass.

### Context

The `plain-language` skill applies directly here: the narrative panel and glossary target a mixed audience including journalists and policy researchers who are not bank analysts. Jargon in the templates propagates to every generated sentence. Reviewing the prose before shipping the feature is cheaper than retrofitting after. This is a writing review pass, not a code change.

---

### W-0073

status: ready
created: 2026-04-30
updated: 2026-04-30

### Outcome

The `remove-ai-slop` pre-commit checklist has been applied to all user-facing prose in the static site: `docs/glossary.html`, `docs/methodology.html`, `docs/lineage.html`, and the narrative panel templates (W-0047). Specific targets: em dashes removed throughout, passive constructions named and rewritten, AI vocabulary words replaced (`fundamentally`, `crucially`, `highlight`, `underscore`, `tapestry`), and no sentence opening with a Wh- word. `glossary.md` is updated as the source of truth. A prose-only PR, no pipeline changes.

### Context

The `remove-ai-slop` skill identifies patterns that reduce credibility in research contexts. User-facing content cited by analysts and journalists carries a higher standard. `glossary.md` already contains formulaic prose ("Measures X. Expressed as a percentage.") that will be visible on the public site. This pass makes the prose sound like it was written by a person with domain knowledge, not generated. Belongs after W-0021 (transparency pages) is built so the full prose surface exists before the review.

---

## Phase 17.5: Extraction Quality Fixes

### W-0074

status: done
ASB "Net Loans and Advances" extraction is fixed. The existing regex `r"(?:net )?loans and advances\b"` misses ASB's label format ("Loans and advances" without the word "Net" and without the trailing word boundary matching "to customers" or similar suffix). The updated pattern is validated against all 16 ASB PDFs in the corpus and the metric is present in `disclosure_metrics.json` for all ASB periods. `tests/test_extract_disclosures.py` gains a test for the ASB label variant. W-0024 learnings.md entry updated to reflect the fix.

### Context

End-to-end run (W-0024, 2026-05-01) showed ASB "Net Loans and Advances" absent from all 16 ASB periods. Root cause: ASB balance sheet uses "Loans and advances" (no "Net" prefix, lowercase) which fails the existing regex. This is a TDD fix: write a failing test with an ASB-format line, extend the pattern, verify the test passes, re-run the full corpus. Low effort — one regex extension. Unblocks ASB completeness for the disclosure charts (W-0025).
---

## Phase 18: Labour and Customer Productivity Metrics

### S-0012

status: open
created: 2026-05-01
updated: 2026-05-01

### Outcome

FTE employee count data sourcing investigated for the six major NZ banks (ANZ, ASB, BNZ, Westpac, Kiwibank, Rabobank). Findings recorded in `learnings.md`. A reference employee table committed to `data/reference/employees.csv` with columns `bank_id | period_end | fte | source | confidence` (confidence: `exact` / `triangulated` / `estimated`). Backlog updated with any follow-on implementation items.

### Context

Per-employee productivity metrics (W-0075) cannot be computed without reliable FTE data. This spike establishes which banks disclose FTE in their General Disclosure Statements and where triangulation is required. Sources to assess:
1. General Disclosure Statements / annual reports — FTE disclosed as a note or in the operational section.
2. Stats NZ Business Demography — employee bands (linked via NZBN); provides a floor/ceiling range.
3. KPMG FIPS annual banking survey — typically reports system-wide and per-bank FTE.
4. NZBA benchmarks — aggregate ~29,000 FTE (majors ~26,000); useful for sanity checks.
5. Historical public estimates: ANZ NZ ~9,000; ASB ~6,000; BNZ ~5,000; Westpac NZ ~5,000; Kiwibank ~2,500; Rabobank ~400.

Must result in: `data/reference/employees.csv`, `learnings.md` update, backlog update or explicit no-action.

---

### S-0013

status: open
created: 2026-05-01
updated: 2026-05-01

### Outcome

Active retail customer count estimation investigated for the six major NZ banks. Findings recorded in `learnings.md`. A reference customer table committed to `data/reference/customers.csv` with columns `bank_id | period_end | active_customers | unique_customers | estimation_method | confidence`. Backlog updated with any follow-on implementation items.

### Context

Per-customer productivity metrics (W-0076) require an active customer denominator. No single authoritative public source exists; estimation is required. Sources to assess in order of reliability:
1. NZBA Retail Banking Insights — industry-level unique retail customers (~10M as at H2 2024; ~9.97M).
2. Individual bank General Disclosure Statements — some disclose retail customers, active digital users, or account volumes.
3. Account-to-customer proxy: total accounts ÷ 2–4 (typical accounts-per-customer ratio for NZ banks).
4. Deposit proxy: retail deposits ÷ assumed average deposit per customer ($10k–$30k range) — macro sanity check only.
5. Active adjustment: apply 75–90% of unique customer count to approximate "transacted within 90–180 days" definition.
6. Published customer figures: Kiwibank >1M; majors each typically 0.8M–2M+ active retail.

Must result in: `data/reference/customers.csv`, `learnings.md` update, backlog update or explicit no-action.

---

### W-0075

status: open
created: 2026-05-01
updated: 2026-05-01

### Outcome

`data/reference/` directory created with two canonical reference files:
- `data/reference/employees.csv` — FTE employee counts per bank per period (output of S-0012).
- `data/reference/customers.csv` — active retail customer estimates per bank per period (output of S-0013).

Both files follow the canonical schema extension: `bank_id | period_end | value | source | confidence`. A `config/reference.yaml` file documents each reference file's schema, provenance, and update cadence. Reference files are committed to git (not gitignored) and updated manually when new bank reports are published.

### Context

Depends on S-0012 and S-0013. Reference files are static inputs to the processing pipeline (W-0076, W-0077); they are not fetched automatically because no machine-readable public API exists for FTE or active-customer data.

---

### W-0076

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

Depends on W-0075 (reference files populated), W-0010 (metrics.csv present), and S-0012/S-0013 (denominators validated). Annualisation: half-year values × 2; quarterly values × 4. Half-year is the standard NZ bank disclosure period, so most values will use ×2 annualisation. Log a `WARNING` if annualisation factor cannot be determined from the period string.

---

### W-0077

status: open
created: 2026-05-01
updated: 2026-05-01

### Outcome

`.github/workflows/compute-productivity.yml` added. The workflow runs after `process-data.yml` succeeds (or can be triggered manually with `workflow_dispatch`). It runs `python scripts/compute_productivity.py` and commits `data/processed/productivity.csv` and `docs/data/processed/productivity.json` idempotently (using `git diff --cached --quiet` guard).

### Context

Depends on W-0076. Follows the same idempotent commit pattern as `process-data.yml` and `fetch-data.yml`.

---

### W-0078

status: open
created: 2026-05-01
updated: 2026-05-01

### Outcome

Frontend `docs/index.html` gains a new **Productivity** tab alongside the existing metric categories. The tab displays two chart groups:

- **Per-employee charts**: Profit per Employee, Gross Income per Employee, Expenses per Employee — one line chart per metric, all six banks, all available periods.
- **Per-customer charts**: Profit per Customer, Gross Income per Customer, Expenses per Customer — same layout.

Charts follow the existing dark-mode Chart.js pattern (IBM Plex Mono, teal accent, `#252b33` border). A confidence badge (🔵 Exact / 🟡 Triangulated / 🔴 Estimated) is shown per bank per period in tooltips, sourced from the `confidence` field in `productivity.json`. If `productivity.json` is absent or all denominators for a bank are missing, that bank's series is silently omitted from productivity charts (graceful degradation). A data-sources note is added below the charts explaining triangulation methodology and linking to `docs/methodology.html`.

### Context

Depends on W-0077 (productivity.json published) and W-0023 (shared design system in place). Consistent with W-0021 (methodology page) which should reference the triangulation approach documented in S-0012 and S-0013.

---
