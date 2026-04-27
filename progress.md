# Progress

> Session logs and completion notes.
Last updated: 2026-04-27 (initial scaffold — W-0001 through W-0012)

---

## Current Status

**Phase:** Phase 1 — Standardisation and Governance
**Active work:** Phase 1.5 setup (metrics mapping, ADR for data contract)
**Next phase:** Phase 2 — Automated Data Pipeline

---

| Phase | Title | Status |
|---|---|---|
| 1 | Standardisation and Governance | In progress |
| 1.5 | Data Modelling and Source Definition | In progress |
| 2 | Automated Data Pipeline | Not started |
| 2.5 | Discovery / Research Spikes | Not started |
| 3 | Visualisation and Deployment | Scaffold done |
| 4 | Qualitative Data Extraction | Deferred |

---

## Work Log

### 2026-04-27 — Initial scaffold (setup-project-as-research-structure)

**Completed:**

- Repository structure initialised following `davidamitchell/Research` conventions
- `.github/skills/` submodule added pointing to `davidamitchell/Skills`
- `.github/copilot-instructions.md` created with language constraints and operational rules
- `backlog.md` populated with all phases and work items
- `progress.md` initialised (this file)
- `learnings.md` initialised with structure
- `glossary.md` created with all KPI categories and definitions
- `docs/adr/README.md` created with index and template
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

**Open:**

- W-0006: Populate `config/metrics.yaml` (depends on spike S-0001)
- W-0008: ADR for canonical data structure assumptions (depends on spike S-0001)
- W-0010: Process data workflow
- W-0011: First live fetch run
- W-0013: Configure GitHub Pages in repo settings
- W-0014: Frontend with real data
- S-0001, S-0002, S-0003: Discovery spikes
