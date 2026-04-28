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

_No spikes completed yet. See `backlog.md` for open spikes (S-0001, S-0002, S-0003)._

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
