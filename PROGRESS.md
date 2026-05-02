# Progress

> Session logs and completion notes.
Last updated: 2026-05-01 (Phase 19 UI layout items W-0079 through W-0088)

---

## Current Status

**Phase:** Phase 19 — UI Layout and Information Architecture (complete)
**Active work:** Next — W-0032 (Capital headroom), W-0021 (Transparency pages), W-0047 (Auto-narrative), W-0062 (URL state sharing)
**Next phase:** Phase 7 Insights / Phase 12 Pipeline Maturity

---

| Phase | Title | Status |
|---|---|---|
| 1 | Standardisation and Governance | Done |
| 1.5 | Data Modelling and Source Definition | Done |
| 2 | Automated Data Pipeline | Done |
| 2.5 | Discovery / Research Spikes | Done |
| 3 | Visualisation and Deployment | In progress (W-0013 manual step remaining) |
| 4 | Qualitative Data Extraction | Deferred |
| 19 | UI Layout and Information Architecture | Done |

---

## Work Log

### 2026-05-01 — Phase 19: UI Layout and Information Architecture (W-0079 through W-0088)

**Items completed:**

- **W-0079**: Sticky control bar — bank selector + controls moved out of page-header into `position: sticky; top: 48px` `.sticky-controls` div. Page header retains only h1, subtitle, status, and freshness.
- **W-0080**: Summary KPI row — 4-card summary section before chart tabs; sector-average CET1/ROE/CTI/NIM with best/worst bank per metric. `renderKpiRow()` added, called from `render()`.
- **W-0081**: Labelled fieldsets — Period and Overlays controls grouped into `<fieldset class="ctrl-group">` elements side-by-side in `.controls-row`.
- **W-0082**: Accessibility — skip link, `aria-label="Site"` on nav, `id="main-content"` on all `<main>`, `aria-label` on all sections. Skip-link CSS added to theme.css.
- **W-0083**: Consistent nav — `<a href="index.html">Dashboard</a>` added as first nav-links item on all inner pages. `aria-current="page"` on active links.
- **W-0084**: Disclosures page reorder — Coverage summary now comes before metric charts (new order: coverage → charts → statements).
- **W-0085**: Subtitles and captions — `class="page-subtitle"` on all pages; `<caption>` on snapshot and disclosures tables; `scope="col"/"row"` on headers and bank cells.
- **W-0086**: Mobile table scroll — `table-scroll-wrap` class with `overflow-x: auto` and `min-width: 600px`; sticky first column for snapshot table.
- **W-0087**: Standardised footer — consistent `<nav aria-label="Footer">` + attribution on all four pages. `footer nav` styles added to theme.css.
- **W-0088**: Persist bank selection — `localStorage["selectedBanks"]` read on init, saved on every change. Period range was already persisted.

**Mini-retro:**
- Did the process work? Yes — all 10 items implemented in one pass; 192 Python tests still pass.
- What slowed things down? Nothing material; all changes were pure HTML/CSS/JS.
- Is this a pattern? Yes — Phase 19 items were individually small; future UI-only phases should be committed as a single batch rather than tracked as 10 separate items.



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
- `BACKLOG.md` populated with all phases and work items
- `PROGRESS.md` initialised (this file)
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

---

### 2026-04-28 — S-0004: Financial disclosures spike, URL research, config, and validation tooling

**What was done:**

- **S-0004 spike**: Authored `scripts/spike_bnz_pdf.py` to download and inspect the
  BNZ September 2024 full-year disclosure statement PDF using `pdfplumber`. The script
  saves structured findings to `data/raw/financial_disclosures/bnz/spike_s0004_bnz_findings.json`.
  Spike must be run manually (network access required); findings template recorded in
  `docs/spikes/s-0004-findings.md`.

