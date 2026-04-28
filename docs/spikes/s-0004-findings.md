# S-0004 Findings: Multi-Bank PDF Disclosure Statement Inspection

**Date:** 2026-04-28
**Spike ID:** S-0004
**Status:** Complete -- findings populated from `scripts/spike_bnz_pdf.py` and
`scripts/spike_multi_bank_pdf.py` runs on 2026-04-28

---

## What Was Investigated

Whether bank General Disclosure Statements (GDS) published as PDFs are
machine-readable using `pdfplumber`, and whether the financial tables they
contain overlap with or extend the RBNZ Bank Financial Strength Dashboard
metrics already in the pipeline.

Three of the six banks were inspected: BNZ, Kiwibank, and Rabobank. ANZ, ASB,
and Westpac PDFs were inaccessible from the pipeline environment (HTTP 403/404)
-- see the [Inaccessible Banks](#inaccessible-banks) section.

**Findings JSON files (per-bank):**
```
data/raw/financial_disclosures/bnz/spike_s0004_multi_findings.json
data/raw/financial_disclosures/kiwibank/spike_s0004_multi_findings.json
data/raw/financial_disclosures/rabobank/spike_s0004_multi_findings.json
data/raw/financial_disclosures/spike_s0004_cross_bank_summary.json
```

---

## Cross-Bank Summary

| Bank | Period | Pages | Table pages | Image pages | Primary method |
|---|---|---|---|---|---|
| BNZ | 2024-09-30 | 98 | 3 | 3 | `extract_text()` |
| Kiwibank | 2024-06-30 | 113 | 79 | 1 | `extract_tables()` |
| Rabobank | 2022-12-31 | 107 | 9 | 5 | `extract_text()` |
| ANZ | 2024-09-30 | -- | -- | -- | NOT ACCESSIBLE |
| ASB | 2024-06-30 | -- | -- | -- | NOT ACCESSIBLE |
| Westpac | 2024-03-31 | -- | -- | -- | NOT ACCESSIBLE |

---

## BNZ (year ended 30 September 2024, 98 pages)

**Source:** `https://www.bnz.co.nz/assets/about-us/financials/pdfs/bnz-disclosure-statement-year-ended-30-september-2024.pdf`

### Structure

`pdfplumber.extract_tables()` found 3 tables across 98 pages. Only page 52
contains useful structured financial data (a segment P&L summary). Pages 86-87
contain audit key matter layout tables (free-text, not financial data).

The substantive financial statements are rendered as **text columns** -- visually
tabular but not PDF table objects. `extract_text()` retrieves them cleanly.

### Income Statement (page 10)

**Method:** `extract_text()` | **Tables:** 0

```
Income Statement -- For the year ended 30 September 2024 -- Banking Group
Dollars in Millions                                     Note  30/9/24  30/9/23
Effective interest income                                  2    7,722    6,759
Fair value through profit or loss                          2      458      325
Interest expense                                           2    5,271    4,187
Net interest income                                              2,909    2,897
Gains less losses on financial instruments                 3      273      245
Other operating income                                     4      434      355
Total operating income                                           3,616    3,497
Operating expenses                                         5    1,392    1,222
Total operating profit before credit impairment                  2,224    2,275
Credit impairment charge                                  11      146      172
Total operating profit before income tax expense                 2,078    2,103
Income tax expense                                         6      572      594
Net profit for the year                                          1,506    1,509
```

All P&L line items are present with current and prior year values. The interest
income split (effective interest vs fair value) extends the RBNZ dashboard which
only records net interest margin.

### Balance Sheet (page 12)

**Method:** `extract_text()` | **Tables:** 0

```
Balance Sheet -- As at 30 September 2024 -- Banking Group
Dollars in Millions                         Note  30/9/24   30/9/23
Cash and liquid assets                         7    5,711    10,950
Due from central banks and other institutions       72         90
Collateral paid                                    927      1,107
Trading assets                                 8   11,103    9,143
Derivative financial instruments              13    3,744    4,802
Loans and advances to customers               10  106,101  101,778
Other assets                                  15    1,563      777
Deferred tax                                  14      345      316
Property, plant and equipment                       622        604
Goodwill and other intangible assets          16      540      498
Total assets                                       130,737  130,065
Due to central banks and other institutions   17    4,879    6,080
Collateral received                                 1,057    1,780
Bonds and notes                               20   19,385   20,786
Deposits from customers                       19   82,284   78,502
Derivative financial instruments              13    3,741    4,715
Total liabilities                                  121,596  121,163
Total equity                                         9,141    8,902
```

Full balance sheet is machine-readable with all asset and liability line items.
Extends the RBNZ dashboard with granular asset breakdown and deposit funding detail.

### Cash Flow Statement (page 13)

**Method:** `extract_text()` | **Tables:** 0

```
Cash Flow Statement -- For the year ended 30 September 2024 -- Banking Group
Dollars in Millions                                         Note  30/9/24   30/9/23
Interest income received                                           8,247     7,003
Interest expense paid                                             (5,140)   (3,790)
Net trading income                                                   265       658
Other income                                                         360       355
Personnel expenses                                                  (726)     (705)
Other operating expenses                                            (565)     (373)
Taxes paid                                                          (425)     (830)
Net cash from operating activities before WC changes               2,016     2,318
Net (increase)/decrease in loans and advances to customers        (4,435)   (2,557)
Net cash from operating activities                                (3,182)   (2,416)
Net cash from investing activities                                   337       182
Net cash from financing activities                                 (2,337)     503
```

Operating, investing, and financing cash flows are all present.

### Capital Adequacy (page 58 + Notes 35, pages 60-65)

**Method:** `extract_text()` | **Tables:** 0

```
Note 35 Capital Adequacy
The RBNZ minimum regulatory capital requirements for banks have been established
under the "Banking Prudential Requirements" (BPR) based on the Basel III framework.

Banking Group (30/9/24)                    CET1      Tier 1    Total Capital
Capital ratio                              13.5%      14.0%        16.2%
Required ratio                              4.5%       6.0%         8.0%
Capital Conservation Buffer                2.5%       2.5%         2.5%
D-SIB Surcharge                            1.0%       1.0%         1.0%
Total required (incl. buffers)             8.0%       9.5%        11.5%
```

Full RWA breakdown by exposure class (IRB approach) available via text. This
significantly extends the RBNZ dashboard, which provides only the top-level ratios.

---

## Kiwibank (year ended 30 June 2024, 113 pages)

**Source:** `https://api.nzx.com/public/announcement/436602/attachment/425238/436602-425238.pdf`
(Obtained via NZX announcement page; `media.kiwibank.co.nz` is not reachable from the pipeline)

### Structure

79 of 113 pages contain PDF table objects. `extract_tables()` is the primary
method. However, the statement pages (Income Statement, Balance Sheet, Cash Flow)
use a **sparse table layout** -- only summary totals appear on the statement pages;
detailed breakdowns are in note tables later in the document.

1 image-based page (index/cover art).

### Income Statement (page 10)

**Method:** `extract_tables()` | **Tables:** 8 (sparse layout)

```
Income Statement -- For the year ended 30 June 2024
$ millions                                       Note  30 June 24  30 June 23
Net interest income                                          824         794
Total operating income                                       880         816
Profit before credit impairment and tax                      298         282
Profit before tax                                            274         245
Profit after tax                                             202         175
```

**Note: page 10 shows only 5 summary line items.** The full interest income
breakdown (by product/customer type) is in Note 2 (pages 19-20):

```
Note 2. Interest income and interest expense (page 20 -- tables)
$ millions                                       30 June 24  30 June 23
Total interest income                                 1,983       1,389
Total interest expense                                1,159         595
```

The detailed split (retail mortgages, corporate, treasury) is present but
requires traversal of note tables on pages 19-22.

### Balance Sheet (page 12)

**Method:** `extract_tables()` | **Tables:** 5 (summary only on statement page)

```
Balance Sheet -- As at 30 June 2024
$ millions                               Note  30 June 24  30 June 23
Total assets                                      36,650      33,838
Total liabilities                                 34,029      31,527
Net assets                                         2,621       2,311
Total equity                                       2,621       2,311
```

**Note: Only 4 summary lines on the statement page.** Line-item breakdowns
(loans by category, deposit funding, etc.) are in note tables (pages 25-45).
`extract_tables()` retrieves these note tables cleanly.

### Cash Flow Statement (pages 13-14)

**Method:** `extract_tables()` | **Tables:** 6 + 2

```
Cash Flow Statement -- For the year ended 30 June 2024
$ millions                                            30 June 24  30 June 23
Net cash from operating activities (pre-WC changes)      353         429
Net cash from operating activities                      (359)      (1,328)
Net cash from investing activities                        (9)          (11)
Net cash from financing activities                       346          844
Cash and cash equivalents at end of period                          1,005
```

Summary cash flow totals are available. Operating, investing, and financing
line items are accessible via note tables.

### Capital Adequacy (page 91)

**Method:** `extract_text()` + 1 table | Capital ratio text present

The capital adequacy section includes the required ratios (CET1, Tier 1, Total
Capital) and regulatory liquidity ratios, comparable to BNZ's disclosure. The
layout is standardised (both use RBNZ BPR requirements under Basel III).

---

## Rabobank (year ended 31 December 2022, 107 pages)

**Source:** `https://www.rabobank.co.nz/content/dam/ranz/ranz-website-images/rbnz-files/pdf/disclosures/2022/rnzl-disclosurestatement-311222.pdf`

Note: The 2023 URL (`globalassets/...`) returns HTTP 403 from the pipeline. The
2022 URL (`content/dam/...`) returns HTTP 200. Both are confirmed in
`config/sources.yaml`; the 2022 report is the most recent accessible version.

### Structure

Text-based for most pages (9 table pages, 5 image-based pages). The
**Statement of Financial Position (Balance Sheet) is rendered as an image on
page 35** -- 0 chars extracted, no tables. This is a critical gap.

### Income Statement (page 34) -- Statement of Comprehensive Income

**Method:** `extract_text()` | **Tables:** 0

```
Statement of Comprehensive Income -- Year ended 31 December 2022
In thousands of NZD                              Note    2022       2021
Interest income                                    4   643,766   445,795
Interest expense                                   5  (278,498) (115,191)
Net interest income                                    365,268   330,604
Other income                                       6     2,713     2,554
Other expense                                      7      (375)     (454)
Other operating losses                             8    (7,093)     (663)
Non-interest income/(expense)                           (4,755)    1,437
Operating income                                       360,513   332,041
Operating expenses                                 9  (156,009) (147,884)
Impairment benefits/(losses)                      10      (103)   16,571
Profit before income tax                               204,401   200,728
Income tax expense                               12.1   (57,294)  (56,277)
Net profit for the year                                147,107   144,451
```

Complete P&L is machine-readable via text. Interest income breakdowns are in
Note 4 (page 50): loans/advances, related entities, FVOCI securities, cash,
and inter-bank positions.

Note: **Values are in thousands of NZD** (not millions), unlike BNZ and Kiwibank.
A unit normalisation step is required when comparing across banks.

### Balance Sheet -- Statement of Financial Position (page 35)

**Method: IMAGE-BASED -- not machine-readable**

Page 35 has 0 extractable characters and no tables. The Statement of Financial
Position is rendered as a scanned image. This is the only critical gap for
Rabobank; all other sections are text-based.

The total assets figure ($8,065,867 thousand) is inferrable from the
Statement of Changes in Equity and Notes, but line-item extraction requires
OCR or manual lookup.

### Cash Flow Statement (page 37)

**Method:** `extract_text()` | **Tables:** 0

```
Statement of Cash Flows -- Year ended 31 December 2022
In thousands of NZD                                          2022      2021
Interest income received                                  630,455   445,597
Other income                                                2,713     2,554
Interest paid                                            (224,345) (126,134)
Management fees and other operating expenses             (138,434) (140,815)
Tax payments                                              (58,395)  (40,344)
Net cash from operating activities before WC changes      212,330   140,476
Due to related entities                                    29,314   (57,955)
Net cash from operating activities                        (...)
```

Operating, investing, and financing flows present and machine-readable.

### Capital Adequacy (pages 23-27)

**Method:** `extract_text()` | **Tables:** 0

```
Capital Adequacy -- Standardised Approach (unaudited) -- 31 December 2022
In thousands of NZD
Tier 1 capital
  Common Equity Tier 1 (CET1)                               551,200
  Retained earnings (net of appropriations)               1,505,883
  Accumulated other comprehensive income                    (15,689)
  Less deductions from CET1:
    Deferred tax assets                                     (15,719)
    Goodwill and other intangible assets                     (1,203)
Total CET1 capital                                        2,024,472
Total Tier 2 capital                                         19,500
Total capital                                             2,043,972
```

Full standardised approach tables (credit risk by exposure class, operational
risk, market risk, liquidity ratios) are machine-readable via text. Note:
Rabobank uses the Standardised Approach; BNZ and Kiwibank use the IRB approach.
Capital ratios are computed differently and are not directly comparable.

---

## Inaccessible Banks

The following banks' PDFs could not be downloaded from the pipeline sandbox:

| Bank | Status | Last confirmed URL |
|---|---|---|
| ANZ | HTTP 404 -- URL pattern changed | `anz.co.nz/content/dam/anzcoz/...` |
| ASB | HTTP 404 -- URL pattern changed | `asb.co.nz/content/dam/asb/...` |
| Westpac | HTTP 403/000 -- WAF blocking | `westpac.co.nz/assets/About-us/...` |
| Kiwibank | HTTP 000 -- media CDN blocked | `media.kiwibank.co.nz/...` (NZX API used instead) |

All four maintain accessible web pages and publish disclosure statements;
the block is environment-specific (pip sandbox outbound traffic restrictions).
ANZ and ASB return correct PDFs in a browser. Westpac's WAF may require
a cookie or session token.

**Impact on extraction decision:** ANZ and ASB are the two largest NZ retail
banks. Without inspecting their PDFs, the cross-bank layout comparison is
incomplete. This remains an open action item before W-0015 begins.

---

## Narrative Summary: Financial Statement Comparisons

### Income Statement

All three inspected banks include:
- Interest income and interest expense (gross)
- Net interest income
- Total operating income
- Operating expenses
- Credit impairment charge / benefit
- Profit before tax
- Income tax expense
- Net profit after tax

**BNZ** is the most granular on the statement page itself (interest income split
into effective interest + fair value; gains on financial instruments separated).

**Kiwibank** shows only 5 summary line items on the statement page; full detail
requires note traversal.

**Rabobank** is fully granular on the statement page; values are in NZD thousands
(not millions), requiring normalisation.

### Balance Sheet

| Field | BNZ | Kiwibank | Rabobank |
|---|---|---|---|
| Cash and central bank | Yes | Note tables | IMAGE-BASED |
| Loans and advances | Yes | Note tables | IMAGE-BASED |
| Total assets | Yes | Yes | IMAGE-BASED |
| Deposits from customers | Yes | Note tables | IMAGE-BASED |
| Total equity | Yes | Yes | IMAGE-BASED |

The Rabobank balance sheet being image-based is a significant gap. BNZ provides
the most complete machine-readable balance sheet on the statement page.

### Cash Flow Statement

All three banks provide net cash flows from operating, investing, and financing
activities. BNZ and Rabobank provide detailed cash flow line items on the statement
page; Kiwibank provides only summary subtotals.

### Capital Adequacy

All three banks provide:
- CET1, Tier 1, and Total Capital ratios
- Required capital ratios (RBNZ BPR minimums)
- Capital surplus vs requirements

BNZ and Kiwibank use the **IRB approach** (more granular, risk-weighted by internal
rating). Rabobank uses the **Standardised Approach** (exposure class averages).
Cross-bank capital comparison requires acknowledging this methodological difference.

---

## Updated Recommendation: Extraction Approach for W-0015

**Recommendation: Hybrid extraction -- `extract_tables()` then `extract_text()` fallback.**

This approach is required because:
1. Kiwibank is predominantly table-based (79/113 pages have table objects);
   `extract_text()` alone would miss structured data.
2. BNZ and Rabobank use text columns; `extract_tables()` finds only 3 and 9
   tables respectively, missing the primary financial statements.
3. The Rabobank Balance Sheet is image-based -- a gap to document, log, and
   fill with OCR if and when required (log WARNING, store null for now).

**Decision deferred:** A final extraction approach decision should not be made
until ANZ and ASB PDFs are inspected. These two banks represent the largest
share of NZ banking assets and may use different layouts. Inspect before W-0015
begins.

No new dependencies are required beyond `pdfplumber` (already in `pyproject.toml`).
If Rabobank or Westpac require OCR for their balance sheets, add `pytesseract` or
`pdfminer.six` at that point and open ADR-0005.

---

## Open Questions and Risks

- **ANZ and ASB not inspected** -- The two largest NZ banks are blocked from
  download in the pipeline environment. Their layouts may differ significantly
  from BNZ/Kiwibank/Rabobank. Manual inspection or a separate environment is
  needed before committing to an extraction pipeline. **HIGH PRIORITY.**

- **Rabobank Balance Sheet is image-based** -- Page 35 of the 2022 report is a
  scanned image with 0 extractable characters. Balance sheet data is unavailable
  via pdfplumber for this bank without OCR. Log WARNING and store null until
  resolved.

- **Kiwibank CDN blocked** -- `media.kiwibank.co.nz` is unreachable from the
  pipeline sandbox. The NZX API provided a workaround for the 2024 report. Verify
  this remains accessible and update the source URL in `config/sources.yaml`.

- **Unit inconsistency** -- BNZ and Kiwibank report in NZD millions; Rabobank
  reports in NZD thousands. The extraction pipeline must normalise units to a
  canonical scale (NZD millions). A `config/metrics.yaml` unit field or a
  per-source multiplier is needed.

- **Year-to-year schema changes** -- BNZ restated some notes in 2022.
  The parser must handle absent or renamed rows gracefully (log WARNING, store null).

- **Westpac URL validation** -- Westpac returns HTTP 403. The most recent
  confirmed URL in config/sources.yaml is a half-year report (March 2024). The
  full-year September 2024 report is pending. URL validation via
  `scripts/validate_disclosure_urls.py` should be re-run after updating URLs.

- **ADR not required at this time** -- No new dependencies are introduced.
  If OCR (pytesseract or pdfminer.six) is adopted for image-based pages, open
  ADR-0005 before implementing.
