# S-0004 Findings: Multi-Bank PDF Disclosure Statement Inspection

**Date:** 2026-04-28
**Spike ID:** S-0004
**Status:** Complete -- findings populated from `scripts/spike_bnz_pdf.py` and
`scripts/spike_multi_bank_pdf.py` runs on 2026-04-28 (BNZ, Kiwibank, Rabobank) and 2026-04-29 (ANZ, ASB)

---

## What Was Investigated

Whether bank General Disclosure Statements (GDS) published as PDFs are
machine-readable using `pdfplumber`, and whether the financial tables they
contain overlap with or extend the RBNZ Bank Financial Strength Dashboard
metrics already in the pipeline.

Five of the six banks have been inspected: BNZ, Kiwibank, Rabobank, ANZ, and
ASB. ANZ and ASB PDFs were retrieved after navigating their investor pages to
find the correct CDN URLs. Westpac PDFs remain inaccessible (HTTP 403/WAF block)
-- see the [Inaccessible Banks](#inaccessible-banks) section.

**Findings JSON files (per-bank):**
```
data/raw/financial_disclosures/anz/spike_s0004_multi_findings.json
data/raw/financial_disclosures/asb/spike_s0004_multi_findings.json
data/raw/financial_disclosures/bnz/spike_s0004_multi_findings.json
data/raw/financial_disclosures/kiwibank/spike_s0004_multi_findings.json
data/raw/financial_disclosures/rabobank/spike_s0004_multi_findings.json
data/raw/financial_disclosures/spike_s0004_cross_bank_summary.json
```

---

## Cross-Bank Summary

| Bank | Period | Pages | Table pages | Image pages | Primary method |
|---|---|---|---|---|---|
| ANZ | 2025-09-30 | 116 | 69 | 4 | `extract_tables()` |
| ASB | 2025-06-30 | 122 | 81 | 5 | `extract_tables()` |
| BNZ | 2024-09-30 | 98 | 3 | 3 | `extract_text()` |
| Kiwibank | 2024-06-30 | 113 | 79 | 1 | `extract_tables()` |
| Rabobank | 2022-12-31 | 107 | 9 | 5 | `extract_text()` |
| Westpac | 2024-03-31 | -- | -- | -- | NOT ACCESSIBLE |

---

## ANZ (year ended 30 September 2025, 116 pages)

**Source:** `https://www.anz.co.nz/content/dam/anzconz/documents/about-us/disclosure-statements/ANZ-Bank-NZ-Ltd-DS-Sep25.pdf`

**URL discovery:** Navigated `https://www.anz.co.nz/about-us/media-centre/investor-information/` with a
Chrome User-Agent; PDFs are listed directly in the page HTML at the new `anzconz/documents/` DAM path.
Older `anzcoz/` URLs have been removed from the CDN and return 404.

### Structure

`pdfplumber.extract_tables()` found tables on **69 of 116 pages** (59% table-based). The document is
primarily table-driven -- similar to Kiwibank but denser. Key financial statement pages are
readable as text columns.

### Income Statement (page 4)

Machine-readable via `extract_text()`. The statement is fully structured and compact (2 pages total).
FY2025 and FY2024 comparatives are present in a single column layout with NZ$m units:

```
Income Statement
                                                    2025    2024
                                                    NZ$m    NZ$m
Interest income                                   10,532  11,914
Interest expense                                  (5,880) (7,512)
Net interest income                                4,652   4,402
Other operating income                               902     480
Operating income                                   5,554   4,882
Operating expenses                                (1,812) (1,760)
Profit before credit impairment and income tax     3,742   3,122
Credit impairment release/(charge)                    25     (44)
Profit before income tax                           3,767   3,078
Income tax expense                                (1,053)   (870)
Profit for the year                                2,714   2,208
```

The Statement of Comprehensive Income follows immediately on the same page.
Two sparse table objects exist on this page but contain only column header artefacts;
`extract_text()` is the correct extraction method.

### Balance Sheet (page 5)

Machine-readable via `extract_text()`. Full balance sheet with all major line items; FY2025 and
FY2024 comparatives. NZ$m units. One table object exists on this page (38 rows x 5 cols) but
rows are mostly empty -- layout artefact, not data.

Key asset line items:
- Cash and cash equivalents: NZ$9,386m (2025) / NZ$11,634m (2024)
- Net loans and advances: NZ$158,683m / NZ$151,666m
- Total assets: NZ$209,989m / NZ$199,176m

### Cash Flow Statement (page 6)

Machine-readable via `extract_text()`. Direct method; FY2025 and FY2024 comparatives; NZ$m units.
Includes operating, investing, and financing sections.

### Capital Adequacy (pages 56-115+)

The keyword "capital adequacy" appears on 22 pages. The primary Capital Adequacy schedule
begins around pages 56-59, covering:
- CET1, Tier 1, Total Capital ratios
- Risk-weighted assets by exposure class (IRB approach)
- Liquidity ratios
- Leverage ratios

ANZ uses the **Internal Ratings-Based (IRB) approach** for credit risk. The section is extensive
and primarily table-based (part of the 69 table pages). All content is machine-readable.

---

## ASB (year ended 30 June 2025, 122 pages)

**Source:** `https://www.asb.co.nz/content/dam/asb/documents/legal/disclosurestatements/2025/asb-disclosure-statement-and-annual-report-june-2025.pdf`

**URL discovery:** Raw HTML of `https://www.asb.co.nz/legal/disclosure-statements.html` contains all
PDF paths directly embedded in the page source (JavaScript-rendered list, but present in the HTML).
The correct DAM path is `legal/disclosurestatements/`, not the previously assumed
`reports-and-announcements/disclosure-statements/` path (which returns 404 for all periods).

### Structure

`pdfplumber.extract_tables()` found tables on **81 of 122 pages** (66% table-based). Similar layout
density to Kiwibank and ANZ. Key statement pages are readable as text; notes are primarily table-based.

### Income Statement (page 9)

Machine-readable via `extract_text()`. Notably, page 9 is a **five-year Historical Summary**
containing Income Statement, Balance Sheet summary, and Capital data for 2021-2025 in a single
overview page. This is more data-rich than point-in-time statements:

```
Historical Summary of Financial Statements ($ millions, Banking Group)
For the year ended 30 June          2025    2024    2023    2022    2021
Interest income                    7,739   7,568   5,806   3,603   3,528
Interest expense                   4,681   4,640   2,761   1,004   1,141
Net interest income                3,058   2,928   3,045   2,599   2,387
Other income                         444     465     444     585     528
Total operating income             3,502   3,393   3,489   3,184   2,915
Impairment losses/(recoveries)        60      70      64      41      (5)
Total operating expenses           1,427   1,296   1,258   1,108   1,084
Net profit before tax              2,015   2,027   2,167   2,035   1,836
Tax expense                          566     572     608     564     515
Net profit after tax               1,449   1,455   1,559   1,471   1,321
```

The detailed Income Statement is on a separate page later in the document.

### Balance Sheet (page 12)

Machine-readable via `extract_text()`. Standard single-column layout with FY2025 and FY2024
comparatives; NZ$m units.

Key line items:
- Total assets: NZ$135,164m (2025) / NZ$127,089m (2024)
- Net advances to customers: NZ$114,727m / NZ$109,010m

### Cash Flow Statement (page 13)

Machine-readable via `extract_text()`. Indirect method; FY2025 and FY2024 comparatives; NZ$m units.

### Capital Adequacy (pages 65-87+)

The keyword "capital adequacy" appears on 23 pages. The primary Capital Adequacy schedule
begins around pages 65-87, covering:
- CET1, Tier 1, Total Capital ratios and capital adequacy ratios
- Stress testing disclosures
- Risk-weighted assets by exposure class (IRB approach)
- Interest rate risk in the banking book

ASB uses the **Internal Ratings-Based (IRB) approach**. All content is machine-readable via
`extract_tables()` (this section is fully table-based). ASB reports in NZ$ millions.

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

The following bank's PDFs could not be downloaded from the pipeline sandbox:

| Bank | Status | Last confirmed URL |
|---|---|---|
| Westpac | HTTP 403/000 -- WAF blocking | `westpac.co.nz/assets/About-us/...` |

ANZ and ASB have now been resolved by navigating their investor pages in a
browser environment with a Chrome User-Agent to discover the correct CDN paths:

| Bank | Resolved URL pattern |
|---|---|
| ANZ | `anz.co.nz/content/dam/anzconz/documents/about-us/disclosure-statements/ANZ-Bank-NZ-Ltd-DS-{Mon}{YY}.pdf` |
| ASB | `asb.co.nz/content/dam/asb/documents/legal/disclosurestatements/{YYYY}/{filename}.pdf` |

Westpac's WAF continues to block pipeline downloads. The most recent confirmed
URL is a half-year report (March 2024). Westpac remains the only uninspected bank.

---

## Narrative Summary: Financial Statement Comparisons

### Income Statement

All five inspected banks include the following on their income statement page(s):
- Interest income and interest expense (gross)
- Net interest income
- Total operating income
- Operating expenses
- Credit impairment charge / benefit
- Profit before tax
- Income tax expense
- Net profit after tax

**ANZ** provides a clean, compact statement (page 4) in NZD millions with two-year
comparatives. Fully machine-readable via `extract_text()`.

**ASB** provides a five-year historical summary on page 9 (2021-2025 side-by-side),
making it uniquely useful for trend analysis from a single page.

**BNZ** is the most granular on the statement page itself (interest income split
into effective interest + fair value; gains on financial instruments separated).

**Kiwibank** shows only 5 summary line items on the statement page; full detail
requires note traversal.

**Rabobank** is fully granular on the statement page; values are in NZD thousands
(not millions), requiring normalisation.

### Balance Sheet

| Field | ANZ | ASB | BNZ | Kiwibank | Rabobank |
|---|---|---|---|---|---|
| Cash and liquid assets | Yes | Yes | Yes | Note tables | IMAGE-BASED |
| Loans and advances | Yes | Yes | Yes | Note tables | IMAGE-BASED |
| Total assets | Yes | Yes | Yes | Yes | IMAGE-BASED |
| Deposits from customers | Yes | Yes | Yes | Note tables | IMAGE-BASED |
| Total equity | Yes | Yes | Yes | Yes | IMAGE-BASED |

ANZ and ASB both provide complete, machine-readable balance sheets on the
statement page. The Rabobank balance sheet being image-based remains a
significant gap for that bank.

### Cash Flow Statement

All five banks provide net cash flows from operating, investing, and financing
activities. ANZ, ASB, BNZ, and Rabobank provide detailed cash flow line items on the
statement page; Kiwibank provides only summary subtotals.

### Capital Adequacy

All five inspected banks provide:
- CET1, Tier 1, and Total Capital ratios
- Required capital ratios (RBNZ BPR minimums)
- Capital surplus vs requirements

**ANZ, ASB, BNZ, and Kiwibank** use the **Internal Ratings-Based (IRB) approach**
(more granular, risk-weighted by internal models). **Rabobank** uses the
**Standardised Approach** (exposure class averages). Cross-bank capital comparison
requires acknowledging this methodological difference.

---

## Updated Recommendation: Extraction Approach for W-0015

**Recommendation: Hybrid extraction -- `extract_tables()` primary, `extract_text()` fallback.**

This approach is confirmed by all five inspected banks:
1. ANZ (69/116 table pages), ASB (81/122 table pages), and Kiwibank (79/113 table pages)
   are predominantly table-based; `extract_text()` alone would miss their note tables.
2. BNZ and Rabobank use text columns on statement pages; `extract_tables()` finds only 3
   and 9 tables respectively -- the primary financial statements require `extract_text()`.
3. Statement header pages (Income Statement, Balance Sheet, Cash Flow) are universally
   readable via `extract_text()` regardless of the bank's overall extraction method.
4. The Rabobank Balance Sheet is image-based -- log WARNING and store null until OCR is
   adopted if needed.

**Decision confirmed:** With ANZ and ASB now inspected (the two largest NZ banks by assets),
the hybrid `extract_tables()` + `extract_text()` approach is validated across all accessible
banks. This decision can support W-0015 implementation. Only Westpac remains uninspected.

No new dependencies are required beyond `pdfplumber` (already in `pyproject.toml`).
If Rabobank or Westpac require OCR for image-based pages, add `pytesseract` or
`pdfminer.six` at that point and open ADR-0005.

---

## Open Questions and Risks

- ~~**ANZ and ASB not inspected**~~ -- **RESOLVED** (2026-04-29). ANZ (116 pages,
  69 table pages) and ASB (122 pages, 81 table pages) both use the `extract_tables()`
  primary method. All four key financial statements are machine-readable. URLs were
  discovered by navigating the banks' investor pages with a Chrome User-Agent and are
  now confirmed in `config/sources.yaml`.

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