- **URL research**: All six bank disclosure statement URLs researched across 2018–2024
  reporting periods. Total 82 report URLs catalogued:
  - ANZ: 14 confirmed, 0 pending
  - ASB: 13 confirmed, 0 pending
  - BNZ: 11 confirmed, 3 pending (2023-03-31, 2021-03-31, 2018-09-30)
  - Westpac: 13 confirmed, 1 pending (2024-09-30 — may not yet be published)
  - Kiwibank: 4 confirmed, 9 pending (inconsistent filenames; all pending must be HTTP-validated)
  - Rabobank: 12 confirmed, 2 pending (2024-12-31, 2024-06-30)

- **Config written**: `config/sources.yaml` updated with three top-level sections:
  `rbnz` (unchanged), `ocr` (new — RBNZ B2 series for OCR/interest rate context),
  and `financial_disclosures` (new — 6 banks with full report lists).

- **Validation script**: `scripts/validate_disclosure_urls.py` written. Performs HTTP
  HEAD requests against all disclosure URLs and updates `status` fields in YAML.
  Writes per-URL results to `data/raw/financial_disclosures/url_validation.json`.

- **Tests**: `tests/test_validate_disclosure_urls.py` added — 9 tests covering 200/404/
  connection-error/timeout cases and JSON output structure. No real network calls.

- **Dependencies**: `requests>=2.32.0` and `pdfplumber>=0.11.0` added to `pyproject.toml`
  and `requirements.txt`.

**What was found / decided:**

- Three distinct BNZ URL patterns exist across years (2023+, 2021–2022, 2018–2020);
  documented in `config/sources.yaml` inline comments.
- Kiwibank uses a media subdomain with inconsistent naming — no clean template pattern.
  All inferred URLs must be HTTP-validated before ingestion.
- `pdfplumber` is sufficient for the spike (no LLM dependency decision yet).
  ADR will only be written after the spike is run and machine-readability is assessed.

**Blockers / open questions:**

- Spike script requires live internet access and a valid BNZ PDF URL — must be run
  manually. `docs/spikes/s-0004-findings.md` is a template pending those results.
- 16 pending URLs (BNZ ×3, Westpac ×1, Kiwibank ×9 + recount, Rabobank ×2) must be
  validated by running `scripts/validate_disclosure_urls.py`.
- ADR-0005 (extraction approach) deferred until spike findings are reviewed.

**Mini-retro:**

- *Did the process work?* Yes — URL research, config authoring, and tooling all
  completed in one session with no backtracking.
- *What slowed things down?* Kiwibank filenames are non-deterministic (random suffixes
  in older files, capitalisation inconsistencies). Required manual pattern inference.
- *Single change to prevent that next time?* Add a URL validation step (now done via
  `scripts/validate_disclosure_urls.py`) as a required gate before any URL enters
  `config/sources.yaml` as `confirmed`.
- *Is this a pattern requiring a root-cause fix?* Yes — the root cause is that banks
  do not follow consistent URL conventions. The validation script is the structural fix;
  add it to the fetch workflow as a pre-check step (backlog item).


---

## 2026-04-30 — W-0015, W-0019, W-0022: PDF extraction, OCR overlay, date-range filter

**Items completed:**

### W-0015 — PDF disclosure extraction pipeline

- `src/processing/extract_disclosures.py`: text extraction from bank disclosure PDFs using `pdfplumber`. Extracts 10 quantitative metrics (Net Interest Income, Total Operating Income, Operating Expenses, Profit After Tax, Total Assets, Net Loans and Advances, Deposits, Equity, CET1 Ratio, Total Capital Ratio). Normalises: brackets = negative, comma thousands, NZD thousands scale (÷1000). Outputs canonical rows `entity | metric | value | period | source`. Only processes PDFs with a `.meta.json` sidecar.
- `scripts/process_disclosures.py`: writes `data/processed/disclosures.csv` and `docs/data/processed/disclosures.json`.
- `tests/test_extract_disclosures.py`: 34 tests covering happy path, bracketed negatives, NZD thousands normalisation, missing sidecar, empty extraction, source field, period format.

### W-0019 — OCR overlay on NIM chart

