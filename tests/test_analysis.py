"""Small synthetic datasets test the assumptions that could change the findings."""
import unittest
import numpy as np
import pandas as pd
from pandas.testing import assert_frame_equal
from snow_analysis import (WEATHER_COLUMNS, clean_observations, select_window,
                           summarize, coverage_audit, threshold_sensitivity)


def raw_frame(dates, snow):
    dates = pd.to_datetime(dates)
    return pd.DataFrame({"Observation station": "Test station", "Year": dates.year,
        "Month": dates.month, "Day": dates.day, "Snow depth [cm]": snow,
        "Average temperature [°C]": -1.0, "Precipitation amount [mm]": -1.0,
        "Maximum temperature [°C]": 1.0, "Minimum temperature [°C]": -3.0})


class TestSnowAnalysis(unittest.TestCase):
    def test_sentinels_and_original_are_preserved(self):
        raw = raw_frame(["2024-01-01", "2024-01-02", "2024-01-03"], [-1, 0, "-"])
        before = raw.copy(deep=True)
        cleaned = clean_observations(raw)
        assert_frame_equal(raw, before)
        self.assertEqual(cleaned["Snow_depth_cm"].iloc[:2].tolist(), [0, 0])
        self.assertTrue(pd.isna(cleaned["Snow_depth_cm"].iloc[2]))
        self.assertTrue(cleaned["Average temperature [°C]"].eq(-1).all())

    def test_changes_do_not_bridge_gaps_missing_snow_or_winters(self):
        raw = raw_frame(["2024-04-28", "2024-04-29", "2024-10-01", "2024-10-03", "2024-10-04", "2024-10-05", "2024-10-06"], [2, 5, 8, 10, "-", 15, 17])
        changes = select_window(clean_observations(raw))["Depth_change_cm"]
        self.assertEqual(changes.dropna().tolist(), [3, 2])
        self.assertTrue(changes.iloc[[0, 2, 3, 4, 5]].isna().all())

    def test_missing_is_not_no_snow_or_no_increase(self):
        data = select_window(clean_observations(raw_frame(["2024-01-01", "2024-01-02", "2024-01-03"], [0, "-", 4])))
        result = summarize(data).iloc[0]
        self.assertEqual(result["Valid_snow_days"], 2)
        self.assertEqual(result["Snow_cover_pct"], 50)
        self.assertEqual(result["Valid_comparisons"], 0)
        self.assertTrue(pd.isna(result["Increase_pct"]))
        self.assertTrue(pd.isna(result["Increase_days"]))

    def test_common_window_recomputes_first_day(self):
        cleaned = clean_observations(raw_frame(["2024-11-09", "2024-11-10", "2024-11-11"], [0, 5, 6]))
        selected = select_window(cleaned, start="11-10")
        self.assertTrue(pd.isna(selected["Depth_change_cm"].iloc[0]))
        self.assertEqual(selected["Depth_change_cm"].iloc[1], 1)

    def test_all_missing_row_stays_in_audit_but_leaves_analysis(self):
        raw = raw_frame(["2024-01-01", "2024-01-02", "2024-01-03"], [0, "-", 5])
        raw[WEATHER_COLUMNS] = raw[WEATHER_COLUMNS].astype(object)
        raw.loc[1, WEATHER_COLUMNS] = "-"
        cleaned = clean_observations(raw)
        self.assertEqual(len(cleaned), 3)
        self.assertEqual(cleaned["All_weather_missing"].sum(), 1)
        selected = select_window(cleaned)
        self.assertEqual(len(selected), 2)
        self.assertTrue(selected["Depth_change_cm"].isna().all())

    def test_numeric_date_strings_are_normalized(self):
        raw = raw_frame(["2024-01-01"], [2])
        raw[["Year", "Month", "Day"]] = raw[["Year", "Month", "Day"]].astype(str)
        cleaned = clean_observations(raw)
        self.assertEqual(cleaned["Month"].iloc[0], 1)

    def test_coverage_includes_leap_day_and_unobserved_months(self):
        cleaned = clean_observations(raw_frame(["2024-02-28", "2024-02-29"], [0, "-"]))
        audit = coverage_audit(cleaned).set_index("Month")
        self.assertEqual(audit.loc[2, "Expected_days"], 29)
        self.assertEqual(audit.loc[2, "Absent_dates"], 27)
        self.assertEqual(audit.loc[2, "Missing_snow_rows"], 1)
        self.assertEqual(audit.loc[2, "Valid_snow_days"], 1)
        self.assertEqual(audit.loc[10, "Absent_dates"], 31)

    def test_threshold_boundaries_and_denominator(self):
        data = select_window(clean_observations(raw_frame(pd.date_range("2024-01-01", periods=5), [0, 1, 4, 9, 9])))
        result = threshold_sensitivity(data)
        self.assertEqual(result["Days"].tolist(), [3, 2, 1])
        self.assertEqual(result["Percent"].tolist(), [75, 50, 25])
        with self.assertRaises(ValueError): threshold_sensitivity(data, [0])

    def test_bad_data_is_rejected_instead_of_silently_dropped(self):
        for snow in [[-2], ["typo"], [np.inf]]:
            with self.subTest(snow=snow):
                with self.assertRaises(ValueError):
                    clean_observations(raw_frame(["2024-01-01"], snow))
        duplicate = raw_frame(["2024-01-01", "2024-01-01"], [1, 2])
        with self.assertRaises(ValueError): clean_observations(duplicate)
        multi = raw_frame(["2024-01-01", "2024-01-02"], [1, 2])
        multi.loc[1, "Observation station"] = "Other station"
        with self.assertRaises(ValueError): clean_observations(multi)


if __name__ == "__main__":
    unittest.main()
