# S-0004 Findings: BNZ PDF Disclosure Statement Inspection

**Date:** 2026-04-28
**Spike ID:** S-0004
**Status:** Complete — findings populated from `scripts/spike_bnz_pdf.py` run on 2026-04-28

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

**Findings JSON:**
`data/raw/financial_disclosures/bnz/spike_s0004_bnz_findings.json`

---

## PDF Structure

| Field | Value |
|---|---|
| Total pages | 98 |
| Total tables found (via `extract_tables()`) | 3 |
| Pages with tables | 52, 86, 87 |
| First table on page | 52 |
| First table dimensions | 23 rows x 6 cols |

### First Table Sample (page 52 -- Segment P&L Summary, first 5 rows)

```
Net interest income                                | 2,089 |   715 | 2,804 |   105 | 2,909
Other income                                       |   212 |   250 |   462 |   245 |   707
Total operating income                             | 2,301 |   965 | 3,266 |   350 | 3,616
Operating expenses                                 |   262 |    59 |   321 | 1,071 | 1,392
Total operating profit/(loss) before CI and tax    | 2,039 |   906 | 2,945 |  (721)| 2,224
```

Columns represent: Retail segment | Business segment | Combined | Head Office | Banking Group total.

The table contains current year (30/9/24) and prior year (30/9/23) as consecutive row blocks
within the same table (rows 1-11 = FY2024, rows 12-23 = FY2023).

### Tables on Pages 86-87 (Audit Key Matters)

Pages 86 and 87 each contain a single table used as layout for audit key matter descriptions
(credit impairment provisioning and IT controls respectively). These contain free-text
paragraphs in cells, not structured financial data. They are not useful for extraction.

---

## Machine-Readability Assessment

**`extract_tables()` verdict: Insufficient on its own.**

`pdfplumber.extract_tables()` found only 3 tables across 98 pages. Only page 52 contains
useful financial data (a segment P&L summary). The substantive financial statements -- the
full Income Statement (page 10), Balance Sheet, Cash Flow Statement, and all Notes to
Accounts including the detailed Capital Adequacy note (pages 60-65) -- are rendered as
**text columns**: visually tabular, but not PDF table objects. `extract_tables()` returns
nothing for these pages.

**`extract_text()` verdict: Fully present and machine-readable.**

`pdfplumber.extract_text()` successfully extracts all financial statement data as text with
column alignment preserved. Spot-checked examples:

- **Page 10 (Income Statement)** -- all P&L line items present: Interest income (effective
  interest and fair value components), Interest expense, Net interest income, Gains less
  losses on financial instruments, Other operating income, Operating expenses, Credit
  impairment charge, Profit before tax, Income tax expense, Net profit.
- **Pages 60-65 (Note 35 -- Capital Adequacy)** -- full capital adequacy tables: RWA by
  exposure class, Tier 1 capital, Total Capital, capital ratios. This data significantly
  extends the RBNZ dashboard.
- **Page 30 (Note 11 -- Expected Credit Losses)** -- loan staging tables and ECL movements
  by stage.

The text extraction is clean and structured. A custom line parser per section is achievable.

---

## Financial Data Fields Found

### From the machine-readable table (page 52 -- Segment P&L)

| Field | Overlaps RBNZ Dashboard | Notes |
|---|---|---|
| Net interest income | Overlaps | RBNZ has NIM ratio; GDS has dollar value |
| Other income | Overlaps | Aligns with RBNZ Other Operating Income |
| Total operating income | Overlaps | |
| Operating expenses | Overlaps | RBNZ has Operating Expenses series |
| Credit impairment charge | Overlaps | RBNZ has Impairment Charges |
| Income tax expense | Extends | Not in RBNZ dashboard |
| Net profit for the year | Overlaps | RBNZ has Net Profit After Tax |
| Lending assets | Overlaps | RBNZ has Total Lending Assets |
| Deposit liabilities | Extends | Granular deposit funding not in dashboard |

### From text extraction (pages 60-65 -- Capital Adequacy, Note 35)

Full capital adequacy data by exposure class and risk weights. This **significantly
extends** the RBNZ dashboard which provides only top-level ratios (CET1, Tier 1,
Total Capital Ratio).

---

## Recommendation: Extraction Approach for W-0015

**Recommendation: `pdfplumber.extract_text()` + custom post-processing (Option 2).**

Rationale:

- `extract_tables()` alone finds only 3 tables in 98 pages; the substantive financial
  data is in text columns, not PDF table objects. Option 1 (tables only) is ruled out.
- `extract_text()` retrieves all financial data as structured text. A custom line-parser
  per section (Income Statement, Balance Sheet, Capital Adequacy note) is achievable
  given the consistent layout within BNZ reports.
- No new external dependencies are required beyond `pdfplumber` (already in `pyproject.toml`).
- LLM extraction (Option 3) is NOT recommended at this stage -- it introduces API cost,
  non-determinism, and a vendor dependency. The text output is clean enough for rule-based
  parsing. If cross-bank or cross-year layout variation proves too high, revisit at that point.

No ADR is required at this time. If W-0015 determines LLM extraction is necessary,
open ADR-0005 before implementation.

---

## Open Questions and Risks

- **Cross-bank layout consistency** -- This spike inspected one bank (BNZ) for one year.
  ASB, Westpac, Kiwibank, and Rabobank may use different section headings, column structures,
  or footnote conventions. A sample of at least 3 banks x 2 years should be validated
  before building the extraction pipeline.

- **Year-to-year schema changes** -- BNZ restated some prior-period notes in 2022. The
  parser must handle absent or renamed rows gracefully (log WARNING, store null).

- **Pending URLs** -- 16 URLs remain pending (BNZ x3, Westpac x1, Kiwibank x9, Rabobank x2).
  Run `scripts/validate_disclosure_urls.py` before ingestion.

- **BNZ download requires browser User-Agent** -- The BNZ asset CDN blocks non-browser
  User-Agents (times out with a bot-like User-Agent). The spike script has been updated to
  use a Chrome User-Agent string. This is a fragile dependency; monitor if BNZ changes
  their CDN configuration.