- `src/processing/parse_ocr.py`: reads RBNZ B2 XLSX, detects OCR column (case-insensitive), converts monthly → quarterly (last value per quarter), outputs canonical rows `entity=RBNZ | metric=OCR | source=rbnz-ocr`. Falls back to any `rbnz-ocr*.xlsx` in `data/raw/` if primary path absent.
- `scripts/process_ocr.py`: writes `data/processed/ocr.csv` and `docs/data/processed/ocr.json`.
- `docs/index.html`: loads `ocr.json` alongside `metrics.json`. NIM chart gains a teal dashed secondary y-axis line (OCR %) on the right side. Graceful degradation: NIM chart renders normally if `ocr.json` fetch fails.
- `tests/test_parse_ocr.py`: 20 tests covering happy path, monthly-to-quarterly conversion, missing file, no OCR column, fallback glob, canonical schema.

### W-0022 — Date-range filter

- `docs/index.html`: date-range filter bar above charts with four presets (`Last 4Q`, `Last 8Q`, `Last 16Q`, `All`). Active button styled teal border (`#00C3A5`). Clicking a preset filters ALL charts and the snapshot table client-side. Preset persists in `localStorage["rangePreset"]` and is restored on page load. Entity filter operates independently.

**W-0016 — marked wont-do**: Kiwibank and Westpac CDNs block pipeline downloads (WAF / timeout). Not fixable without manual intervention.

**Mini-retro:**

- *Did the process work?* Yes — spike S-0004 findings were precise enough to design the extraction regex patterns without reading any additional PDF pages.
- *What slowed things down?* Capital ratio extraction needed a "second percentage" strategy distinct from the "first value" strategy used for income/balance sheet metrics. This required a separate extraction path.
- *Single change to prevent that next time?* Document the two extraction strategies (first_value vs second_pct) in the spike output before implementation begins, so the distinction is explicit.
- *Is this a pattern?* Yes — financial disclosure PDFs consistently have a minimum-requirement column before the actual bank ratio column. Document this in `learnings.md`.

---

## 2026-05-01 — W-0049, W-0033, W-0030, W-0024: ADR-0005, entity_type, new metrics series, disclosure pipeline run

**Items completed:**

### W-0049 — ADR-0005: PDF Disclosure Extraction Strategy

- `docs-adr/0005-pdf-extraction-approach.md`: Documents the extraction architecture (pdfplumber `extract_text()` + two-strategy regex approach). Captures the `first_value` and `second_pct` strategies, unit detection logic, known gaps (Rabobank image-based, Westpac WAF), four rejected alternatives (extract_tables, LLM, OCR, manual entry), and implementation notes including the TDD workflow for adding new metrics.
- `docs-adr/README.md`: ADR-0005 entry added to index.

### W-0033 — entity_type field in canonical schema

- `src/processing/parse.py`: Added `_GROUP_ENTITIES` frozenset classifying 7 group entities (ANZ Group, BOC Group, CBA Group, CCB Group, ICBC Group, Rabo Group, WBC Group). Every row now includes `entity_type: "standalone" | "group"`. CSV writer updated to include `entity_type` in field list.
- `docs/data/processed/metrics.json` + `data/processed/metrics.csv`: Regenerated with `entity_type` field.
- `docs/index.html`: "Standalone only" button now derives group entities from `entity_type` field in data rather than hardcoded name list.
- `docs-adr/0004-rbnz-data-contract.md`: Schema table and Decision section updated to document the new field.
- `tests/test_processing.py`: 4 new tests (TDD Red→Green): standalone entity type, group entity type, unknown defaults to standalone, all 7 known group entities classified correctly.

### W-0030 — Mismatch ratios + credit concentration series

- `config/metrics.yaml`: Added 5 confirmed RBNZ series: `DBB.QIH10` (1-Month Mismatch Ratio), `DBB.QIH20` (1-Week Mismatch Ratio), `DBB.QIJ10` (Top 5 Non-Bank Credit Exposures), `DBB.QIJ30` (Top 5 Bank Credit Exposures), `DBB.QIJ40` (Bank Exposures ≥10% of CET1).
- `docs/data/processed/metrics.json` + `data/processed/metrics.csv`: Regenerated — 13900 → 17375 rows (+3475 new rows for 5 series).
- `glossary.md`: 5 new metric definitions added with RBNZ series IDs and units.

