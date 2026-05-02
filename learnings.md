# Learnings

A living document capturing outputs from discovery spikes. Each entry records what was investigated, what was found, and what decision or action followed.

---

## How to use this document

Each entry has:
- **Problem investigated**: the question the spike was trying to answer
- **Findings**: what was discovered
- **Decision or deferral**: what was decided (or explicitly deferred)
- **Resulting updates**: backlog items opened, ADRs written, or explicit no-action

Entries are added after each spike is completed. Do not add entries for routine implementation work — only spike outputs belong here.

---

## Spike outputs

_No spikes completed yet. See `BACKLOG.md` for open spikes (S-0001, S-0002, S-0003)._

---

## Spike outputs

### S-0001 — RBNZ XLSX structure investigation

**Date completed:** 2026-04-28

**Problem investigated:** What is the structure of the RBNZ Bank Financial Strength Dashboard XLSX? What sheet names, column headers, data types, entity names, and period format does it use?

**Findings:**

- The XLSX contains five sheets: `Data`, `Table Description`, `Series Definitions`, `Supplementary Commentary`, `Revisions`. The `Data` sheet is the primary source.
- The `Data` sheet is **wide format**: each row is a (date, institution) pair; each column from index 2 onwards is a metric series.
- Header structure (0-indexed rows):
  - Row 0: Category group label (e.g. `Capital adequacy - ratios & buffer`)
  - Row 1: Series name (e.g. `C2. CET1 capital ratio`)
  - Row 2: Notes row
  - Row 3: Unit row (`%`, `NZDm`, `no`, or `None`)
  - Row 4: Series ID row (e.g. `DBB.QIB12`) — **stable identifier for mapping**
  - Row 5+: Data rows (col 0 = quarter-end date as `datetime`, col 1 = institution name)
- **112 metric columns** across categories: Issuer credit ratings, Capital adequacy, Asset quality, Profitability, Balance sheet, Liquidity, Credit concentration.
- **22 institutions** in the current data: ANZ, ANZ Group, ASB, BNZ, BOB, BOC, BOC Group, BOI, CBA Group, CCB, CCB Group, Co-op, Heartland, ICBC, ICBC Group, Kiwibank, Rabo Group, Rabobank, SBS, TSB, WBC Group, Westpac.
- **Period range:** 2018-Q1 through 2025-Q4 (published March 2026).
- Quarter-end dates are `datetime` objects (e.g. `2025-12-31`); converted to `YYYY-QN` strings by the pipeline.
- **LCR (Liquidity Coverage Ratio) is not reported** in this file. The Liquidity section includes Core Funding Ratio (CFR), 1-month mismatch ratio, and 1-week mismatch ratio only.
- **Provisioning Coverage** is not directly reported; it would need to be derived from individual provisions ÷ non-performing loans — not stored per ADR-0001.

**Decision or deferral:**

- Map series by series ID (row 4), not by series name — IDs are stable across RBNZ publication updates.
- Populate `config/metrics.yaml` with initial mappings for 20 key series (see W-0006).
- Write ADR-0004 to formalise the data contract.
- LCR: mark as not available in ADR-0004 and glossary. No backlog item opened.

**Resulting updates:** W-0006 marked done, ADR-0004 written, `glossary.md` extended, `config/metrics.yaml` populated.

---

### S-0002 — Additional bank disclosure sources (PDF annual reports)

**Date completed:** 2026-04-28

**Problem investigated:** Are additional bank disclosure sources (e.g. annual report PDFs) feasible for inclusion in the pipeline?

**Findings:**

- NZ bank annual reports are publicly available as PDFs from each bank's investor relations page.
- Extracting structured data from PDFs requires either: (a) a table-extraction library (e.g. `pdfplumber`, `camelot`), or (b) an LLM-based extraction pipeline (W-0015).
- The RBNZ dashboard already covers the key regulatory metrics. Annual reports provide qualitative commentary, detailed segment breakdowns, and some metrics not in the dashboard (e.g. Operating Efficiency Ratio, Cost-to-Income).
- PDF formats differ significantly across banks and years, making a general extraction pipeline non-trivial.

**Decision or deferral:**

- Deferred pending completion of Phase 3 (working frontend with RBNZ data) and LLM extraction tooling (W-0015).
- No new backlog items opened at this stage.

**Resulting updates:** None. S-0002 closed as explicitly deferred.

---

### S-0003 — Metric inconsistencies across banks

**Date completed:** 2026-04-28

**Problem investigated:** Are there metric inconsistencies across banks in the RBNZ data — different reporting periods, different metric coverage?

**Findings:**

