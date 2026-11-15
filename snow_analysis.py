"""Descriptive snow analysis. No network calls or personal filesystem paths.

Original FMI fields are retained. Derived fields have names and units that
distinguish snow on the ground from measured fresh snowfall.
"""
from pathlib import Path
import calendar
import numpy as np
import pandas as pd

WINTER_MONTHS = [10, 11, 12, 1, 2, 3, 4]
MONTH_LABELS = [calendar.month_abbr[m] for m in WINTER_MONTHS]
WEATHER_COLUMNS = ["Snow depth [cm]", "Average temperature [°C]",
                   "Precipitation amount [mm]", "Maximum temperature [°C]",
                   "Minimum temperature [°C]"]


def find_project_root(start=None):
    """Find the included data from the project root or any subfolder."""
    start = Path(start or Path.cwd()).resolve()
    for candidate in [start, *start.parents]:
        if (candidate / "data/raw/oulu_kaukovainio_daily.xlsx").is_file():
            return candidate
    raise FileNotFoundError("Run from the extracted/cloned repository. See README.md.")


def clean_observations(raw):
    """Validate the single-station input, without dropping missing observations.

    Only '-' is interpreted as a missing-value marker. Unexpected text raises
    an error, so a misspelt number cannot silently disappear from the analysis.
    """
    required = ["Observation station", "Year", "Month", "Day", *WEATHER_COLUMNS]
    missing = sorted(set(required) - set(raw.columns))
    if missing:
        raise ValueError(f"Required columns missing: {missing}")
    if raw.empty:
        raise ValueError("No observations provided.")
    data = raw.copy(deep=True)
    stations = data["Observation station"].dropna().unique()
    if len(stations) != 1 or data["Observation station"].isna().any():
        raise ValueError("Expected exactly one named station; analyse multiple stations separately.")
    parts = data[["Year", "Month", "Day"]].apply(pd.to_numeric, errors="raise")
    if parts.isna().any().any() or not parts.eq(parts.round()).all().all():
        raise ValueError("Year, Month and Day must be non-missing integers.")
    data[parts.columns] = parts.astype(int)
    data["Date"] = pd.to_datetime(parts.rename(columns=str.lower), errors="raise")
    if data["Date"].duplicated().any():
        raise ValueError("Duplicate station dates found; resolve them before computing daily changes.")
    for column in WEATHER_COLUMNS:
        data[column] = pd.to_numeric(data[column].mask(data[column].eq("-")), errors="raise")
        if np.isinf(data[column].dropna()).any():
            raise ValueError(f"Infinite values in {column}.")
    for column in ["Snow depth [cm]", "Precipitation amount [mm]"]:
        invalid = data[column].lt(0) & data[column].ne(-1)
        if invalid.any():
            raise ValueError(f"Unexpected negative value in {column}; only -1 is an FMI sentinel.")
    inverted = data["Minimum temperature [°C]"] > data["Maximum temperature [°C]"]
    if inverted.any():
        raise ValueError("Minimum temperature exceeds maximum temperature.")
    data["Snow_depth_cm"] = data["Snow depth [cm]"].replace(-1, 0)
    data["Precipitation_mm"] = data["Precipitation amount [mm]"].replace(-1, 0)
    data["All_weather_missing"] = data[WEATHER_COLUMNS].isna().all(axis=1)
    start_year = data["Date"].dt.year.where(data["Date"].dt.month >= 10, data["Date"].dt.year - 1)
    data["Winter"] = start_year.astype(str) + "-" + (start_year + 1).astype(str)
    return data.sort_values("Date").reset_index(drop=True)


def select_window(data, start="10-01", end="04-30"):
    """Select a calendar window, retaining partially missing weather rows.

    All-weather-missing rows are excluded from analysis but kept in the input
    to coverage_audit. The first selected day has no change within this window.
    """
    for boundary in [start, end]:
        if pd.to_datetime("2000-" + boundary, format="%Y-%m-%d").strftime("%m-%d") != boundary:
            raise ValueError("Window boundaries must use MM-DD format.")
    key = data["Date"].dt.strftime("%m-%d")
    mask = ((key >= start) | (key <= end)) if start > end else ((key >= start) & (key <= end))
    selected = data.loc[mask & data["Date"].dt.month.isin(WINTER_MONTHS) & ~data["All_weather_missing"]].copy()
    if selected.empty:
        raise ValueError("No usable observations in the selected winter window.")
    return add_daily_metrics(selected)