### W-0024 — Disclosure extraction end-to-end

- `scripts/process_disclosures.py`: Fixed output path from `disclosures.json` (the existing PDF index file) to `disclosure_metrics.json` (distinct metrics file). Added `_log_extraction_summary()` to log extracted/null counts per bank per period.
- Script run against full corpus (ANZ ×3, ASB ×16, BNZ ×6, Kiwibank ×13, Rabobank ×3 = 41 PDFs).
- Outputs: `data/processed/disclosures.csv` and `docs/data/processed/disclosure_metrics.json`.

**Mini-retro:**

- *Did the process work?* Yes — TDD cycle caught the CSV header regression immediately (existing test for field list needed updating for the new `entity_type` field). Fixed in the same cycle before the commit.
- *What slowed things down?* The process_disclosures.py output path bug (writing to `disclosures.json` which overwrites the PDF index) was found only when reading the W-0024 backlog item carefully. The naming should have been caught when W-0015 was initially implemented.
- *Single change to prevent this next time?* When a script produces a new output file, check whether the path conflicts with existing files in the same directory before choosing the name. Add this as a code-review checklist item.
- *Is this a pattern?* Yes — naming ambiguity between index files and metrics files. Document in copilot-instructions.md: processed output files should use descriptive names (`_metrics`, `_index`) to avoid collision.

---

## 2026-05-01 (continued) — W-0074, W-0052, W-0053: extraction fix, RWA series, provisioning

**Items completed:**

### W-0074 — ASB "Advances to customers" regex fix

Root cause of ASB "Net Loans and Advances" gap: ASB uses "Advances to customers" as the balance sheet label, not "Loans and advances". TDD cycle:
- Red: 2 tests using `_BALANCE_METRICS` production patterns fail (result=None on ASB label line)
- Green: `r"advances to customers\b"` added to `_BALANCE_METRICS` patterns for "Net Loans and Advances"
- Full suite: 152 tests pass, 0 regressions
- ASB extraction: 125 → 140 rows; total disclosure rows: 344 → 359

### W-0052 — RWA series and derived charts

- `config/metrics.yaml`: `DBB.QIB90` (Total Risk-Weighted Assets) added
- `glossary.md`: Total Risk-Weighted Assets, RORWA, Risk Density definitions added
- `docs/index.html`: RORWA (PAT/RWA×100) and Risk Density (RWA/Loans×100) computed in `buildLookup()`; added to `KEY_METRICS` and `METRIC_LABELS`
- `metrics.json`/`metrics.csv`: 17375 → 19460 rows

### W-0053 — Provisioning series and Provisioning Coverage chart

- `config/metrics.yaml`: `DBB.QIC60` (Individual Provisions), `DBB.QIC70` (Collective Provisions) added
- `glossary.md`: Individual Provisions, Collective Provisions, Provisioning Coverage, Provision Charge definitions added
- `docs/index.html`: Provisioning Coverage ((IndProv+CollProv)/NPL×100) computed client-side and added to chart grid

**Mini-retro:**

- *Did the process work?* Yes — the ASB regex fix followed the TDD cycle correctly; the second Red test (using `_BALANCE_METRICS` directly from production code) was a genuine Red before the fix.
- *What slowed things down?* First TDD attempt for W-0074 used the fixed patterns in the test parameters, making the test pass immediately (not a true Red). Caught and corrected before proceeding.
- *Single change to prevent this next time?* When testing extraction patterns, import `_BALANCE_METRICS` (or the equivalent production constant) in the test rather than hardcoding patterns in the test parameter. This ensures the test exercises the production code paths and will be Red when the production pattern is wrong.
- *Is this a pattern?* Yes — when unit-testing configurable behaviour (like regex pattern lists), always import the production config into the test rather than duplicating it.

