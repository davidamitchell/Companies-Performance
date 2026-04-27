# Copilot Instructions — Companies Performance

## Purpose

This repository tracks the financial performance of companies using structured data pipelines and static visualisation. The primary data source is the RBNZ Bank Financial Strength Dashboard XLSX.

---

## Language Constraints

| Layer | Language |
|---|---|
| Data ingestion and processing | Python 3.11+ |
| Frontend / visualisation | HTML, CSS, JavaScript (static only — no build step) |
| Configuration | YAML |
| Data persistence | CSV (tabular), JSON (indexes and frontend consumption) |

Do not introduce additional languages or runtimes without a supporting ADR.

---

## Financial Accuracy

- All metric values must be sourced directly from official data files with no manual editing.
- Metric names must match the canonical definitions in `glossary.md` exactly. Do not introduce synonyms or abbreviations.
- Numeric values must be stored as-is from the source; do not round, normalise, or impute.
- If a value is missing or ambiguous in the source, store `null` / empty and log a `WARNING`.

---

## Operational Rules

### Idempotency (required)
All workflows must be idempotent. Re-running a workflow must produce the same result and must not duplicate or corrupt data. Implement idempotency by:
- Overwriting output files at fixed paths (not appending)
- Using `git diff --cached --quiet` guards before committing

### Logging (required)
Use structured logging at three levels, visible in GitHub Actions logs:
- `INFO` — normal progress (file downloaded, rows processed, commit created)
- `WARNING` — non-fatal anomalies (missing value, skipped row, unexpected column name)
- `ERROR` — fatal failures that abort the pipeline (HTTP error, parse failure, schema violation)

Use `src.logger.get_logger(__name__)` in every module. Do not use `print()` for operational output.

### Separation of Concerns
Code is organised into three distinct layers:
1. **Ingestion** (`src/ingestion/`) — fetch raw files from sources; no transformation
2. **Processing** (`src/processing/`) — parse, normalise, validate; no I/O to external services
3. **Presentation** (`docs/`) — static HTML/CSS/JS only; consumes repo-stored JSON

Do not mix responsibilities across layers.

---

## Glossary Adherence

Every metric name used in code, config, or data files must appear verbatim in `glossary.md`. If a new metric is introduced, add it to the glossary first. If a source file uses a different name, map it via `config/metrics.yaml`.

---

## Development Workflow

1. New significant decisions → write an ADR in `docs-adr/` before implementing.
2. New data sources → add via discovery spike, record in `learnings.md`, update `backlog.md`.
3. All compute runs via GitHub Actions (manual trigger initially).
4. Tests live in `tests/`; run with `make test` or `pytest tests/`.
5. Do not commit generated data files (`data/raw/*.xlsx`) — these are in `.gitignore`.
6. Processed data files (`data/processed/`) are committed by the pipeline workflow.

---

## Reference Repository

This repo follows conventions established in `davidamitchell/Research`. Deviations are documented in `docs-adr/0002-directory-structure.md`.

---

## Continuous Improvement

After completing each piece of work, conduct a short retrospective focused on **the system that produced the work** — not the application itself.

Ask:
- What friction slowed this work down? (missing decisions, unclear conventions, incomplete scaffolding)
- Was any assumption made without evidence? If so, open a spike or ADR to resolve it.
- Did any step require backtracking because a decision was made too early?
- Is there a workflow, template, or convention that would prevent the same friction next time?

Record actionable findings as backlog items (`backlog.md`) or ADRs (`docs-adr/`). Discard observations that produced no action. Do not improve things that aren't broken.

This is not a review of the application's correctness — it is a review of the process that built it.
