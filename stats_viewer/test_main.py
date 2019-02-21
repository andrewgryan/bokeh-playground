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


class TestProfileRead(unittest.TestCase):
    def setUp(self):
        self._paths = []
        self.path = self.fixture("test-read.nc")
        self.metrics = ["metric"]
        self.areas = ["area"]
        self.units = "seconds since 1981-01-01 00:00:00 utc"

    def fixture(self, path):
        self._paths.append(path)
        return path

    def tearDown(self):
        for path in self._paths:
            if os.path.exists(path):
                os.remove(path)

    def test_read_sets_circle_source(self):
        times = [dt.datetime(2019, 1, 1)]
        with netCDF4.Dataset(self.path, "w") as dataset:
            self.define(dataset, self.metrics, self.areas, times, self.units)
            var = dataset.createVariable(
                "stats_variable", "f",
                ("time", "forecasts", "surface", "metrics", "areas"))
            var[:] = 1
            dataset.product = "A"

        profile = main.ProfileSelection([self.path], "product")
        profile.render("A", "stats_variable", "metric", "area", times)
        result = profile.circle_source.data
        expect = {
            "x": [1.],
            "y": [0.],
            "t": np.array(times, dtype=object)
        }
        np.testing.assert_array_almost_equal(expect["x"], result["x"])
        np.testing.assert_array_almost_equal(expect["y"], result["y"])
        np.testing.assert_array_equal(expect["t"], result["t"])

    def test_read_selects_particular_files(self):
        times = [dt.datetime(2019, 1, 1)]
        with netCDF4.Dataset(self.path, "w") as dataset:
            self.define(dataset, self.metrics, self.areas, times, self.units)
            var = dataset.createVariable(
                "stats_variable", "f",
                ("time", "forecasts", "surface", "metrics", "areas"))
            var[:] = 1
            dataset.product = "B"

        profile = main.ProfileSelection([self.path], "product")
        profile.render("A", "stats_variable", "metric", "area", times)
        result = profile.circle_source.data
        expect = {
            "x": [],
            "y": [],
            "t": []
        }
        np.testing.assert_array_almost_equal(expect["x"], result["x"])
        np.testing.assert_array_almost_equal(expect["y"], result["y"])
        np.testing.assert_array_equal(expect["t"], result["t"])

    def test_read_profile_sets_time_correctly(self):
        year, month = 2018, 1
        times = [dt.datetime(year, month, 1), dt.datetime(year, month, 2)]
        depths = [10, 50]
        with netCDF4.Dataset(self.path, "w") as dataset:
            self.define(dataset, self.metrics, self.areas, times, self.units)
            self.define_depths(dataset, depths)
            var = dataset.createVariable(
                "stats_variable", "f",
                ("time", "forecasts", "depths", "metrics", "areas"))
            var[:] = [[1, 1], [2, 2]]
            dataset.product = "product"
        profile = main.ProfileSelection([self.path], "product")
        profile.render("product", "stats_variable", "metric", "area", times)
        result = profile.circle_source.data
        expect = {
            "x": [1, 1, 2, 2],
            "y": [10, 50, 10, 50],
            "t": [times[0], times[0], times[1], times[1]]
        }
        np.testing.assert_array_almost_equal(expect["x"], result["x"])
        np.testing.assert_array_almost_equal(expect["y"], result["y"])
        np.testing.assert_array_equal(expect["t"], result["t"])

    @staticmethod
    def define(dataset, metrics, areas, times, units):
        dataset.createDimension("time", len(times))
        dataset.createDimension("forecasts", 1)
        dataset.createDimension("surface", 1)
        dataset.createDimension("metrics", len(metrics))
        dataset.createDimension("areas", len(areas))
        dataset.createDimension("string_length", 64)
        var = dataset.createVariable(
            "metric_names", "c",
            ("metrics", "string_length"))
        var[:] = netCDF4.stringtochar(np.array(metrics, dtype="S64"))
        var = dataset.createVariable(
            "area_names", "c",
            ("areas", "string_length"))
        var[:] = netCDF4.stringtochar(np.array(areas, dtype="S64"))
        var = dataset.createVariable(
            "time", "d", ("time",))
        var.units = units
        var[:] = netCDF4.date2num(times, units=units)

    @staticmethod
    def define_depths(dataset, depths):
        dataset.createDimension("depths", len(depths))
        var = dataset.createVariable("depths", "f", ("depths",))
        var[:] = depths


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