---

## 2026-05-01 (continued) — W-0031, W-0035, W-0036, W-0060: charts, events, freshness badge

**Items completed:**

### W-0031 — Loan-to-Deposit Ratio chart

- `docs/index.html`: LDR = (Net Loans / Deposits) × 100 computed in `buildLookup()`. Added to `KEY_METRICS` and `METRIC_LABELS`. Renders as a chart alongside existing metrics. No new data pipeline work — both series already in `metrics.json`.
- `glossary.md`: Loan-to-Deposit Ratio definition added.

### W-0035 — OCR rate-change vertical annotations

- `docs/index.html`: `verticalLinesPlugin` (custom Chart.js plugin, registered globally) draws dashed vertical lines via canvas `afterDraw`. Red = OCR hike, teal = OCR cut. Threshold: |delta| ≥ 0.25 (25 bps). `buildOcrEvents()` computes quarterly OCR deltas from already-loaded `ocr.json`. "OCR rate changes" checkbox toggle (off by default); preference persisted in `localStorage`.

### W-0036 — NZ/global events overlay

- `config/events.yaml`: 13 curated events (2019-Q4 through 2024-Q3) covering RBNZ capital reform, COVID, FLP, LVR cycles, OCR peaks, SVB/Credit Suisse, Kiwibank govt buyback. Category colour scheme: teal=monetary, amber=regulatory, grey=macro/market.
- `docs/index.html`: `NZ_EVENTS` and `EVENT_COLORS` inlined as JS constants for static-site delivery. "NZ events" checkbox toggle (off by default). Both OCR event and NZ event annotation layers merged and passed to `verticalLinesPlugin` per chart render cycle.

### W-0060 — Data freshness badge

- `docs/index.html`: Freshness badge below the status line shows "RBNZ data: YYYY-QN · Disclosures: YYYY-QN". RBNZ latest derived from `allPeriods.last`. Disclosure latest derived from loaded `disclosure_metrics.json`. Badge is teal-coloured; failure to load disclosures is non-fatal.

**Mini-retro:**

- *Did the process work?* Yes — all four items were purely client-side and did not require pipeline changes. The vertical annotation plugin approach (custom Chart.js plugin using `afterDraw`) is clean and avoids external dependencies.
- *What slowed things down?* The NZ events toggle required merging two annotation layers (OCR events + NZ events) before passing to the plugin. Initial implementation passed them separately, requiring a merge step.
- *Single change to prevent that next time?* Design the annotation layer API to accept a unified array from the start rather than retrofitting it.
- *Is this a pattern?* Yes — when adding multiple overlays that share the same rendering path, define the unified data contract first.

---

## 2026-05-01 — W-0042, W-0020, W-0041, W-0037, W-0043, W-0025–W-0029, W-0054: chart tabs, UX improvements, disclosure charts

**Items completed:**

### W-0042 — Tab categories

- `docs/index.html`: `TABS` const maps 4 tab categories to metric lists (profitability / capital / asset quality / liquidity). `KEY_METRICS` derived as the flat union. Tab bar (`.tab-bar` / `.tab-btn`) rendered above chart grid; active tab persists in `localStorage["activeTab"]`. `renderCharts` filters to `TABS[activeTab]` metrics only. `METRIC_LABELS` extended with 11 new entries covering all newly-visible series.

### W-0020 — Fullscreen charts

- `docs/index.html`: `⛶` button per chart card opens `#chart-modal-overlay` (fixed, full-viewport). `openFullscreen(idx)` clones chart config via `structuredClone`, re-attaches tooltip callback from `chartMeta`, creates a fresh `Chart` instance on `#modal-canvas`. `closeFullscreen()` destroys modal chart. Escape key and overlay background click both close.

### W-0041 — Chart PNG export

- `docs/index.html`: `↓` button per card (and in modal). `downloadChart(idx)` draws chart canvas onto an offscreen canvas with `#0d0d0d` fill, exports via `canvas.toDataURL('image/png')` → programmatic `<a download>` click. Slug derived from metric name.

