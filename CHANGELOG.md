# Changelog

All notable changes to the data schema, pipeline behaviour, and user-facing features are documented here.

Follows [Keep a Changelog 1.0.0](https://keepachangelog.com/en/1.0.0/).  
New entries go under `## [Unreleased]` at the top. On release, move them to a dated section.

---

## [Unreleased]

### Added
- **W-0091**: `config/metrics.yaml` extended with `controllability` section classifying every canonical metric as High / Medium / Low / Hybrid. `config/metric_groups.yaml` (new file) defines three metric groups: Management Controllable, Market-Driven, Productivity-Focused. `glossary.md` updated with controllability level definitions.
- **W-0092**: "Group" dropdown added to sticky controls bar in `docs/index.html`. Options: All Metrics, Management Controllable, Market-Driven, Productivity-Focused. Persisted to `localStorage["metricGroup"]`.
- **W-0093**: Collapsible "Golden Metrics" sparkline panel added to `docs/index.html`. Renders 8-quarter sparklines for CET1, ROE, CTI, NIM, NPL Ratio, and CFR.
- **W-0094**: "Correlations" tab added to `docs/index.html`. Renders a Pearson correlation heatmap across selected banks and periods. Highly-correlated pairs (|r| > 0.85) listed below the matrix.
- **W-0095**: Collapsible "Market Context" section added to `docs/index.html`. User-selected metric vs OCR overlay (OCR on right Y-axis). Accessible from Analysis ▾ nav dropdown.
- **W-0096**: `config/strategy_pillars.yaml` (new file) defines five strategy pillars: Customer, Efficiency, Resilience, Innovation, Returns. "Strategy Scorecard" tab added to `docs/index.html`. Per-bank comparison mode: when multiple banks are selected, each metric shows one row per bank with individual value, QoQ trend arrow, and colour-coded proportional bar — no averaging across organisations. Single-bank mode shows peer-percentile bar relative to all banks in the dataset. Design decision documented in ADR-0007.
- **W-0097**: Export CSV and Print buttons added to Strategy Scorecard tab. CSV: `strategy-scorecard-{period}.csv` with bank|pillar|metric|latest_value|prior_value|trend|leading_or_lagging (per-bank rows). Print: `window.print()` with a print stylesheet that hides nav/controls/tabs.
- **W-0098**: "Dimensionality Reduction" tab added to `docs/index.html`. Vanilla-JS power-iteration PCA with scree plot and 2D PC1 vs PC2 projection. Respects metric group filter.
- **W-0099**: Chart tooltips in `docs/index.html` extended with controllability and pillar context. `docs/glossary.html` gains controllability (colour-coded) and pillar badges on each metric term via a JS injection.
- **W-0100**: "Analysis ▾" `<details>/<summary>` dropdown added to site nav on `docs/index.html`. Links to Correlations, Dimensionality Reduction, Strategy Scorecard, and Market Context.
- ADR-0007: Strategy Scorecard — Per-Bank Comparison over Sector Average.

### Changed
- `backlog.md` renamed to `BACKLOG.md` and `progress.md` renamed to `PROGRESS.md` to align with `davidamitchell/Research` conventions (ADR-0002).

### Added
- `CHANGELOG.md` created (this file) — W-0068.
- `strategy-author` skill added to `.github/copilot-instructions.md`; systemic improvement principles and root-cause mandate documented.
- Skills git submodule (`.github/skills`) initialised to `davidamitchell/Skills` at commit `f8c5471`.
- ADR-0006: Agent Instructions Format and Governance Standards — documents the decision to adopt the `Latest-developments-` instruction format, add CHANGELOG/PROGRESS/ADR mandates, and introduce the Slice Completion Checklist.
- **W-0032**: `Capital Headroom` derived metric added to `docs/index.html` and capital tab. Computed as CET1 Ratio minus applicable RBNZ minimum (RBNZ 2019 capital reform phase-in 2023–2028, D-SIB surcharges for ANZ/Westpac +1.5%, ASB/BNZ +1.0%). Config in `config/capital_requirements.yaml`.
- **W-0055**: `Pre-Provision Profit` (NZDm) derived metric added to profitability tab. Formula: NII + Trading + Fees + Other Income − Operating Expenses.
- **W-0056**: `Non-Interest Income Share` (%) derived metric added to profitability tab. Formula: Non-interest income ÷ total operating income × 100.
- **W-0057**: `Credit Impairment Rate` (% loans) derived metric added to asset quality tab. Formula: ΔNPL ÷ Net Loans × 100 (quarter-over-quarter).
- **W-0058**: `Opex Intensity` (bps) derived metric added to profitability tab. Formula: (Operating Expenses × 4) ÷ Total Assets × 10,000.
- **W-0021**: `docs/methodology.html` and `docs/lineage.html` transparency pages created. Navigation links added to all existing pages.
- **W-0061**: Monthly schedule trigger (`0 6 1 * *`) added to `fetch-data.yml`.
- **W-0062**: Hash-based URL state sharing in `docs/index.html`; "Copy link" button.
- **W-0063**: CSV download of filtered data in canonical schema format.
- **W-0040**: Indexed (base=100) chart mode toggle in `docs/index.html`.
- **W-0047**: Auto-narrative panel with plain-English sector bullets in `docs/index.html`.
- **S-0012/S-0013**: Reference data files added: `data/reference/employees.csv` (annual FTE per bank, sourced from KPMG FIPS and bank annual reports) and `data/reference/customers.csv` (active retail customer estimates). Schema documented in `config/reference.yaml`.
- **W-0075**: `data/reference/` directory created with `employees.csv`, `customers.csv`, and `config/reference.yaml`.
- **W-0076**: `src/processing/compute_productivity.py` and `scripts/compute_productivity.py` added. Computes six productivity metrics: Profit per Employee, Gross Income per Employee, Expenses per Employee, Profit per Customer, Gross Income per Customer, Expenses per Customer. Output: `data/processed/productivity.csv` and `docs/data/processed/productivity.json`. Confidence field propagated from reference data. Tests in `tests/test_compute_productivity.py` (20 tests).
- **W-0077**: `.github/workflows/compute-productivity.yml` added. Runs after Process Data workflow and commits productivity output files idempotently.
- **W-0078**: `Productivity` tab added to `docs/index.html` with six line charts (3 per-employee, 3 per-customer). NZD values formatted with `Intl.NumberFormat`. Confidence badges (🔵 Exact / 🟡 Triangulated / 🔴 Estimated) shown in chart tooltips. Graceful degradation if `productivity.json` is absent.

---

## [2026-05-01] — Phase 19 UI layout; disclosure pipeline; metrics expansion; Phase 8 governance

### Added
- **Phase 19 UI layout (W-0079–W-0088)**: sticky control bar; KPI row; labelled fieldsets; landmark regions + skip link; consistent nav with Dashboard home link; disclosures page reorder; page subtitles and table captions; mobile table scroll + sticky bank column; standardised footer; `localStorage` persistence for bank selection.
- **W-0049**: `docs-adr/0005-pdf-extraction-approach.md` — documents hybrid `extract_tables()` / `extract_text()` strategy, extraction patterns, unit normalisation rules, and known data gaps.
- **W-0025–W-0029**: Disclosure charts on `docs/disclosures.html` — profit waterfall, opex trend, capital components, and funding structure charts from `disclosure_metrics.json`.
- **W-0033**: `entity_type` field (`standalone` / `group`) added to `metrics.csv` and `metrics.json`; "Standalone only" quick-select on bank selector.
- **W-0041**: Chart PNG export button (↓) on every chart card.
- **W-0042**: Chart grid reorganised into four tab categories (Profitability / Capital / Asset Quality / Liquidity).
- **W-0043**: Snapshot table sortable by column; best/worst colour coding; period selector.
- **W-0060**: Data freshness badge showing the most recent quarter in `metrics.json`.

### Changed
- **W-0052**: `config/metrics.yaml` extended with `DBB.QIB90` (Total Risk-Weighted Assets). `metrics.json` regenerated.
- **W-0053**: `config/metrics.yaml` extended with `DBB.QIC60` (Individual Provisions) and `DBB.QIC70` (Collective Provisions). `metrics.json` regenerated.
- **W-0054**: `config/metrics.yaml` extended with credit concentration series `DBB.QIJ10`, `DBB.QIJ30`, `DBB.QIJ40`. `metrics.json` regenerated.

---

## [2026-04-30] — Disclosure pipeline; OCR overlay; frontend enhancements

### Added
- **W-0015**: `src/processing/extract_disclosures.py` — extracts 10 quantitative metrics from bank disclosure PDFs. Outputs `disclosures.csv` and `disclosure_metrics.json`.
- **W-0024**: End-to-end disclosure extraction across full PDF corpus (ANZ ×3, ASB ×15, BNZ ×7, Kiwibank ×14, Rabobank ×4). Null gaps for Rabobank balance sheet (image-based page) logged as `WARNING`.
- **W-0019**: OCR overlay on NIM chart — `src/processing/parse_ocr.py`, `scripts/process_ocr.py`, `docs/data/processed/ocr.json`.
- **W-0020**: Fullscreen chart modal (⛶ button on every chart card).
- **W-0030**: `config/metrics.yaml` extended with `DBB.QIH10` (1-month mismatch ratio) and `DBB.QIH20` (1-week mismatch ratio). `metrics.json` regenerated.
- **W-0031**: Loan-to-Deposit Ratio derived client-side; added to Capital tab and Snapshot table.

---

## [2026-04-28] — First processed data; frontend with real data

### Added
- **W-0010**: Full processing pipeline — `src/processing/parse.py`, `scripts/process_data.py`, `.github/workflows/process-data.yml`. Outputs `data/processed/metrics.csv` and `docs/data/processed/metrics.json` (11,815 rows, 20 metrics, 22 institutions, 2018-Q1–2025-Q4).
- **W-0017**: Default KPI metrics updated (Cost-to-Income, ROE, ROA, NIM). Top 6 standalone banks as default. Three new RBNZ income series mapped: `DBB.QIE50`, `DBB.QIE55`, `DBB.QIE57`.
- **W-0018**: Historical time-series line charts (Chart.js 4.x) for all key metrics.
- **W-0023**: Dark design system applied — `docs/css/theme.css`, IBM Plex Mono, `#0d0d0d` background, `#00C3A5` teal.

### Changed
- `config/metrics.yaml` populated with 20 RBNZ series ID → canonical metric mappings (W-0006).

---

## [2026-04-27] — Initial scaffold

### Added
- Repository scaffold: `BACKLOG.md`, `PROGRESS.md`, `learnings.md`, `glossary.md`, `.github/copilot-instructions.md`, `docs-adr/`, `config/`, `src/`, `tests/`.
- ADR-0001: Data format decision (CSV persistence, JSON frontend delivery).
- ADR-0002: Directory structure aligned to `davidamitchell/Research`.
- `.github/skills/` submodule pointing to `davidamitchell/Skills`.
- CI, fetch-data, and deploy-pages GitHub Actions workflows.
- `docs/index.html` — static frontend skeleton.
