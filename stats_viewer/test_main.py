# pylint: disable=missing-docstring, invalid-name
import unittest
import netCDF4
import numpy as np
import main


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