### W-0037 — Sector average line

- `docs/index.html`: "Sector avg" checkbox added to filter bar. `getStandaloneEntities()` uses `entity_type === 'group'` detection with STANDALONE fallback. Sector avg dataset (dashed grey `#888`) added per chart when ≥2 standalone visible banks have data for a period. Nulls excluded from mean. Persists in `localStorage["showSectorAvg"]`.

### W-0043 — Snapshot table improvements

- `docs/index.html`: (1) Click-to-sort column headers — `sortState` updated on click, `▲`/`▼` CSS suffix added via `.sort-asc`/`.sort-desc` classes; (2) Best/worst cell colouring — `.cell-best` (teal) and `.cell-worst` (red) applied per column; (3) Period selector dropdown above table — `#snapshot-period-sel` populated from `allPeriods`, persists in `localStorage["snapshotPeriod"]`.

### W-0025–W-0029 — Disclosure charts

- `docs/disclosures.html`: Chart.js CDN added. New `#disc-charts-section` inserted before existing content. Six charts rendered from `disclosure_metrics.json`:
  - W-0025: Line charts for Profit After Tax, Operating Expenses (abs), Total Assets, CET1 Ratio — one line per bank, all periods
  - W-0026: Grouped bar chart (income statement) for latest full-period per bank: NII, Non-Interest Income, OpEx abs, PAT
  - W-0027: Operating Expenses over time (line chart, abs values)
  - W-0028: Capital ratios (CET1 + Total Capital Ratio as solid/dashed lines per bank)
  - W-0029: Loans & Deposits (Net Loans + Deposits as solid/dashed lines per bank; Rabobank null noted)

### W-0054 — Credit concentration display in Liquidity tab

- Already in `config/metrics.yaml` (added by W-0030). Now visible as the bottom three series in the Liquidity tab (W-0042). `METRIC_LABELS` extended for all three series. Glossary already had no entries for these three — added via the W-0030 progress note.

**Mini-retro:**

- *Did the process work?* Yes — all items were client-side only; no Python changes needed.
- *What slowed things down?* The fullscreen modal required `structuredClone` of the Chart.js config to avoid shared state; tooltip callbacks (functions) are not clonable and needed to be stored separately on `chartMeta` and reattached.
- *Single change to prevent next time?* When designing chart config storage, separate serialisable config from non-serialisable callbacks from the start.
- *Is this a pattern?* Yes — any time chart configs need to be duplicated (e.g. for export, fullscreen, or print), treat the callback functions as a separate layer attached after cloning.


### 2026-05-02 — File naming alignment, CHANGELOG, and copilot instructions improvements (W-0068, W-0089, W-0090)

**Completed:**

- **W-0089**: `backlog.md` → `BACKLOG.md`, `progress.md` → `PROGRESS.md` — aligns with `davidamitchell/Research` convention already specified in ADR-0002. All references updated (README.md, learnings.md, copilot-instructions.md, BACKLOG.md itself).
- **W-0068**: `CHANGELOG.md` created following Keep a Changelog 1.0.0. Historical entries backfilled for the initial scaffold, first processed data, disclosure pipeline, OCR overlay, and Phase 19 UI. Future schema changes must include a CHANGELOG entry as a hard gate.
- **W-0090**: `.github/copilot-instructions.md` comprehensively updated following a review of `davidamitchell/Latest-developments-/.github/copilot-instructions.md`:
  - Skills section moved to the top of the file
  - Explicit Skill Chains table added
  - `BACKLOG.md`, `PROGRESS.md`, `learnings.md`, `CHANGELOG.md`, and ADR mandates added as standalone sections
  - Slice Completion Checklist added (hard gates: make check, make test, PROGRESS.md, CHANGELOG.md if schema change, ADR if warranted, glossary if new metric)
  - `decisions` skill added to the skills table (maps to `adr`)
  - "Root Cause Before Action" section added
  - Previous "Continuous Improvement" and "Systemic Improvement Principles" sections consolidated
  - All `backlog.md`/`progress.md` lowercase references updated to uppercase

