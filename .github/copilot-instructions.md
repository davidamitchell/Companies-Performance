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

## GitHub Actions Conventions

- **Never inline Python or shell scripts** in a workflow `run:` block beyond a single-line command.
  Move any multi-line logic to a dedicated script under `scripts/` and invoke it with `python scripts/<name>.py`.
- Every script under `scripts/` must have corresponding tests in `tests/`.
- Workflow steps must invoke existing `src` modules and `scripts/`; they must not duplicate or shadow that logic inline.

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
7. When a script produces output files in `docs/data/processed/`, verify the output path does not overwrite an existing file that serves a different purpose.

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
- What **class** of problem did this item represent? Has the root cause been addressed so the same class cannot recur?

Record actionable findings as backlog items (`backlog.md`) or ADRs (`docs-adr/`). Discard observations that produced no action. Do not improve things that aren't broken.

This is not a review of the application's correctness — it is a review of the process that built it.

**Retrospective outputs must address root causes, not symptoms.** If a finding is a symptom (e.g. "a field was missing"), trace it to its root cause (e.g. "the schema contract was not documented") and add a backlog item that eliminates the root cause. Point fixes to recurring problems are not acceptable — the fix must make the class of problem structurally impossible or explicitly governed.

---

## Output File Naming

Processed output files in `docs/data/processed/` must use descriptive suffixes to avoid naming collisions:
- `_metrics.json` — canonical rows in the `entity | metric | value | period | source` schema
- `_index.json` — lookup or reference lists (e.g. the list of available PDFs with their metadata)

Do not use bare names like `disclosures.json` when both a metrics file and an index file exist for the same source. Use `disclosure_metrics.json` and `disclosures.json` (or similar) to make the purpose unambiguous. When creating a new output file, check whether the chosen path already exists and serves a different purpose.

---

## Systemic Improvement Principles

**Fix root causes and classes of problems — not point solutions.**

When a bug, friction, or gap is found, ask: *what class of problem is this?* If it is symptomatic of a structural or process gap, the fix must address the root cause, not just the symptom. Apply this at all layers: data pipeline, processing logic, frontend, infrastructure, conventions, and this instruction set itself.

Applying this principle in practice:
- When a convention is violated, update the convention so it cannot be violated again — do not just fix the one instance.
- When a workflow step fails, ask whether the workflow design prevents this failure class. If not, propose a structural fix in the backlog.
- When a retrospective identifies friction, add a backlog item that eliminates the **type** of friction, not just the specific instance.
- When a decision is made under uncertainty, open a research spike immediately rather than deferring indefinitely.
- Use `strategy-author` when the root cause is a missing strategic direction or incoherent guiding policy — not every problem needs code; some need a decision.

---

## Available Skills

Skills are stored as sub-agent definitions in `.github/skills/`. Use the appropriate skill for each type of work:

| Skill | When to use |
|---|---|
| `backlog-worker` | Working the backlog autonomously — selects the next `ready` item, decomposes it, executes, reviews, records learnings, and advances to `done`. Use when asked to "work the backlog" or "execute the next item". |
| `backlog-manager` | Reading, adding, refining, starting, completing, and archiving backlog items. Use before `backlog-worker` to ensure items are in `ready` status. |
| `strategy-author` | Producing strategy using Rumelt's Kernel (Diagnosis, Guiding Policy, Coherent Actions). Use when defining or reviewing the guiding policy, evaluating strategic options, or translating a diagnosis into a coherent set of backlog priorities. Use before `backlog-manager` when the priority stack or guiding policy needs revision. |
| `swe` | Implementing features, making architectural decisions, reviewing designs for SOLID/REST/pattern adherence. |
| `tdd` | Writing tests before or alongside implementation. Use with `swe` for all production code changes. |
| `code-review` | Reviewing completed code for quality, correctness, and adherence to conventions. Apply at the end of every `backlog-worker` execution cycle. |
| `technical-writer` | Writing and updating documentation (ADRs, progress.md, learnings.md, glossary.md). |
| `adr` | Drafting Architecture Decision Records in `docs-adr/`. Use when making a significant technical decision. |
| `research` | Investigating unknowns before acting. Use when an item requires discovery before implementation. |
| `feedback` | Evaluating non-code outputs (documentation, data analysis, UI copy) before marking an item done. |

**How to invoke a skill**: Call the skill sub-agent at the start of work that matches its scope. Skills compose — `backlog-worker` orchestrates `swe`, `tdd`, `code-review`, `technical-writer`, and `feedback` as needed for each item.

**Backlog workflow**: `strategy-author` to validate or revise the guiding policy → `backlog-manager` to refine items to `ready` → `backlog-worker` to execute them → `code-review` to verify → `technical-writer` to update docs → `backlog-manager Complete` to close.
