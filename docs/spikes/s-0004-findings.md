# S-0004 Findings: BNZ PDF Disclosure Statement Inspection

**Date:** 2026-04-28
**Spike ID:** S-0004
**Status:** Template — run `python scripts/spike_bnz_pdf.py` to populate findings

---

## What Was Investigated

Whether bank General Disclosure Statements (GDS) published as PDFs are
machine-readable using `pdfplumber`, and whether the financial tables they
contain overlap with or extend the RBNZ Bank Financial Strength Dashboard
metrics already in the pipeline.

The BNZ full-year September 2024 disclosure statement was chosen as the
representative sample because it is the most recent full-year report for a
major bank with a confirmed URL.

**Source document:**
`https://www.bnz.co.nz/assets/about-us/financials/pdfs/bnz-disclosure-statement-year-ended-30-september-2024.pdf`

---

## PDF Structure

> **To be filled in after running `python scripts/spike_bnz_pdf.py`**
> The findings JSON is written to `data/raw/financial_disclosures/bnz/spike_s0004_bnz_findings.json`.

| Field | Value |
|---|---|
| Total pages | `[total_pages]` |
| Total tables found | `[total_tables_found]` |
| Pages with tables | `[pages_with_tables]` |
| First table on page | `[first_table_page]` |
| First table dimensions | `[first_table_row_count]` rows × `[first_table_column_count]` cols |

### First Table Sample (first 5 rows)

```
[first_table_sample — paste output from spike script here]
```

---

## Machine-Readability Assessment

> **To be filled in after reviewing the spike output.**

Options:

- **Fully machine-readable** — `pdfplumber.extract_tables()` returns well-structured
  lists of lists with clean cell boundaries. No post-processing required beyond
  column-header normalisation.

- **Partially machine-readable** — Tables are detected but cells are merged, split,
  or contain newlines that require post-processing. `pdfplumber` plus a cleaning
  step is sufficient.

- **Image-based / not machine-readable** — `pdfplumber` returns no tables or only
  empty rows, indicating the PDF was scanned or contains rasterised content.
  LLM-assisted extraction or OCR would be required.

**Assessment:** `[FILL IN: fully / partially / image-based]`

---

## Financial Data Fields Found

> **To be filled in after reviewing the spike output.**

List the column headers discovered in tables, noting whether each metric:
- **Overlaps** with an existing RBNZ dashboard series (already in `config/metrics.yaml`)
- **Extends** the dataset with net-new data not available from the RBNZ dashboard

| Table | Column headers | Overlap / Extends |
|---|---|---|
| `[table on page N]` | `[col1, col2, ...]` | `[overlap / extends]` |

---

## Recommendation: Extraction Approach for W-0015

> **To be filled in after reviewing the spike output.**

Based on the machine-readability assessment, one of three approaches is recommended:

1. **`pdfplumber` alone** — if tables are fully machine-readable with clean structure.
   No new dependencies. Recommended if assessment is "fully machine-readable".

2. **`pdfplumber` + post-processing** — if tables require cell-boundary cleaning,
   header normalisation, or multi-row spanning logic. Still no new external dependencies
   beyond `pdfplumber`. Recommended if assessment is "partially machine-readable".

3. **LLM-assisted extraction** — if tables are image-based or layout is too complex
   for rule-based extraction. Introduces a new dependency (API cost, rate limits,
   reproducibility concerns). Requires an ADR before implementation.

**Recommendation:** `[FILL IN: option 1 / option 2 / option 3]`

---

## Open Questions and Risks

- **URL stability** — Kiwibank (10 of 13 URLs pending) and Rabobank (2 pending) must
  be HTTP-validated before ingestion. Run `scripts/validate_disclosure_urls.py` to
  resolve these.

- **BNZ URL gaps** — Three BNZ entries remain `pending` (2023-03-31, 2021-03-31,
  2018-09-30). These may have been removed from the BNZ site or published under
  different filenames. Manual investigation required.

- **Westpac September 2024** — The September 2024 full-year report may not yet be
  published. Re-check after October 2024.

- **Table schema consistency** — Even if the BNZ 2024 PDF tables are machine-readable,
  the schema may differ across years and across banks. A sample of at least 3 banks
  × 2 years should be inspected before committing to an extraction pipeline.

- **LLM cost model** — If LLM extraction is required, the cost per document (
  ~200–400 pages per year across 6 banks × 2 reports) must be estimated before
  committing. This is a blocker for Phase 4.
