# ADR-0007: Strategy Scorecard — Per-Bank Comparison over Sector Average

Date: 2026-05-03
Status: Accepted

## Context

The Strategy Scorecard tab (W-0096) was first described in the Phase 20 backlog decomposition
(PR #35). The original design showed a single aggregated value per metric — the average across
all selected banks. A subsequent review identified that averaging across selected organisations
eliminates the ability to compare distinct performances, directly contradicting the rest of the
dashboard which is built around side-by-side bank comparisons.

The core problem: given five selected banks and a metric like NPL Ratio, an average of
{1.2%, 1.5%, 0.8%, 2.1%, 0.9%} = 1.3% tells you nothing about which banks are performing
well or poorly. The average destroys the comparative signal.

Two design options were considered:

**Option A: Grouped bar chart per metric (Chart.js)**
Render a small Chart.js grouped bar chart for each metric in a pillar card, one bar per bank,
coloured by bank colour.

*Pros*: Visually impactful, instantly comparable.
*Cons*: Requires canvas per metric (large DOM for 19 metrics across 5 pillars), destroys and
recreates charts on every re-render, increases JS complexity, and makes the print stylesheet
difficult to manage. The existing tab-chart rendering already provides this at metric granularity.

**Option B: Per-bank row table within each pillar card (chosen)**
For each metric inside a pillar card, render one row per selected bank showing: bank colour
swatch, bank name, latest value, QoQ trend arrow (colour-coded by good-direction), and a small
inline bar showing position relative to the min–max range across selected banks.

*Pros*: No additional Chart.js instances. Scannable at a glance. Aligns with the site's existing
design language (swatches + coloured trend arrows). Print-friendly (pure HTML). Degrades
gracefully to a single-bank view when only one bank is selected (shows peer-relative bar
against all banks in the dataset). Low JS complexity.
*Cons*: Bars are proportional, not absolute — two metrics on different scales cannot be
compared. This is acceptable because the pillar card groups metrics that are conceptually
related, not numerically comparable anyway.

## Decision

Implement Option B (per-bank row table).

When **one bank is selected**, each metric row shows: metric name | QoQ trend | value | peer
percentile bar (relative to all banks in the dataset) | lead/lag badge.

When **multiple banks are selected**, each metric becomes a section header, followed by one
bank row per selected bank: colour swatch | bank name | value | QoQ trend | mini bar (relative
to min–max of selected banks).

The `scorecard` tab is added to the `TABS` constant with a `null` value (no standard metric
list), matching the pattern used by `productivity`. `renderCharts()` dispatches to the dedicated
`renderScorecard()` function when `activeTab === 'scorecard'`. `KEY_METRICS` is derived from
`Object.values(TABS).filter(Boolean).flat()` so the null entry is excluded.

## Consequences

### Positive
- Each selected bank's performance is always individually visible — the scorecard now supports
  the same comparative use case as every other tab.
- Single-bank mode retains the peer-relative view, making it useful for both contexts.
- No new external dependencies introduced.
- Export CSV (W-0097) exports per-bank rows, so the downloaded file is equally comparable.

### Negative / Trade-offs
- Mini bars within a pillar card are relative to the selected banks' range, not the full
  dataset range. If only high-performing banks are selected, all bars appear full. This is a
  known limitation of relative positioning but is consistent with how the rest of the dashboard
  filters by selection.

### Neutral
- `config/strategy_pillars.yaml` is the authoritative source for pillar definitions. The JS
  constant `STRATEGY_PILLARS` in `docs/index.html` is inlined for static-site delivery and must
  be kept in sync manually when the YAML changes.