**Mini-retro:**
- Root cause of the file naming non-conformance: ADR-0002 specified the standard but the initial scaffold implementation was never checked against it. Fix: Slice Completion Checklist now includes an ADR compliance gate, and the file naming standard is explicitly enforced by the instructions.
- Root cause of the missing CHANGELOG: W-0068 was in the backlog but not yet executed. The new copilot instructions make CHANGELOG maintenance a hard gate for every schema-changing item.
- Root cause of the instructions gap: the reference repo (`Latest-developments-`) had evolved since this repo was scaffolded and the divergence was not tracked. Fix: ADR mandate now includes a rule to review the reference repo when making instruction changes.

## 2026-05-02 — Backlog execution: W-0032, W-0040, W-0047, W-0055–W-0063, W-0070–W-0071, W-0021

**What changed:**

- **W-0061**: Added monthly schedule trigger (`0 6 1 * *`) to `fetch-data.yml` alongside `workflow_dispatch`. Updated comment to reflect both triggers.
- **W-0070**: Added YAML front matter (`title`, `status`, `date`, `authors`, `tags`, `supersedes`, `superseded_by`) to ADR-0001 through ADR-0004. Added coded consequence bullet IDs (POS-001, NEG-001, NEU-001) to all four ADRs.
- **W-0071**: Added `## Code Review Standard` section to `.github/copilot-instructions.md` with six-point checklist: correctness, data accuracy, test coverage, security, idempotency, ADR compliance.
- **W-0032**: Created `config/capital_requirements.yaml` with the RBNZ 2019 capital reform phase-in schedule (2023–2028, D-SIB and non-D-SIB). Added Capital Headroom derived metric to `buildLookup()` in `docs/index.html`, using the phase-in schedule and D-SIB surcharges (ANZ/Westpac +1.5%, ASB/BNZ +1.0%). Added to capital tab, METRIC_LABELS, and METRIC_INFO.
- **W-0055**: Added Pre-Provision Profit (PPP = NII + Trading + Fees + Other − Opex) to `buildLookup()`. Added to profitability tab, METRIC_LABELS, METRIC_INFO.
- **W-0056**: Added Non-Interest Income Share (%) to `buildLookup()`. Added to profitability tab, METRIC_LABELS, METRIC_INFO.
- **W-0057**: Added `buildProvisioningMetrics()` function for Credit Impairment Rate (ΔNPL ÷ Net Loans × 100). Called from `render()`. Added to asset quality tab, METRIC_LABELS, METRIC_INFO.
- **W-0058**: Added Opex Intensity (bps) to `buildLookup()` (quarterly opex × 4 ÷ total assets × 10000). Added to profitability tab, METRIC_LABELS, METRIC_INFO.
- **W-0062**: Added `syncUrlHash()` and `loadFromHash()` for hash-based URL state encoding (banks, range, tab, mode). Added "📋 Copy link" button with Copied! feedback.
- **W-0063**: Added `downloadCsv()` function and "↓ CSV" button. Exports filtered data in canonical schema format.
- **W-0040**: Added Indexed (base=100) chart mode toggle. Rebases all non-OCR datasets to 100 at first non-null value. Stored in `localStorage["chartMode"]`. Shows informational note when active.
- **W-0047**: Added auto-narrative panel (`#narrative-section`) between KPI row and charts. Generates 4–5 plain-English bullets: NIM trend, ROE leader, CET1 direction, C/I trend, NPL trend. Collapsible with localStorage state.
- **W-0021**: Created `docs/methodology.html` (KPI formulas, RBNZ series table, derived metrics, capital reform schedule, data currency) and `docs/lineage.html` (data model, pipeline stages, source files, disclosure pipeline). Added Methodology and Lineage nav/footer links to all existing pages.

**Tests:** 192 passed (no regressions).

