# ADR-0006: Agent Instructions Format and Governance Standards

Date: 2026-05-02
Status: Accepted

## Context

This repository uses `.github/copilot-instructions.md` to direct the behaviour of AI coding agents (GitHub Copilot, Copilot Workspace). The initial instructions were minimal and lacked:

1. Explicit skill chains — agents had to infer how to compose skills rather than follow a documented chain
2. Mandatory gates on slice completion — no explicit checklist enforcing CHANGELOG, PROGRESS.md, and ADR updates
3. Clear criteria for when an ADR is required — agents were making architectural decisions without documenting them
4. A CHANGELOG.md mandate — schema-changing items were not systematically recorded for downstream users
5. A root-cause-before-action discipline — agents were fixing symptoms without addressing structural causes

A review of `davidamitchell/Latest-developments-/.github/copilot-instructions.md` surfaced a more evolved format with all of the above.

## Decision

Adopt the `Latest-developments-` instruction format as the template for this repository's `.github/copilot-instructions.md`. Specifically:

1. Move the Skills section to the top of the file — agent behaviour is most influenced by knowing which skills exist and when to use them
2. Add an explicit Skill Chains table mapping task types to ordered skill sequences
3. Add standalone mandate sections for `BACKLOG.md`, `PROGRESS.md`, `learnings.md`, `CHANGELOG.md`, and ADRs
4. Add a Slice Completion Checklist as a hard gate — every item must satisfy all checklist items before being marked `done`
5. Add explicit "when required" criteria for ADRs
6. Add a "Root Cause Before Action" section classifying problem types (context gap / model error / specification error)
7. Add `CHANGELOG.md` to the repo root following Keep a Changelog 1.0.0

Repo-specific content (financial accuracy rules, RBNZ pipeline conventions, output file naming, separation of concerns) is retained as-is.

## Consequences

### Positive
- POS-001: Agent sessions now have unambiguous chains for every major task type — less reasoning overhead, more consistent outputs
- POS-002: Slice Completion Checklist prevents documentation debt: CHANGELOG, PROGRESS.md, ADR, and glossary updates can no longer be silently skipped
- POS-003: ADR "when required" criteria make the decision to write an ADR explicit — reduces both under-documentation (missing ADRs) and over-documentation (trivial choices)
- POS-004: CHANGELOG.md gives users of the processed data files a machine-readable record of schema evolution — reduces the risk of breaking downstream analyses

### Negative / Trade-offs
- NEG-001: Longer instructions file — more context consumed at the start of each session
- NEG-002: Skill chains are guidance for non-trivial work; applying them to minor config changes adds overhead. Mitigated by the explicit caveat in the Skill Chains section

### Neutral
- NEU-001: Instructions are periodically reviewed against `davidamitchell/Latest-developments-` as that repo evolves; this is not automated
- NEU-002: The `decisions` skill alias is added to the skills table — it is the same as the `adr` skill and both names are valid

## References

- REF-001: `davidamitchell/Latest-developments-/.github/copilot-instructions.md` (reviewed 2026-05-02)
- REF-002: Keep a Changelog 1.0.0 — https://keepachangelog.com/en/1.0.0/
- REF-003: ADR-0002 — Directory Structure (establishes `BACKLOG.md`, `PROGRESS.md` naming standard)
