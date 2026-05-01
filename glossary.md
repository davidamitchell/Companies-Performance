# Glossary

Foundational definitions for all metrics tracked in this repository. All metric names used in code, configuration, and data files must match these definitions verbatim.

---

## Financial Resilience

Metrics measuring capital adequacy, liquidity, and asset quality.

### CET1 Ratio
**Common Equity Tier 1 Ratio.** The ratio of a bank's Common Equity Tier 1 capital to its risk-weighted assets. Measures the core capital buffer available to absorb losses. Expressed as a percentage.

### Total Risk-Weighted Assets
Total assets adjusted for credit, market, and operational risk weights as defined by RBNZ prudential standards. The denominator for CET1 Ratio and RORWA. Expressed in NZDm. RBNZ series `DBB.QIB90`.

### RORWA
**Return on Risk-Weighted Assets.** Annualised Profit After Tax divided by Total Risk-Weighted Assets. Capital-structure-neutral profitability metric: unlike ROE, it is not affected by leverage decisions. Expressed as a percentage. Derived client-side; not stored (ADR-0001).

### Risk Density
Total Risk-Weighted Assets divided by Net Loans and Advances. Measures the average risk weight of the loan book. A rising density indicates portfolio mix is shifting toward higher-risk exposures. Expressed as a percentage. Derived client-side; not stored (ADR-0001).

### Individual Provisions
Specific loan loss provisions set against individually identified impaired loans. Measured by the bank's credit team on a case-by-case basis. Expressed in NZDm. RBNZ series `DBB.QIC60`.

### Collective Provisions
General loan loss provisions held against the performing loan portfolio as a buffer against unidentified losses. Expressed in NZDm. RBNZ series `DBB.QIC70`.

### Provisioning Coverage
Total provisions (Individual + Collective) divided by Total Non-Performing Loans. Measures the adequacy of reserves against known bad loans. A ratio above 100% means provisions exceed non-performing loans. Expressed as a percentage. Derived client-side; not stored (ADR-0001).

### Provision Charge
The quarterly change in total provisions (Individual + Collective), expressed as a percentage of Net Loans and Advances. The primary credit cycle indicator: spikes in downturns when banks front-load expected losses, and negative in recoveries when provisions are released. Derived client-side; not stored (ADR-0001).

### LCR
**Liquidity Coverage Ratio.** The ratio of high-quality liquid assets to net cash outflows over a 30-day stress period. Measures short-term liquidity resilience. Expressed as a percentage; regulatory minimum is 100%.

### Cash Position
The absolute level of cash and cash equivalents held by an institution. Expressed in the reporting currency (NZD millions unless otherwise specified).

### SBC
**Share-Based Compensation.** The expense recognised for equity instruments granted to employees. Relevant for assessing non-cash compensation costs. Expressed in the reporting currency.

### NPL Ratio
**Non-Performing Loan Ratio.** The ratio of non-performing loans (loans 90+ days past due or impaired) to total gross loans. Measures asset quality. Expressed as a percentage.

### Provisioning Coverage
The ratio of loan loss provisions to non-performing loans. Measures the adequacy of reserves against expected credit losses. Expressed as a percentage.

---

## Growth Momentum

Metrics measuring revenue growth, customer expansion, and commercial velocity.

### CRPO
**Current Remaining Performance Obligations.** The portion of contracted revenue expected to be recognised within the next 12 months. Indicates near-term revenue visibility.

### Contract Backlog
Total value of signed contracts not yet recognised as revenue. A forward-looking indicator of revenue momentum.

### NIM
**Net Interest Margin.** The difference between interest income earned and interest paid out, expressed as a percentage of average earning assets. Core profitability metric for banks.

### Rule of 40
The sum of revenue growth rate and EBITDA margin. A combined efficiency and growth metric for SaaS and high-growth companies. A score above 40 indicates healthy balance between growth and profitability.

### Operating Margin
Operating income as a percentage of revenue. Measures operational efficiency before interest and taxes.

### High-Value Customer Growth
Year-on-year growth rate in the count or revenue contribution of customers above a defined value threshold (definition varies by source). Measures the quality of the customer base expansion.

---

## Structural Moat

Metrics measuring customer retention, competitive positioning, and business durability.

### Renewal Rate
The percentage of expiring contracts or subscriptions that are renewed. Measures customer retention and product stickiness.

### NDR
**Net Dollar Retention (also Net Revenue Retention, NRR).** Revenue retained from existing customers including expansions, contractions, and churn, divided by starting-period revenue. A rate above 100% indicates net expansion. Expressed as a percentage.

### Cohort Maturity
A qualitative or quantitative assessment of how a customer cohort's revenue contribution evolves over time. Used to assess whether early cohorts are expanding or contracting.

### Core Funding Ratio (CFR)
**Core Funding Ratio.** The ratio of stable funding sources (retail deposits, long-term wholesale) to total loans and advances. A New Zealand regulatory metric. Higher is more stable. Expressed as a percentage.

