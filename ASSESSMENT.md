# Assessment of the snow-clearing opportunity

## What the original results support

Across the available winter periods, the station recorded 45, 43 and 34 positive daily snow-depth changes. This establishes recurring conditions worth investigating for a snow-clearing service, but does not establish demand for paid services. Existing snow cover and fresh accumulation are different quantities, and neither can be directly converted into customer visits.

## Added assessment 1: compare the same calendar window

The full-window increase percentages were 26.2%, 20.4% and 16.1%, but the first winter lacks October and early November. Recomputing each winter from **10 November to 30 April** gives:

| Winter | Observed days | Snow-covered days | Snow-covered share | Valid daily comparisons | Increase days | Increase share |
|---|---:|---:|---:|---:|---:|---:|
| 2023–2024 | 173 | 170 | 98.3% | 172 | 45 | 26.2% |
| 2024–2025 | 172 | 117 | 68.0% | 171 | 43 | 25.1% |
| 2025–2026 | 172 | 114 | 66.3% | 171 | 34 | 19.9% |

February 2024 has an additional day; percentages use the observed denominator for each winter. The first day in each window is excluded from change calculations.

**Interpretation:** The difference in increase frequency between the first two winters becomes much smaller (about 1.0 percentage point using unrounded rates) once their calendar coverage is aligned. This demonstrates why the original unequal windows must be disclosed. Snow cover was much more persistent in the first observed winter, even after aligning dates. Three seasons still cannot establish a long-term trend.

## Added assessment 2: sensitivity to larger increases

Using the same **10 November–30 April** window in every winter:

| Minimum daily depth increase | 2023–24 | 2024–25 | 2025–26 |
|---|---:|---:|---:|
| At least 1 cm | 45 days (26.2%) | 43 days (25.1%) | 34 days (19.9%) |
| At least 3 cm | 17 days (9.9%) | 14 days (8.2%) | 18 days (10.5%) |
| At least 5 cm | 9 days (5.2%) | 7 days (4.1%) | 6 days (3.5%) |

**Interpretation:** Frequency depends strongly on the threshold. Of the positive-change days, 28/45, 29/43 and 16/34 had increases below 3 cm. Therefore, describing every small increase as a significant service event would overstate the evidence. The 2025–26 season had fewer positive-change days overall than 2024–25, but more days reaching at least 3 cm. A single event count does not describe the entire distribution of changes.

These 1/3/5 cm thresholds are illustrative. They are not official operational triggers, proof that smaller increases are errors, or measurements of actual snowfall. All three winters have complete readings in this narrower window, with one additional leap day in 2023–24. Available October–April sensitivity results remain separately exported in `outputs/sensitivity_available.csv`.

## Added assessment 3: data coverage and event magnitudes

The full 2023–24 October–April window contains 213 calendar days. The file contains 174 rows in that window: 39 dates are absent and one present row has no snow reading. There are therefore 173 valid snow days, or 81.2% coverage. Both later windows have 212 valid readings out of 212 expected dates. A valid zero is counted as a measurement, never as missing data.

Within the common window, positive changes below 3 cm make up 62.2%, 67.4% and 47.1% of positive-change days. Changes of 3 to below 5 cm account for 8, 7 and 12 days; changes of at least 5 cm account for 9, 7 and 6 days. This separates change size from event frequency. It does not turn those changes into independently verified snowfall events or actual service calls.

No significance test treating the daily observations as independent winters is applied. The daily series is temporally dependent and only three winters are available. Descriptive rates and sensitivity checks are a better fit for the evidence than a confident trend or demand forecast.

## Business recommendation

The opportunity is **conditionally promising enough to investigate**, especially for an existing maintenance provider. Before investment, gather evidence on unmet residential demand, willingness to pay, competition, property-specific clearing requirements and delivery costs. Link actual service records with local weather if possible. No revenue, market-size or profitability estimate is supported by the current dataset.

## What changed in the portfolio edition

- Portable data and output paths; no Drive mounting or personal absolute paths.
- Original input workbook included unchanged, with FMI attribution and checksum.
- Missing-marker conversion avoids the earlier pandas downcasting warning.
- `snow_accumulation` renamed `Snow_covered` to reflect its actual meaning; duplicated assignment removed.
- Corrected quote usage so the notebook also parses on Python versions before 3.12.
- Added common-calendar comparison, threshold sensitivity and offline interactive chart.
- Refactored validation, calculations and plotting into documented reusable functions.
- Added nine synthetic edge-case tests, plus snapshot assertions for the original results and calendar coverage.
- Added an increase-magnitude chart and calendar-based missing-data audit.
- Aligned the main threshold comparison to the common date window; retained the original available-window sensitivity separately.
- Exported new assessments alongside the original data and summaries to Excel and CSV.

Source: [FMI daily observations](https://en.ilmatieteenlaitos.fi/download-observations), supplied Oulu Kaukovainio snapshot. See [data provenance](data/README.md). AI assisted with this portfolio expansion; the original submitted notebook is not overwritten.
