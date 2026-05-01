---
title: "ADR-0005: PDF Disclosure Extraction Strategy"
status: "Accepted"
date: "2026-05-01"
authors: "Pipeline team"
tags: ["data-pipeline", "pdf-extraction", "decision"]
supersedes: ""
superseded_by: ""
---

# ADR-0005: PDF Disclosure Extraction Strategy

## 1. Status

Accepted

---

## 2. Context

Bank General Disclosure Statements are the only source of annual P&L, balance sheet, and capital data at bank entity level. No alternative structured feed exists for these figures at the individual bank subsidiary level in the New Zealand market.

The following forces shaped this decision:

- pdfplumber can extract text from machine-readable PDFs without OCR, and covers the income statement pages of ANZ, ASB, BNZ, Kiwibank, and Rabobank disclosures when those pages are text-rendered.
- Disclosure PDFs contain two distinct value format types: financial values denominated in NZDm or NZD thousands, and capital ratio figures expressed as percentages. A single extraction strategy cannot handle both correctly.
- Capital ratio pages follow a standard RBNZ format where each row contains: metric label | regulatory minimum % | current bank ratio % | prior year %. Extracting the first percentage on such a line yields the regulatory minimum, not the bank's actual ratio.
- Financial tables embed note references — integers in the range 1–99 — inline between the metric label and the value column. These appear as the first numeric token on a line, creating false positives if not filtered.
- Rabobank's balance sheet (approximately page 35) is image-rendered; pdfplumber yields zero extractable characters for that page. This is a structural gap in the source data, not a tooling failure.
- Westpac disclosure PDFs are blocked by a Web Application Firewall and cannot be downloaded programmatically, making them unavailable as a data source under current access conditions.
- No LLM or OCR tooling is present in the project. Adding either would introduce API cost, new binary dependencies, non-determinism across model versions, or a requirement for a network-connected environment. The guiding policy is no paid data sources and no external API dependencies in the pipeline.

---

## 3. Decision

We will use pdfplumber `extract_text()` for all PDF text extraction, combined with two regex-based extraction strategies (`first_value` and `second_pct`) applied line-by-line to the full document text.

`extract_text()` is reliable across different PDF authoring tools and produces a consistent plain-text representation of machine-readable pages. `extract_tables()` depends on visual whitespace detection and line separators to infer grid structure; this fails silently on borderless grid layouts used by some banks. `extract_text()` recovered all rows correctly on the same pages where `extract_tables()` returned zero tables.

The two-strategy approach directly addresses the capital ratio column layout problem: `first_value` is used for income statement and balance sheet metrics (10 numeric metrics total), while `second_pct` is used for capital ratio metrics, returning the second percentage token on the line which corresponds to the bank's current ratio. The note-reference filter (skip positive integers ≤99 with no comma separator) is a low-false-positive heuristic validated against all committed PDFs in the repository.

---

## 4. Consequences

### Positive

- **POS-001**: No dependencies beyond pdfplumber (already required by the project); no additional installation steps, no API keys, and no network access required to run the extraction pipeline.
- **POS-002**: Deterministic output — the same PDF always yields the same extracted value, with no variance across runs or environments.
- **POS-003**: 34 unit tests validate all extraction patterns against committed PDFs; regressions caused by pattern drift or code changes are caught before deployment.

### Negative

- **NEG-001**: Rabobank balance sheet metrics (Total Assets, Net Loans, Deposits, Equity) are null in pipeline output because the relevant page is image-rendered; this cannot be fixed without introducing OCR (see ALT-005/ALT-006).
- **NEG-002**: Regex patterns are brittle to layout changes in source PDFs; if a bank reformats its income statement page, affected patterns must be updated and re-validated against all historical PDFs from that bank before the change can be deployed.
- **NEG-003**: `extract_text()` does not preserve column alignment; the note-reference heuristic (skip integers ≤99) is an approximation that could misfire if a bank legitimately reports a financial value smaller than 100 in a position that the heuristic treats as a note reference.

---

## 5. Alternatives Considered

#### pdfplumber `extract_tables()`