**Mini-retro:**
- Batch execution of 13 items in one session was feasible because all items were well-specified with concrete formulas and clear scope. The main risk was JS syntax consistency in the large index.html file — mitigated by using a sub-agent with full context.
- Root cause of complexity: index.html is a monolithic file. Future work should assess whether splitting into modules would reduce the cognitive load per change.

## 2026-05-02 — Batch 2: W-0045, W-0046, W-0048, W-0051, W-0059

Five items implemented in a single session.

- **W-0045**: Added "Band (min/max)" checkbox to Overlays fieldset. When enabled with ≥2 standalone banks visible, renders a semi-transparent teal shaded band (`#00C3A508` fill) between the min and max values across standalone banks for each period. Uses two hidden `_band_min`/`_band_max` datasets with a `fill: '-1'` Chart.js band fill. Legend entries starting with `_band_` are filtered from display.
- **W-0046**: Added `#ranking-section` below the snapshot table. `renderRankingTable()` shows rows = banks, columns = KEY_METRICS with data in the selected period. Rank view colours top quartile teal (`.rank-best`) and bottom quartile red (`.rank-worst`). A "Value view" / "Rank view" toggle button persists state in `localStorage["rankingViewMode"]`. `HIGHER_IS_BETTER` set drives ranking direction for 12 metrics; lower-is-better for the remaining 11.
- **W-0048**: Added "Trend flags" checkbox to Overlays fieldset. When enabled, appends ` ▲` / ` ▼` / ` →` to each bank's chart legend label based on the trailing slope of the last 4 data points. Stable threshold: `|slope| < 0.05 × stdDev` (or 0.1 if stdDev = 0). Direction is interpreted via `HIGHER_IS_BETTER`. `trailingSlope()` helper added.
- **W-0051**: Replaced the terse `#capital-reform` section in `docs/methodology.html` with a richer version: narrative introduction, restructured CET1 requirements table (Period / Non-D-SIB / D-SIB base / surcharges), conservation buffer explanation, and Capital Headroom linkage.
- **W-0059**: Added `--batch` flag to `scripts/download_disclosures.py` (existing batch behaviour is now explicitly invoked via this flag). Created `.github/workflows/download-disclosures.yml` with `workflow_dispatch` inputs for `bank` and `force`. Added 6 tests for the `--batch` flag covering: acceptance, all-banks processing, bank filter, force pass-through, partial failure exit code, and non-abort behaviour on single failure.

**Tests:** 198 passed (no regressions). Lint clean.

## 2026-05-02 — Batch 3: W-0044, W-0050, W-0064, W-0065

### W-0044 — NIM Pass-Through Analysis Panel
Added `quarterOffset()`, `linearRegression()`, and `renderNimPassThrough()` to `docs/index.html`. The scatter chart (OCR change vs NIM change 2Q later, per bank) appends to the profitability tab chart grid when OCR data is loaded. Shows per-bank trend lines via linear regression. Falls back to a placeholder card when OCR data is absent.

### W-0050 — Coverage Page
Created `docs/coverage.html` with two sections: (1) RBNZ quarterly coverage table — rows = RBNZ-stored KEY_METRICS, columns = Top 6 banks, cells = present/total periods colour-coded teal/amber/red; (2) Disclosure coverage table — rows = banks, columns = key disclosure metrics, shows ✓/— with WAF and image-based notes. Coverage nav link added to all existing pages (index, glossary, disclosures, methodology, lineage, data-sources).

### W-0064 — Snapshot Page
Created `docs/snapshot.html` — 3-column bar-chart grid (one chart per KEY_METRIC, all standalone banks side-by-side) with a quarter selector dropdown. Duplicates the derived-metrics logic from index.html for client-side computation. "Full snapshot →" link added to snapshot section title in `docs/index.html`.

### W-0065 — Anomaly Flags
Added `computeAnomalies()` which computes trailing 8Q mean and stddev per bank/metric and flags values > 2σ. Anomaly ⚠ icons (amber, with tooltip showing σ distance and trailing average) applied to snapshot table and ranking table value view. CSS `.anomaly-flag` added.
