# Version 2

- Split calculation and plotting logic into `snow_analysis.py` and `snow_charts.py`; the notebook walks through the analysis with explanations and visible results.
- Added strict input validation and nine focused tests. Missing values stay distinct from genuine zeros.
- Added a monthly and seasonal coverage audit against the full October–April calendar, including leap years.
- Used the same 10 November–30 April window for the main between-winter and threshold comparisons. Full available-window tables remain available.
- Added a chart of positive-change magnitudes, making its denominator explicit.
- Kept original input bytes unchanged. Regenerated Excel, CSV, PNG and HTML outputs from the notebook.
- Preserved the original business scope: a descriptive opportunity assessment, not a forecast or a complete business plan.

## Reading this project

Start with the notebook and `ASSESSMENT.md`. Read `snow_analysis.py` for the calculations, and `tests/test_analysis.py` for examples of how missing or invalid inputs are handled. The notebook requires the complete repository, including the two Python modules and data folder; uploading only the notebook is insufficient.
