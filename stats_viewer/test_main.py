# pylint: disable=missing-docstring, invalid-name
import unittest
import datetime as dt
import netCDF4
import numpy as np
import main
import os


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


def fixtures(cls):
    class Wrapped(cls):
        def setUp(self):
            self._paths = []
            super().setUp()

        def tearDown(self):
            for path in self._paths:
                if os.path.exists(path):
                    os.remove(path)
            super().tearDown()

        def fixture(self, path):
            self._paths.append(path)
            return path

        def add_fixtures(self, paths):
            self._paths += paths
            return paths

    return Wrapped


@fixtures
class TestProfileRead(unittest.TestCase):
    def setUp(self):
        self.path = self.fixture("test-read.nc")
        self.forecast_names = ["forecast"]
        self.forecasts = [12.]
        self.metrics = ["metric"]
        self.areas = ["area"]
        self.units = "seconds since 1981-01-01 00:00:00 utc"
        self.product = "FOAM"

    def test_read_sets_circle_source(self):
        times = [dt.datetime(2019, 1, 1)]
        with netCDF4.Dataset(self.path, "w") as dataset:
            statistics = Statistics(
                dataset,
                self.forecast_names,
                self.forecasts,
                self.metrics,
                self.areas,
                times)
            var = statistics.variable("stats_variable", surface=True)
            var[:] = 1
            dataset.product = self.product

        profile = main.ProfileSelection([self.path], "product")
        profile.render(self.product, "stats_variable", "metric", "area", times)
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
            statistics = Statistics(
                dataset,
                self.forecast_names,
                self.forecasts,
                self.metrics,
                self.areas,
                times)
            var = statistics.variable("stats_variable", surface=True)
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
            statistics = Statistics(
                dataset,
                self.forecast_names,
                self.forecasts,
                self.metrics,
                self.areas,
                times,
                depths)
            var = statistics.variable("stats_variable")
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


@fixtures
class TestLeadtime(unittest.TestCase):
    def setUp(self):
        self.forecast_names = ["forecast"]
        self.forecasts = [12.]
        self.metrics = ["metric"]
        self.areas = ["area"]
        self.times = [dt.datetime(2019, 1, 1)]
        self.depths = [10, 20]
        self.attribute = "product"

    def test_leadtime_read_given_two_files_returns_average(self):
        paths = self.add_fixtures(["test-lt-0.nc", "test-lt-1.nc"])
        for i, path in enumerate(paths):
            with netCDF4.Dataset(path, "w") as dataset:
                statistics = Statistics(
                    dataset,
                    self.forecast_names,
                    self.forecasts,
                    self.metrics,
                    self.areas,
                    self.times,
                    self.depths)
                var = statistics.variable("stats_variable")
                var[:] = i
                setattr(dataset, self.attribute, "A")
        leadtime = main.Leadtime(paths, self.attribute)
        leadtime.render("A", "stats_variable", "metric", "area")
        result = leadtime.source.data
        expect = {
            "x": [12.],
            "y": [0.5]
        }
        np.testing.assert_array_almost_equal(expect["x"], result["x"])
        np.testing.assert_array_almost_equal(expect["y"], result["y"])

    def test_leadtime_read_filters_files_by_attribute(self):
        paths = self.add_fixtures(["test-lt-0.nc", "test-lt-1.nc"])
        labels = ["A", "B"]
        for i, path in enumerate(paths):
            with netCDF4.Dataset(path, "w") as dataset:
                statistics = Statistics(
                    dataset,
                    self.forecast_names,
                    self.forecasts,
                    self.metrics,
                    self.areas,
                    self.times,
                    self.depths)
                var = statistics.variable("stats_variable")
                var[:] = i
                setattr(dataset, self.attribute, labels[i])
        leadtime = main.Leadtime(paths, self.attribute)
        leadtime.render("B", "stats_variable", "metric", "area")
        result = leadtime.source.data
        expect = {
            "x": [12.],
            "y": [1]
        }
        np.testing.assert_array_almost_equal(expect["x"], result["x"])
        np.testing.assert_array_almost_equal(expect["y"], result["y"])


class TestEraseStatistics(unittest.TestCase):
    def setUp(self):
        self.dataset = netCDF4.Dataset("test-remove.nc", "w", diskless=True)
        self.variable = "stats_variable"
        self.forecast_names = ["forecast", "forecast", "persistence"]
        self.forecasts = [12., 36., 12.]
        self.areas = ["A1", "A2"]
        self.metrics = ["M1", "M2"]
        self.times = [dt.datetime(2019, 1, 1), dt.datetime(2019, 1, 2)]
        self.shape = (
            len(self.times),
            len(self.forecasts),
            1,
            len(self.metrics),
            len(self.areas))

    def tearDown(self):
        self.dataset.close()

    def test_remove_statistic_erases_particular_statistic(self):
        ti, fi, mi, ai = 0, 0, 1, 0
        values = np.ma.arange(np.product(self.shape)).reshape(self.shape)
        statistics = Statistics(
            self.dataset,
            self.forecast_names,
            self.forecasts,
            self.metrics,
            self.areas,
            self.times)
        var = statistics.variable(self.variable, surface=True)
        var[:] = values
        main.remove_statistic(
            self.dataset,
            self.variable,
            self.forecast_names[fi],
            self.forecasts[fi],
            self.metrics[mi],
            self.areas[ai],
            self.times[ti])
        result = self.dataset.variables[self.variable][:]
        expect = values.copy()
        expect[ti, fi, :, mi, ai] = np.ma.masked
        self.assert_masked_array_equal(expect, result)

    def assert_masked_array_equal(self, expect, result):
        self.assertEqual(expect.shape, result.shape)
        np.testing.assert_array_equal(expect.compressed(), result.compressed())


class Statistics(object):
    units = "seconds since 1981-01-01 00:00:00 utc"

    def __init__(self,
                 dataset,
                 forecast_names,
                 forecasts,
                 metrics,
                 areas,
                 times,
                 depths=None):
        self.dataset = dataset
        self.define(dataset, metrics, areas, times, self.units)
        self.define_forecasts(dataset, forecast_names, forecasts)
        if depths is not None:
            self.define_depths(dataset, depths)

    @staticmethod
    def define(dataset, metrics, areas, times, units):
        dataset.createDimension("time", len(times))
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
        if len(times) > 0:
            var[:] = netCDF4.date2num(times, units=units)

    @staticmethod
    def define_forecasts(dataset, names, hours):
        dataset.createDimension("forecasts", len(names))
        var = dataset.createVariable(
            "forecast_names", "c",
            ("forecasts", "string_length"))
        var[:] = netCDF4.stringtochar(np.array(names, dtype="S64"))
        var = dataset.createVariable(
            "forecasts", "f",
            ("forecasts",))
        var[:] = hours

    @staticmethod
    def define_depths(dataset, depths):
        dataset.createDimension("depths", len(depths))
        var = dataset.createVariable("depths", "f", ("depths",))
        var[:] = depths

    def variable(self, name, surface=False):
        if surface:
            depths = "surface"
        else:
            depths = "depths"
        return self.dataset.createVariable(
            name, "f", ("time", "forecasts", depths, "metrics", "areas"))


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
