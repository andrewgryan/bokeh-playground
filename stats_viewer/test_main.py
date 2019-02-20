# pylint: disable=missing-docstring, invalid-name
import unittest
import datetime as dt
import netCDF4
import numpy as np
import main
import os


class TestStatsViewer(unittest.TestCase):
    def test_read_forecasts(self):
        with netCDF4.Dataset("test-read-forecasts.nc",
                             mode="w", diskless=True) as dataset:
            dataset.createDimension("forecasts", 2)
            var = dataset.createVariable(
                "forecasts", "f", ("forecasts",))
            var[:] = [12., 36.]
            result = main.read_forecasts(dataset)
            expect = np.array([12, 36], dtype="f")
            np.testing.assert_array_equal(expect, result)

    def test_read_forecast_names(self):
        forecast_names = np.array(["forecast", "persistence"], dtype="S64")
        with netCDF4.Dataset("test-read-forecasts.nc",
                             mode="w", diskless=True) as dataset:
            dataset.createDimension("forecasts", len(forecast_names))
            dataset.createDimension("string_length", 64)
            var = dataset.createVariable(
                "forecast_names", "c", ("forecasts", "string_length"))
            var[:] = netCDF4.stringtochar(forecast_names)
            result = main.read_forecast_names(dataset).astype("S64")
            expect = forecast_names
            np.testing.assert_array_equal(expect, result)


class TestEnvironment(unittest.TestCase):
    def tearDown(self):
        if "STATS_FILES" in os.environ:
            del os.environ["STATS_FILES"]

    def test_parse_env_requires_stats_files(self):
        with self.assertRaises(main.MissingEnvironmentVariable):
            result = main.parse_env()

    def test_stats_files_given_environment_variable(self):
        os.environ["STATS_FILES"] = "a.nc b.nc"
        result = main.parse_env().stats_files
        expect = ["a.nc", "b.nc"]
        self.assertEqual(expect, result)

    def test_attribute_default(self):
        os.environ["STATS_FILES"] = "a.nc b.nc"
        result = main.parse_env().attribute
        expect = "product"
        self.assertEqual(expect, result)

    def test_attribute_given_environment_variable(self):
        os.environ["STATS_FILES"] = "a.nc b.nc"
        os.environ["ATTRIBUTE"] = "system"
        result = main.parse_env().attribute
        expect = "system"
        self.assertEqual(expect, result)


class TestMain(unittest.TestCase):
    def test_main(self):
        path = "test-stats.nc"
        os.environ["STATS_FILES"] = path
        with netCDF4.Dataset(path, "w") as dataset:
            pass
        main.main()


class TestProfile(unittest.TestCase):
    def test_render_given_times(self):
        profile = main.Profile([])

    def test_time_mask(self):
        time_axis = [dt.datetime(2018, 1, 1)]
        times = [dt.datetime(2018, 1, 1)]
        result = main.time_mask(time_axis, times)
        expect = [True]
        self.assertEqual(expect, result)

    def test_time_mask_given_zero_times(self):
        start, middle, end = (
            dt.datetime(2018, 1, 1),
            dt.datetime(2018, 1, 2),
            dt.datetime(2018, 1, 3))
        result = main.time_mask([start, middle, end], [])
        expect = [False, False, False]
        np.testing.assert_array_equal(expect, result)

    def test_time_mask_given_single_time(self):
        start, middle, end = (
            dt.datetime(2018, 1, 1),
            dt.datetime(2018, 1, 2),
            dt.datetime(2018, 1, 3))
        result = main.time_mask([start, middle, end], [middle])
        expect = [False, True, False]
        np.testing.assert_array_equal(expect, result)

    def test_time_mask_given_two_times(self):
        start, middle, end = (
            dt.datetime(2018, 1, 1),
            dt.datetime(2018, 1, 2),
            dt.datetime(2018, 1, 3))
        result = main.time_mask([start, middle, end], [start, end])
        expect = [True, False, True]
        np.testing.assert_array_equal(expect, result)

    def test_time_mask_given_four_times(self):
        time_axis = np.array([
            dt.datetime(2018, 1, 1),
            dt.datetime(2018, 1, 2),
            dt.datetime(2018, 1, 3),
            dt.datetime(2018, 1, 4),
            dt.datetime(2018, 1, 5)], dtype=object)
        times = np.array([
            dt.datetime(2018, 1, 1),
            dt.datetime(2018, 1, 3),
            dt.datetime(2018, 1, 4),
            dt.datetime(2018, 1, 5)], dtype=object)
        result = main.time_mask(time_axis, times)
        expect = [True, False, True, True, True]
        np.testing.assert_array_equal(expect, result)