- **ALT-001**: **Description**: Use pdfplumber's table detection mode instead of raw text extraction. Table detection returns structured row/column data that would eliminate the need for regex parsing and note-reference filtering.
- **ALT-002**: **Rejection Reason**: Table detection relies on visual whitespace and line separators to infer grid structure. Tested on the ASB 2022 disclosure — `extract_tables()` produced zero tables for the income statement page, which uses a borderless grid layout. `extract_text()` recovered all rows correctly on the same page. Silent failure with no error raised makes this mode unreliable as a primary strategy.

#### LLM-based extraction

- **ALT-003**: **Description**: Pass page text or page images to a large language model (e.g. GPT-4o) via API and extract values using a structured prompt with schema validation.
- **ALT-004**: **Rejection Reason**: Adds per-call API cost and a network dependency to a zero-cost, offline-capable pipeline. Introduces non-determinism — the same PDF may yield different extracted values across model versions or API updates. Violates the guiding policy constraint of no paid data sources and no external API dependencies in the pipeline.

#### OCR (Tesseract / cloud vision)

- **ALT-005**: **Description**: Render each PDF page as a raster image and apply OCR (Tesseract locally, or a cloud vision API) to extract text, then apply the same regex strategy to the OCR output.
- **ALT-006**: **Rejection Reason**: Adds a Tesseract binary dependency (or cloud API cost and network dependency) that is unnecessary for the majority of PDFs, which are machine-readable. This alternative is reconsidered only if NEG-001 (Rabobank balance sheet gap) becomes high priority — specifically, if Rabobank balance sheet metrics are required for a sector-level comparison that materially affects dashboard conclusions.

#### Manual data entry

- **ALT-007**: **Description**: Maintain a hand-curated CSV of disclosure figures, updated each reporting cycle by a team member reading the PDFs directly.
- **ALT-008**: **Rejection Reason**: Not maintainable as the number of banks and reporting periods grows; introduces transcription error risk with no automated audit trail; values cannot be independently reproduced or verified by another team member or automated process.

---

## 6. Implementation Notes

- **IMP-001**: Unit detection scans the first 3000 characters of the full document text. Patterns matched (case-insensitive): `$'000` or `NZD thousands` → scale factor 0.001 (thousands); `$ millions`, `NZ$m`, or `NZDm` → scale factor 1.0 (millions). Default scale is 1.0 (millions), which matches the majority of NZ bank disclosures when no unit marker is detected.
- **IMP-002**: `first_value` strategy: scan the matched line token-by-token using `_NUMBER_RE`; return the first token that is not a note reference. Note-reference heuristic: skip a token if it is a positive integer ≤99 with no comma separator. Used for income statement and balance sheet metrics.
- **IMP-003**: `second_pct` strategy: collect all tokens matching `\d+(?:\.\d+)?\s*%` on the matched line and return index [1] (the second match). If only one percentage token exists on the line, return it as a fallback to handle formats that omit the regulatory minimum column. Used for CET1 Ratio and Total Capital Ratio.
- **IMP-004**: PDFs without a `.meta.json` sidecar file are skipped with a WARNING log entry, not an ERROR. This allows partial pipeline runs when new PDFs are added to the repository before their sidecar files are written, without aborting processing of already-complete entries.
- **IMP-005**: Adding a new metric requires: (a) add an entry to `_INCOME_METRICS`, `_BALANCE_METRICS`, or `_CAPITAL_METRICS` in `extract_disclosures.py`; (b) add a failing test before writing the regex pattern (TDD Red step); (c) verify the pattern against all committed PDFs from the relevant bank; (d) add the metric and its definition to `glossary.md`.

---

## 7. References

- **REF-001**: ADR-0001 — Data Format Decision (no derived values stored; canonical schema) — `docs-adr/0001-data-format-decision.md`
- **REF-002**: ADR-0004 — RBNZ Data Contract and canonical schema — `docs-adr/0004-rbnz-data-contract.md`
- **REF-003**: Spike S-0004 findings in `learnings.md` — machine-readability assessment of all committed PDFs, confirming which pages yield extractable text and which are image-rendered
- **REF-004**: pdfplumber documentation — https://github.com/jsvine/pdfplumber
