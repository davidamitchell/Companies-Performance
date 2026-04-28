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

status: open
created: 2026-04-27
updated: 2026-04-27

### Outcome

`config/metrics.yaml` is populated with initial field mappings from RBNZ XLSX columns to canonical glossary terms.

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

status: open
created: 2026-04-27
updated: 2026-04-27

### Outcome

An ADR documents the canonical data structure assumptions (`entity | metric | value | period | source`) and any deviations required by the RBNZ data shape.

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

status: open
created: 2026-04-27
updated: 2026-04-27

### Outcome

`.github/workflows/process-data.yml` exists; running it parses the RBNZ XLSX, normalises rows into the canonical schema, validates data quality (range checks, missing values, duplicate detection), and writes `data/processed/metrics.csv` and `data/processed/metrics.json`.

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

status: open
created: 2026-04-27
updated: 2026-04-27

### Outcome

Investigate the RBNZ XLSX structure: sheet names, column headers, data types, entity names, and period format. Record findings in `learnings.md`. Update `config/metrics.yaml` with initial mappings. Open backlog items for any gaps.

### Context

Must result in: backlog update, or ADR, or explicit no-action decision.

---

### S-0002

status: open
created: 2026-04-27
updated: 2026-04-27

### Outcome

Investigate feasibility of additional bank disclosure sources (e.g. annual report PDFs). Record findings in `learnings.md`. Open backlog items for any viable sources.

### Context

Must result in: backlog update, or ADR, or explicit no-action decision.

---

### S-0003

status: open
created: 2026-04-27
updated: 2026-04-27

### Outcome

Investigate metric inconsistencies across banks in the RBNZ data (different reporting periods, different metric coverage). Record findings in `learnings.md`.

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

status: open
created: 2026-04-27
updated: 2026-04-27

### Outcome

Frontend displays real data from the first successful pipeline run. Charts or trend indicators added for key metrics (CET1, LCR, NIM).

### Context

Depends on W-0010 and W-0013.

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