### 1-Month Mismatch Ratio
The ratio of a bank's 1-month cumulative net cash position to its total liabilities, per RBNZ liquidity policy (BS13). Measures short-term funding resilience over a one-month horizon. Expressed as a percentage. RBNZ series `DBB.QIH10`.

### 1-Week Mismatch Ratio
The ratio of a bank's 1-week cumulative net cash position to its total liabilities, per RBNZ liquidity policy (BS13). Measures short-term funding resilience over a one-week horizon. Expressed as a percentage. RBNZ series `DBB.QIH20`.

### Top 5 Non-Bank Credit Exposures
The sum of the five largest non-bank credit exposures as a percentage of the bank's CET1 capital. Measures single-borrower concentration risk in the non-bank lending book. Expressed as a percentage of CET1. RBNZ series `DBB.QIJ10`.

### Top 5 Bank Credit Exposures
The sum of the five largest interbank credit exposures as a percentage of the bank's CET1 capital. Measures interbank counterparty concentration risk. Expressed as a percentage of CET1. RBNZ series `DBB.QIJ30`.

### Bank Exposures ≥10% of CET1
The total of all interbank credit exposures that individually exceed 10% of the bank's CET1 capital. Identifies material single-counterparty interbank concentrations. Expressed as a percentage of CET1. RBNZ series `DBB.QIJ40`.

---

## Strategic Evolution

Metrics measuring the trajectory of product mix, technology adoption, and competitive displacement.

### AI ACV
**AI Annual Contract Value.** The annualised contracted value of AI-specific products or features. Measures the monetisation rate of AI capabilities.

### Product Mix
The distribution of revenue across product lines or categories. Tracks shifts in revenue composition over time.

### Competitive Displacement
A qualitative or quantitative measure of wins against named competitors. Indicates market share momentum.

### Cost of Intelligence
The total cost of AI infrastructure, model usage, and associated labour as a proportion of revenue or gross margin. An emerging metric for AI-enabled businesses tracking unit economics of intelligence delivery.

---

## RBNZ Dashboard — Additional Metrics

Metrics sourced from the RBNZ Bank Financial Strength Dashboard that supplement the core glossary definitions above. All values are as reported by the RBNZ; monetary values are in NZD millions (NZDm) unless otherwise stated.

### Total Capital Ratio
The ratio of total regulatory capital (Tier 1 + Tier 2) to risk-weighted assets. The broadest capital adequacy measure. Expressed as a percentage. RBNZ series C1.

### Tier 1 Capital Ratio
The ratio of Tier 1 capital (CET1 + Additional Tier 1) to risk-weighted assets. Expressed as a percentage. RBNZ series C3.

### Total Non-Performing Loans
The sum of impaired loans and loans 90+ days past due but not yet impaired. Expressed in NZDm. RBNZ series F4 (total loan portfolio).

### Return on Assets
Annualised profit after tax divided by average total assets. Expressed as a percentage. RBNZ series P1.

### Return on Equity
Annualised profit after tax divided by average equity. Expressed as a percentage. RBNZ series P2.

### Net Interest Income
Interest income less interest expense. Core revenue line for a bank. Expressed in NZDm. RBNZ series Q3.

### Operating Expenses
Total non-interest operating expenses (staff, technology, premises, etc.). Expressed in NZDm. RBNZ series Q7.

### Profit After Tax
Net profit after all expenses and tax. Bottom-line earnings measure. Expressed in NZDm. RBNZ series Q11.

### Total Assets
Total balance sheet assets. Expressed in NZDm. RBNZ series R1.

### Net Loans and Advances
Gross loans less loan loss provisions. Primary earning asset for banks. Expressed in NZDm. RBNZ series R4.

### Deposits
Customer and institutional deposits — the primary funding source. Expressed in NZDm. RBNZ series R9.

### Equity
Total shareholders' equity (residual interest). Expressed in NZDm. RBNZ series R14.

### Trading and Hedging Gains
Net gains and losses on trading and hedging activities. Expressed in NZDm. RBNZ series Q4.

### Fees and Commission Income
Net fees and commissions earned from banking services. Expressed in NZDm. RBNZ series Q5.

### Other Income
All other operating income not captured in interest income, trading gains, or fees. Expressed in NZDm. RBNZ series Q6.

### Cost to Income Ratio
Total operating expenses divided by total operating income (Net Interest Income + Trading and Hedging Gains + Fees and Commission Income + Other Income). Measures operational efficiency. Lower is more efficient. Expressed as a percentage. **Derived from RBNZ series Q7 ÷ (Q3 + Q4 + Q5 + Q6); computed in the frontend, not stored in canonical data files (see ADR-0001).**

### OCR Rate
**Official Cash Rate.** The wholesale interest rate set by the Reserve Bank of New Zealand (RBNZ) at each Monetary Policy Committee meeting. It is the primary monetary policy instrument and directly influences short-term borrowing and deposit rates across the economy. Expressed as a percentage per annum. Published by the RBNZ.

---
