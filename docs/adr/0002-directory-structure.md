# ADR-0002: Directory Structure Aligned to Research Repo

Date: 2026-04-27
Status: Accepted

## Context

The Companies Performance repository must follow the structural, operational, and workflow conventions established in `davidamitchell/Research`. Deviations from those conventions must be documented.

The Research repo uses:
- `docs-adr/` for Architecture Decision Records
- `docs/` for GitHub Pages output (generated)
- `config/` for YAML configuration
- `src/` for Python source
- `tests/` for pytest tests
- `progress/` (subdirectory) and `PROGRESS.md` at root
- `BACKLOG.md` at root
- `learnings.md` at root

This repository has different concerns (financial data pipeline vs. research tooling) and a different GitHub Pages strategy.

## Decision

Adopt the Research repo structure with the following deliberate deviations:

| Path | Research repo | This repo | Reason |
|---|---|---|---|
| ADRs | `docs-adr/` | `docs/adr/` | ADRs are part of the published docs site |
| Data | (none) | `data/raw/`, `data/processed/` | Financial pipeline requires explicit data storage |
| GitHub Pages | `docs/` (generated output) | `docs/` (static + ADRs) | Simpler deployment; no separate build step needed initially |

All other conventions (config, src, tests, backlog, progress, learnings, skills submodule, CI via GitHub Actions) are adopted without deviation.

## Consequences

### Positive
- Alignment with Research repo reduces cognitive overhead for contributors familiar with that project
- Single `docs/` directory simplifies GitHub Pages configuration (no separate build workflow for initial phase)
- ADRs are browsable on the deployed site

### Negative / Trade-offs
- `docs/adr/` mixing with static HTML requires careful path management
- If the site grows to require a build step (e.g. Jinja templates), the `docs/` convention may need revisiting (document via new ADR)

### Neutral
- The `data/` directory uses `.gitkeep` for the raw subdirectory; raw XLSX files are excluded via `.gitignore`