- **Group vs. standalone entities:** 8 of the 22 institutions appear in both standalone and group form (e.g. ANZ / ANZ Group, BOC / BOC Group, ICBC / ICBC Group, WBC Group / Westpac, Rabo Group / Rabobank, CBA Group). Group entities have different regulatory reporting boundaries and different metric coverage to their standalone counterparts. This creates apparent duplicates at the entity level.
- **Smaller bank coverage gaps:** Smaller institutions (BOB, BOI, CCB, Co-op, Heartland, ICBC, SBS, TSB) have fewer non-null values across metrics, particularly in capital breakdown and risk-weighted asset categories. Some only report a subset of the dashboard series.
- **Period coverage:** All institutions share the same quarterly period axis (2018-Q1 to 2025-Q4), but cells may be null for periods where data was not yet reported or not applicable.
- **Metric unit consistency:** All % metrics are expressed in percentage points (e.g. CET1 Ratio of 11 = 11%). All NZDm metrics are in NZD millions. No normalisation is required.
- **No LCR inconsistency** to investigate as LCR is not in the dataset.

**Decision or deferral:**

- No schema or pipeline changes needed. The canonical output includes all entities (group and standalone) — consumer filtering is the responsibility of the frontend or analyst.
- Document group/standalone distinction in ADR-0004 (done).
- Future backlog item: add an `entity_type` field (`standalone` | `group`) to the canonical schema if needed for filtering — not opened now.

**Resulting updates:** ADR-0004 updated to mention group vs. standalone. No new backlog items.

---

## Spike output: PDF text extraction approach for NZ bank disclosures

**Date completed:** 2026-04-30

**Problem investigated:** Can `pdfplumber` extract structured quantitative metrics from NZ bank General Disclosure Statement PDFs reliably enough to build an automated pipeline?

**Findings:**

### Text extraction (Income Statement, Balance Sheet)

