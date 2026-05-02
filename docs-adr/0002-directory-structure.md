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
- `PROGRESS.md` at root
- `BACKLOG.md` at root
- `learnings.md` at root

This repository has different concerns (financial data pipeline vs. research tooling) and requires explicit data storage paths.

## Decision

Adopt the Research repo structure. The only deliberate deviation is the addition of the `data/` directory, which has no equivalent in the Research repo:

| Path | Research repo | This repo | Reason |
|---|---|---|---|
| ADRs | `docs-adr/` | `docs-adr/` | Aligned — not a deviation |
| Data | (none) | `data/raw/`, `data/processed/` | Financial pipeline requires explicit data storage |
| GitHub Pages | `docs/` (generated output) | `docs/` (static HTML) | Simpler deployment; no separate build step initially |

All other conventions (config, src, tests, backlog, progress, learnings, skills submodule, CI via GitHub Actions) are adopted without deviation.

## Amendment (2026-05-02)

`backlog.md` and `progress.md` were initially created with lowercase names despite this ADR specifying `BACKLOG.md` and `PROGRESS.md`. Corrected in W-0089 — files renamed to match the standard. All references updated.

## Consequences

### Positive
- Full alignment with Research repo reduces cognitive overhead for contributors
- `docs/` is kept clean for GitHub Pages content only — no mixed concerns with ADRs
- `docs-adr/` is consistent with the reference repo and familiar to contributors

### Negative / Trade-offs
- ADRs are not published on the GitHub Pages site; they live in the repo only
- If ADRs need to be published in future, a build step or symlink strategy would be required (document via new ADR)

### Neutral
- The `data/` directory uses `.gitkeep` for the raw subdirectory; raw XLSX files are excluded via `.gitignore`
