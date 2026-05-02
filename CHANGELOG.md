# Changelog

All notable changes to the data schema, pipeline behaviour, and user-facing features are documented here.

Follows [Keep a Changelog 1.0.0](https://keepachangelog.com/en/1.0.0/).  
New entries go under `## [Unreleased]` at the top. On release, move them to a dated section.

---

## [Unreleased]

### Changed
- `backlog.md` renamed to `BACKLOG.md` and `progress.md` renamed to `PROGRESS.md` to align with `davidamitchell/Research` conventions (ADR-0002).

### Added
- `CHANGELOG.md` created (this file) — W-0068.
- `strategy-author` skill added to `.github/copilot-instructions.md`; systemic improvement principles and root-cause mandate documented.
- Skills git submodule (`.github/skills`) initialised to `davidamitchell/Skills` at commit `f8c5471`.
- ADR-0006: Agent Instructions Format and Governance Standards — documents the decision to adopt the `Latest-developments-` instruction format, add CHANGELOG/PROGRESS/ADR mandates, and introduce the Slice Completion Checklist.

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