def add_daily_metrics(data):
    """Never bridge missing calendar days, winter boundaries or missing snow."""
    data = data.sort_values("Date").copy().reset_index(drop=True)
    if data["Date"].duplicated().any():
        raise ValueError("Duplicate dates would make daily changes ambiguous.")
    snow = data["Snow_depth_cm"]
    data["Snow_covered"] = snow.ge(1).astype("boolean").where(snow.notna())
    gaps = data.groupby("Winter")["Date"].diff().dt.days
    change = data.groupby("Winter")["Snow_depth_cm"].diff()
    data["Depth_change_cm"] = change.where(gaps.eq(1))
    data["Depth_increased"] = data["Depth_change_cm"].gt(0).astype("boolean").where(data["Depth_change_cm"].notna())
    return data


def summarize(data, groups=("Winter",)):
    """Use separate, valid denominators for snow cover and depth changes."""
    summary = data.groupby(list(groups)).agg(
        Rows=("Date", "size"),
        Valid_snow_days=("Snow_depth_cm", "count"),
        Snow_covered_days=("Snow_covered", lambda x: x.sum(min_count=1)),
        Mean_depth_cm=("Snow_depth_cm", "mean"),
        Median_depth_cm=("Snow_depth_cm", "median"),
        Maximum_depth_cm=("Snow_depth_cm", "max"),
        Valid_comparisons=("Depth_change_cm", "count"),
        Increase_days=("Depth_increased", lambda x: x.sum(min_count=1)),
        Maximum_increase_cm=("Depth_change_cm", "max"),
    )
    summary["Snow_cover_pct"] = 100 * summary["Snow_covered_days"] / summary["Valid_snow_days"].replace(0, np.nan)
    summary["Increase_pct"] = 100 * summary["Increase_days"] / summary["Valid_comparisons"].replace(0, np.nan)
    return summary


def coverage_audit(data):
    """Measure coverage against every expected October–April date.

    Distinguishes absent dates from present rows whose snow measurement is
    missing. A zero reading is a valid observation, not missing data.
    """
    winter_data = data.loc[data["Date"].dt.month.isin(WINTER_MONTHS)]
    rows = []
    for winter, group in winter_data.groupby("Winter"):
        year = int(winter.split("-")[0])
        for month in WINTER_MONTHS:
            actual_year = year if month >= 10 else year + 1
            expected = calendar.monthrange(actual_year, month)[1]
            actual = group.loc[group["Date"].dt.month.eq(month)]
            valid = int(actual["Snow_depth_cm"].notna().sum())
            rows.append({"Winter": winter, "Month": month, "Expected_days": expected,
                         "Rows_present": len(actual), "Absent_dates": expected - len(actual),
                         "Missing_snow_rows": int(actual["Snow_depth_cm"].isna().sum()),
                         "Valid_snow_days": valid, "Coverage_pct": 100 * valid / expected})
    return pd.DataFrame(rows)


def threshold_sensitivity(data, thresholds=(1, 3, 5)):
    """Exploratory depth thresholds, not official snow-clearing triggers."""
    if not thresholds or any(not np.isfinite(t) or t <= 0 for t in thresholds):
        raise ValueError("Thresholds must be finite positive numbers.")
    rows = []
    for winter, group in data.groupby("Winter"):
        changes = group["Depth_change_cm"].dropna()
        for threshold in sorted(set(thresholds)):
            count = int(changes.ge(threshold).sum()) if len(changes) else np.nan
            rows.append({"Winter": winter, "Threshold_cm": threshold,
                         "Valid_comparisons": len(changes), "Days": count,
                         "Percent": 100 * count / len(changes) if len(changes) else np.nan})
    return pd.DataFrame(rows)


def increase_magnitudes(data):
    """Describe positive changes separately from their frequency per valid day."""
    rows = []
    for winter, group in data.groupby("Winter"):
        changes = group["Depth_change_cm"].dropna()
        positive = changes[changes.gt(0)]
        for label, low, high in [("0 to <3 cm", 0, 3), ("3 to <5 cm", 3, 5), ("≥5 cm", 5, np.inf)]:
            count = int((positive.ge(low) & positive.lt(high)).sum())
            rows.append({"Winter": winter, "Magnitude": label, "Days": count,
                         "Positive_change_days": len(positive),
                         "Share_of_positive_changes_pct": 100 * count / len(positive) if len(positive) else np.nan})
    return pd.DataFrame(rows)


def export_tables(tables, output_dir):
    """Save the same tables to Excel and CSV, without rounding stored values."""
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    path = output_dir / "DABI_Oulu_Snow_Analysis.xlsx"
    with pd.ExcelWriter(path, engine="openpyxl") as writer:
        for name, table in tables.items():
            indexed = not isinstance(table.index, pd.RangeIndex)
            table.to_excel(writer, sheet_name=name, index=indexed)
            if name != "Original_dataset":
                table.to_csv(output_dir / (name.lower() + ".csv"), index=indexed)
    return path
