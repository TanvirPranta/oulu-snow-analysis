# Data provenance

Provider: Finnish Meteorological Institute (FMI). Station: Oulu Kaukovainio.
Source: https://en.ilmatieteenlaitos.fi/download-observations
Licence: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/), per
https://en.ilmatieteenlaitos.fi/open-data-licence . No FMI endorsement is implied.

The user downloaded this daily-observation Excel snapshot for the requested interval
2016-10-01 to 2026-04-30. The actual file has 904 rows, 2023-11-09 to 2026-04-30.
The exact download timestamp is not recorded. The first row has no weather observations.

`raw/oulu_kaukovainio_daily.xlsx` is byte-for-byte unchanged; only the copied filename is shorter.
Original filename: `Oulu Kaukovainio_ 1.10.2016 - 30.4.2026_16aba4e5-621d-47b6-880c-079f695fb82f.xlsx`.
SHA-256: `a9810a77f5725dc9ceb78ba96ca05bb35a7e0d6e6836e98a1b3dee719218f895`

Derived files in `outputs/` replace missing markers with nulls, remove the all-weather-missing row,
select October–April, convert the snow/precipitation -1 codes to zero in separate columns,
and calculate the metrics described in the notebook. Original columns are retained.
Negative temperatures are not replaced. Raw zero precipitation is a trace (<0.1 mm),
approximated as zero in the processed column. Snow depth is not snowfall.
