# Companies Performance

Financial performance tracking for companies — automated data pipeline and static visualisation.

## Overview

This repository ingests financial data (initially from the [RBNZ Bank Financial Strength Dashboard](https://bankdashboard.rbnz.govt.nz/)) and displays key metrics via a static GitHub Pages site.

## Structure

```
├── .github/
│   ├── copilot-instructions.md   # Agent and developer instructions
│   ├── skills/                   # Submodule: davidamitchell/Skills
│   └── workflows/                # GitHub Actions (CI, fetch-data, deploy-pages)
├── backlog.md                    # Work items and discovery spikes
├── config/
│   ├── sources.yaml              # Data source registry
│   └── metrics.yaml              # Raw field → canonical metric mappings
├── data/
│   ├── raw/                      # Downloaded source files (not committed)
│   └── processed/                # Normalised CSV/JSON (committed by pipeline)
├── docs-adr/                     # Architecture Decision Records
├── docs/
│   └── index.html                # Static frontend (GitHub Pages)
├── glossary.md                   # Canonical KPI definitions
├── learnings.md                  # Discovery spike outputs
├── progress.md                   # Work log
└── src/
    ├── config.py                 # Config loader
    ├── logger.py                 # Structured logging
    └── ingestion/                # Data fetching
```

## Getting started

```bash
pip install -e ".[dev]"
make test
```

## Workflows

| Workflow | Trigger | Purpose |
|---|---|---|
| CI | Push / PR | Lint and test |
| Fetch Data | Manual | Download RBNZ XLSX to `data/raw/` |
| Deploy Pages | Manual / push to main | Deploy `docs/` to GitHub Pages |

## Reference

Follows conventions established in [davidamitchell/Research](https://github.com/davidamitchell/Research).
Deviations documented in [docs-adr/0002-directory-structure.md](docs-adr/0002-directory-structure.md).
