# Copilot Instructions — Companies Performance

## Purpose

This repository tracks the financial performance of companies using structured data pipelines and static visualisation. The primary data source is the RBNZ Bank Financial Strength Dashboard XLSX.

---

## Skills

Skills are stored as sub-agent definitions in `.github/skills/`. Load the relevant skill at the start of any task that matches its description — do not synthesise a substitute.

| Skill | When to use |
|---|---|
| `backlog-worker` | Executing ready backlog items — selects, decomposes, acts, reviews, marks done. Use when asked to "work the backlog". |
| `backlog-manager` | Reading, adding, refining, starting, completing, and archiving items in `BACKLOG.md`. Use before `backlog-worker`. |
| `strategy-author` | Producing strategy using Rumelt's Kernel (Diagnosis, Guiding Policy, Coherent Actions). Use when the guiding policy or priority stack needs revision. Use before `backlog-manager`. |
| `swe` | Implementing features, making architectural decisions, reviewing designs for SOLID/REST/pattern adherence. |
| `tdd` | Writing tests before or alongside implementation. Use with `swe` for all production code changes. |
| `code-review` | Reviewing completed code for quality, correctness, and adherence to conventions. Apply at the end of every `backlog-worker` cycle. |
| `technical-writer` | Writing and updating documentation (ADRs, `PROGRESS.md`, `learnings.md`, `glossary.md`). |
| `adr` / `decisions` | Drafting Architecture Decision Records in `docs-adr/`. Use when making a significant technical decision. |
| `research` | Investigating unknowns before acting. Use when an item requires discovery before implementation. |
| `feedback` | Evaluating non-code outputs (documentation, data analysis, UI copy) before marking an item done. |

**How to invoke a skill**: Call the skill sub-agent at the start of work that matches its scope. Skills compose — `backlog-worker` orchestrates `swe`, `tdd`, `code-review`, `technical-writer`, and `feedback` as needed for each item.

---

## Skill Chains

Every significant task maps to a skill chain. Apply in sequence rather than working from general reasoning alone. **These chains are guidance for non-trivial work — do not apply them to minor config changes or documentation updates where the overhead outweighs the value.**

| Task type | Skill chain |
|---|---|
| Research a topic before acting | `research` → findings → decide |
| Turn research into a plan | `research` → `strategy-author` → `backlog-manager` |
| Revise guiding policy or priority stack | `strategy-author` → `backlog-manager` |
| Work the backlog | `backlog-manager` (refine to `ready`) → `backlog-worker` (execute to `done`) |
| Implement a feature or fix a bug | `swe` (design) → `tdd` (test-first) → `code-review` (verify) |
| Write or improve documentation | `technical-writer` → `feedback` |
| Write an ADR | `decisions` |

---

## Backlog Mandate

The backlog is `BACKLOG.md` at the repo root. Read it at the start of every session. Use the `backlog-manager` skill to manage items and `backlog-worker` to execute them.

`BACKLOG.md` contains standalone **W-XXXX items** with `status: ready | active | done | archived`. These are the target of `backlog-worker`.

---

## PROGRESS.md Mandate

Append a dated entry to `PROGRESS.md` after every meaningful session or PR. Never edit old entries — append only. Format: `## YYYY-MM-DD — <summary>` then what changed and why.

---

## learnings.md Mandate

`learnings.md` records **patterns, root causes, and per-session technical discoveries** — things a future agent should know before touching related code. Read it at the start of any session involving pipeline code, tests, or the site. Append a new dated section when a session surfaces a new pattern or resolves a recurring friction point. `PROGRESS.md` records what was done; `learnings.md` records what was learned.

---

## CHANGELOG.md Mandate

