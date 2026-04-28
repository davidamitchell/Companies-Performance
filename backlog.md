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

status: open
created: 2026-04-28
updated: 2026-04-28

### Outcome

The automated fetch workflow (`.github/workflows/fetch-data.yml`) runs end-to-end successfully against the live RBNZ URL; the downloaded XLSX is committed to `data/raw/` without manual intervention.

### Context

The initial RBNZ XLSX was loaded manually to unblock the pipeline (ADR-0003). This item validates and activates the automated fetch so that future data refreshes do not require manual steps. Requires network access from the Actions runner. Supersedes the manual load approach.

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

## Phase 4: Qualitative Data Extraction (Deferred)

### W-0015

status: deferred
created: 2026-04-27
updated: 2026-04-27

### Outcome

Define a prompt for agent-based qualitative extraction from bank disclosures. Define output schema. Implement as a separate pipeline workflow.

### Context

Deferred pending completion of Phase 3 and findings from spike S-0002.

---
