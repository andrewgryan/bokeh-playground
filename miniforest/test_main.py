# pylint: disable=missing-docstring, invalid-name
import unittest
import os
import netCDF4
import numpy as np
import main


class TestEnvironment(unittest.TestCase):
    def tearDown(self):
        if "FOREST_FILE" in os.environ:
            del os.environ["FOREST_FILE"]

    def test_environment_given_forest_file_variable(self):
        os.environ["FOREST_FILE"] = "/other/file.nc"
        self.check("path", "/other/file.nc")

    def check(self, attr, expect):
        env = main.parse_env()
        result = getattr(env, attr)
        self.assertEqual(expect, result)


@unittest.skip("dead code")
class TestUMFile(unittest.TestCase):
    """
    dimensions:
        time = 41 ;
        latitude = 901 ;
        longitude = 1800 ;
        time_0 = 41 ;
        latitude_0 = 900 ;
        longitude_0 = 1800 ;
        pressure = 4 ;
        time_1 = 40 ;
        time_2 = 40 ;
        bnds = 2 ;
    variables:
        int latitude_longitude ;
            latitude_longitude:grid_mapping_name = "latitude_longitude" ;
            latitude_longitude:longitude_of_prime_meridian = 0.  ;
            latitude_longitude:earth_radius = 6371229. ;
        float latitude_0(latitude_0) ;
            latitude_0:axis = "Y" ;
            latitude_0:units = "degrees_north" ;
            latitude_0:standard_name = "latitude" ;
        float longitude_0(longitude_0) ;
            longitude_0:axis = "X" ;
            longitude_0:units = "degrees_east" ;
            longitude_0:standard_name = "longitude" ;
        double time_2(time_2) ;
            time_2:axis = "T" ;
            time_2:bounds = "time_2_bnds" ;
            time_2:units = "hours since 1970-01-01 00:00:00" ;
            time_2:standard_name = "time" ;
            time_2:calendar = "gregorian" ;
        double time_2_bnds(time_2, bnds) ;
        double forecast_period_2(time_2) ;
            forecast_period_2:bounds = "forecast_period_2_bnds" ;
            forecast_period_2:units = "hours" ;
            forecast_period_2:standard_name = "forecast_period" ;
        double forecast_period_2_bnds(time_2, bnds) ;
        float stratiform_rainfall_rate(time_2, latitude_0, longitude_0) ;
            stratiform_rainfall_rate:standard_name = "stratiform_rainfall_rate" ;
            stratiform_rainfall_rate:units = "kg m-2 s-1" ;
            stratiform_rainfall_rate:um_stash_source = "m01s04i203" ;
            stratiform_rainfall_rate:cell_methods = "time_2: mean (interval: 1 hour)" ;
            stratiform_rainfall_rate:grid_mapping = "latitude_longitude" ;
            stratiform_rainfall_rate:coordinates = "forecast_period_2 forecast_reference_time" ;
    """
    def setUp(self):
        self.dataset = netCDF4.Dataset("test.nc", "w", diskless=True)
        self.um = main.UM(self.dataset)

    def tearDown(self):
        self.dataset.close()

    def test_longitudes(self):
        values = [10, 20, 30, 40]
        self.dataset.createDimension("longitude_0", len(values))
        var = self.dataset.createVariable("longitude_0", "f", ("longitude_0",))
        var[:] = values
        result = self.um.longitudes()
        expect = values
        np.testing.assert_array_almost_equal(expect, result)

    def test_latitudes(self):
        values = [-10, 0, 10]
        self.dataset.createDimension("latitude_0", len(values))
        var = self.dataset.createVariable("latitude_0", "f", ("latitude_0",))
        var[:] = values
        result = self.um.latitudes()
        expect = values
        np.testing.assert_array_almost_equal(expect, result)

    def test_stratiform_rainfall_rate(self):
        values = np.ones((1, 1, 1))
        self.dataset.createDimension("time_2", 1)
        self.dataset.createDimension("latitude_0", 1)
        self.dataset.createDimension("longitude_0", 1)
        var = self.dataset.createVariable(
            "stratiform_rainfall_rate", "f",
            ("time_2", "latitude_0", "longitude_0"))
        var[:] = values

        result = self.um.values("stratiform_rainfall_rate")
        expect = values[0]
        np.testing.assert_array_almost_equal(expect, result)