Record every user-facing schema or pipeline change in `CHANGELOG.md`. Follow [Keep a Changelog 1.0.0](https://keepachangelog.com/en/1.0.0/). New entries go under `## [Unreleased]` at the top. Adding a `CHANGELOG.md` entry is a hard gate for any item that modifies `config/metrics.yaml` or the canonical data schema.

---

## ADR Mandate

Every non-trivial architectural or design decision must be recorded as an ADR in `docs-adr/`. Use the `decisions` skill. Format: MADR. Files named `docs-adr/NNNN-short-title.md`. Update `docs-adr/README.md` after adding.

**An ADR is required** any time a change involves one or more of the following:

- Introducing a new external dependency, service, or third-party API
- Choosing between two or more viable technical approaches (document what was rejected and why)
- Changing how agent configuration is delivered (MCP, skills, instructions files)
- Changing how the project is built, tested, or deployed
- Introducing a new persistent file format or data schema
- Any change a future agent would need context on to understand *why* it was done this way

If you find yourself thinking "this is just config" or "this is just wiring" — stop and ask whether a future agent reading only the diff could reconstruct the reasoning. If not, write the ADR.

**"Any new ADRs written and indexed" is a hard gate on slice completion, not a suggestion.**

---

## Slice Completion Checklist

Before marking any backlog item `done`:

- [ ] Code merged to the branch (if applicable)
- [ ] `make check` passes (ruff lint + format)
- [ ] `make test` passes
- [ ] `PROGRESS.md` updated (append-only)
- [ ] `CHANGELOG.md` updated if any schema or pipeline change
- [ ] Any required ADRs written and indexed in `docs-adr/README.md`
- [ ] `glossary.md` updated if any new metrics introduced
- [ ] README updated if user-facing behaviour changed

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

## Output File Naming

Processed output files in `docs/data/processed/` must use descriptive suffixes to avoid naming collisions:
- `_metrics.json` — canonical rows in the `entity | metric | value | period | source` schema
- `_index.json` — lookup or reference lists (e.g. the list of available PDFs with their metadata)

Do not use bare names like `disclosures.json` when both a metrics file and an index file exist for the same source. When creating a new output file, check whether the chosen path already exists and serves a different purpose.

---

## Reference Repository

This repo follows conventions established in `davidamitchell/Research`. Deviations are documented in `docs-adr/0002-directory-structure.md`.

---

## Root Cause Before Action

When something is broken or unclear, spend time on *why* before reaching for a fix.

Most problems fall into one of three categories:

**Context gap** — the information needed to do the right thing was never provided. Surface the missing information; do not guess or patch around it. If you find yourself assuming, write the assumption down and verify it.

**Model error** — the mental model of how the system works is wrong. The code was correct given the model, but the model didn't match reality. Update the model first, then re-derive the solution. Patching the code without fixing the model produces the next bug.

**Specification error** — the task was stated in a way that made the wrong solution look right. If a first attempt produced something reasonable but wrong, look at how the task was framed before retrying.

Treat repeated rework on the same problem as a signal that one of these is unresolved.

---

## Continuous Improvement

After completing each piece of work, conduct a short retrospective focused on **the system that produced the work** — not the application itself.

Ask:
- What friction slowed this work down? (missing decisions, unclear conventions, incomplete scaffolding)
- Was any assumption made without evidence? If so, open a spike or ADR to resolve it.
- Did any step require backtracking because a decision was made too early?
- Is there a workflow, template, or convention that would prevent the same friction next time?
- What **class** of problem did this item represent? Has the root cause been addressed so the same class cannot recur?

Record actionable findings as backlog items (`BACKLOG.md`) or ADRs (`docs-adr/`). Discard observations that produced no action. Do not improve things that aren't broken.

This is not a review of the application's correctness — it is a review of the process that built it.

**Retrospective outputs must address root causes, not symptoms.** If a finding is a symptom (e.g. "a field was missing"), trace it to its root cause (e.g. "the schema contract was not documented") and add a backlog item that eliminates the root cause. Point fixes to recurring problems are not acceptable — the fix must make the class of problem structurally impossible or explicitly governed.

- When a convention is violated, update the convention so it cannot be violated again — do not just fix the one instance.
- When a retrospective identifies friction, add a backlog item that eliminates the **type** of friction, not just the specific instance.
- When a decision is made under uncertainty, open a research spike immediately rather than deferring indefinitely.
- Use `strategy-author` when the root cause is a missing strategic direction or incoherent guiding policy — not every problem needs code; some need a decision.
