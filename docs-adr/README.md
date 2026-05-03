# Architecture Decision Records

This directory contains Architecture Decision Records (ADRs) for the Companies Performance project.

ADRs document significant design decisions, the context in which they were made, and the trade-offs considered. They are immutable history — when a decision changes, a new ADR is written that supersedes the old one.

Format: [MADR (Markdown Architectural Decision Records)](https://adr.github.io/madr/)

---

## Index

| ADR | Title | Status | Date |
|---|---|---|---|
| [0001](0001-data-format-decision.md) | Data format: CSV for persistence | Provisional | 2026-04-27 |
| [0002](0002-directory-structure.md) | Directory structure aligned to Research repo | Accepted | 2026-04-27 |
| [0003](0003-manual-rbnz-file-load.md) | Manual initial load of RBNZ XLSX file | Accepted | 2026-04-28 |
| [0004](0004-rbnz-data-contract.md) | RBNZ data contract — canonical schema and XLSX mapping | Accepted | 2026-04-28 |
| [ADR-0005](0005-pdf-extraction-approach.md) | PDF Disclosure Extraction Strategy | Accepted | 2026-05-01 |
| [ADR-0006](0006-agent-instructions-governance.md) | Agent Instructions Format and Governance Standards | Accepted | 2026-05-02 |
| [ADR-0007](0007-scorecard-per-bank-comparison.md) | Strategy Scorecard — Per-Bank Comparison over Sector Average | Accepted | 2026-05-03 |

---

## When to write an ADR

- A new tool, dependency, or external service is adopted
- A file format, naming convention, or workflow is established
- A non-trivial architectural choice is made that would be costly to reverse
- A discovery spike results in a structural decision

---

## How to Add an ADR

1. Copy the template below into a new file `NNNN-short-title.md` (zero-padded, sequential)
2. Fill in all sections
3. Update the index table above
4. Commit with message: `docs: add ADR-NNNN <short title>`

### Template

```markdown
# ADR-NNNN: Title

Date: YYYY-MM-DD
Status: proposed | accepted | superseded by [ADR-XXXX] | deprecated

## Context

What is the problem or situation forcing a decision?

## Decision

What have we decided to do?

## Consequences

### Positive
- ...

### Negative / Trade-offs
- ...

### Neutral
- ...
```