- All five tested banks (ANZ, ASB, BNZ, Kiwibank, Rabobank) have PDFs where `page.extract_text()` returns structured text, not image scans. `readable_via_text: true` confirmed in spike S-0004 for all income statement and balance sheet sections.
- Kiwibank (and likely others) uses "$ millions" as the unit header. ANZ uses "NZ$m". Older/smaller banks may use "$'000" (NZD thousands). Unit detection via the first 3000 characters of document text is sufficient.
- Income statement lines follow the pattern: `<label> [note_ref] <current_value> <prior_value>`. Note references are small bare positive integers (≤ 99 for major banks). They can be safely skipped using the heuristic: positive integer, no commas, value ≤ 99.
- Negative values are always represented as bracketed numbers: `(582)` = -582.
- The "Historical summary" page (Kiwibank page 9) and the "Income statement" page (page 10) both contain income-statement metrics. For most metrics, the historical summary either omits them ("Net interest income" is absent in Kiwibank's summary) or repeats the current-period value first. Taking the first occurrence in document text is safe.

### Capital adequacy ratio extraction

- Capital ratio lines consistently appear in the capital adequacy section (late in the document, after notes).
- Line format: `<ratio label> <minimum_requirement%> <banking_group_current%> <prior_period%>`. Three percentage values per line.
- The **first** percentage is the regulatory minimum (RBNZ-set), not the bank's actual ratio. The **second** percentage is the current-period bank ratio. Must use a "second_pct" extraction strategy, not "first_value".
- Example: `"Common equity Tier 1 capital ratio 4.5% 11.9% 10.3%"` → CET1 = 11.9%.
- If only one percentage appears on a line, use it as a fallback (some older formats).

### OCR XLSX data structure

- RBNZ B2 Wholesale Interest Rates XLSX (`rbnz-ocr.xlsx`) contains monthly close data. Each row is one month.
- The OCR column header contains "OCR" or "Official Cash Rate" (case may vary). Column detection by header substring search across the first 10 rows is reliable.
- Monthly → quarterly conversion: group by calendar quarter (Q1 = Jan–Mar, Q2 = Apr–Jun, Q3 = Jul–Sep, Q4 = Oct–Dec) and take the **last available monthly value** per quarter. This gives the quarter-end policy rate, which aligns with bank reporting periods.
- The first column with a `datetime` type value is the date column. Scanning rows 5–15 is sufficient to detect it.

**Decision:**

- Use `pdfplumber` `extract_text()` for all income statement, balance sheet, and capital adequacy extractions. No table extraction needed.
- Two extraction strategies required: `first_value` (income/balance sheet) and `second_pct` (capital ratios).
- Unit scale detection from the first 3000 characters of document text.
- Note number filtering: skip positive integers ≤ 99 with no commas.
- Implemented in `src/processing/extract_disclosures.py`.

**Resulting updates:** W-0015 → done, W-0016 → wont-do, W-0019 → done, W-0022 → done.

---

### W-0024 — Disclosure pipeline end-to-end run (2026-05-01)

**Problem investigated:** Does the extraction pipeline correctly handle all 41 committed disclosure PDFs across all banks?

**Findings:**

- **ANZ** (3 PDFs): 29 rows extracted. All 10 metrics present. One exception: `Total Capital Ratio` missing from `anz-disclosure-2025-03-31.pdf` — format change in the most recent annual report where the capital table label changed. Logged as WARNING.
- **ASB** (16 PDFs): 125 rows. `Net Loans and Advances` is absent for all periods across all ASB PDFs. ASB's balance sheet labels "Loans and advances" without the "Net" prefix, and the regex `r"(?:net )?loans and advances\b"` does not match this. Root cause: regex requires word boundary after "advances" but ASB may have a table format that differs. The early 2018–2020 disclosures also miss `Net Interest Income` — the label is "Net interest income" with lowercase 'i' which should match (case-insensitive), but those early PDFs may have a different format. Needs further investigation.
- **BNZ** (6 PDFs): 52 rows. All 10 metrics present across all periods.
- **Kiwibank** (13 PDFs): 116 rows. Most periods fully extracted. Some older periods (2020–2021) missing `Profit After Tax` and `Equity` — earlier Kiwibank formats differ from current layout.
- **Rabobank** (3 PDFs): 22 rows. 2018-Q4 and 2019-Q4 are fully extracted (10 metrics each). 2022-Q4 yields only 2 metrics (`Deposits`, `Net Loans and Advances`) — the balance sheet page is confirmed image-based (zero text). The 2 extracted values likely come from an overview section or a text-readable sub-table on a different page. These 2 values should be treated as data-quality flags pending verification against the source PDF.
- **Westpac**: 0 rows. WAF block confirmed. No PDFs were accessible for download; the westpac directory contains no PDF files.

**Data quality notes:**
- Total: 344 rows from 41 PDFs across 5 banks (Westpac excluded).
- Rabobank 2022-Q4 partial extraction (2 of 10 metrics) warrants manual verification against the source PDF.
- ASB "Net Loans and Advances" gap is a regex pattern miss, not a PDF structure issue — the label differs from the expected pattern. Open W-0024a as a follow-on fix.

**Decision or deferral:**
- Pipeline validated end-to-end. Output at `docs/data/processed/disclosure_metrics.json` is the new canonical extraction file.
- ASB loan balance gap: open a follow-on backlog item to extend the regex pattern to match ASB's label format.
- Rabobank 2022 partial values: flag in the coverage page (W-0050) rather than filtering them out; let the user see which values are present.

**Resulting updates:** W-0024 → done. New item needed for ASB loan regex fix (add to backlog as W-0074).

---

## 2026-05-02 — Productivity metrics: reference data design patterns

### Pattern: annual reference data joined to quarterly pipeline output

When reference data (FTE, customers) is annual but pipeline output is quarterly, use a "most recent at or before" lookup: find the latest reference row whose `period_end` is at or before the quarter-end date. This correctly assigns the 2022-09-30 FTE figure to 2023-Q1 (March 31) for Sep-year-end banks — no interpolation required.

### Pattern: confidence field propagation

The confidence tier (`exact` / `triangulated` / `estimated`) from the reference data row should be propagated to every output row. This lets the frontend display data quality badges without requiring a separate lookup. When both employee and customer denominators are used in the same metric, propagate the worst-quality confidence of the two.

### Pattern: annualisation of quarterly NZDm values

RBNZ quarterly P&L values (PAT, Operating Expenses, NII) are in NZDm for the quarter. To get an annual figure for per-employee/per-customer productivity: multiply by 4 (quarters per annum), then divide by the denominator, then multiply by 1,000,000 (NZDm → NZD). The RBNZ does not report cumulative YTD figures, so ×4 is the correct annualisation for all quarters.

### Pattern: group entity exclusion

The `entity_type` field in `metrics.csv` distinguishes standalone from group entities. Always check whether this field is populated before filtering — if absent (e.g. in a minimal test fixture), use the employees reference keys as the entity set. Do not default to "group = exclude" when the field is absent.

### FTE data quality notes

- KPMG FIPS is the most reliable public source; publishes ~March-April for the prior calendar year.
- ANZ/BNZ/Westpac fiscal year ends 30 September; ASB/Kiwibank 30 June; Rabobank 31 December.
- Rabobank NZ is primarily agricultural/business banking; per-customer metrics should be interpreted as business-customer metrics, not retail.
- 2022 and 2023 FTE values have `confidence: exact` (KPMG FIPS published figures). Earlier years are triangulated estimates.
