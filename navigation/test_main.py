import unittest
import numpy as np
import datetime as dt
import main


class TestTimes(unittest.TestCase):
    def test_to_stamp(self):
        date = dt.datetime(2019, 4, 18, 6)
        result = main.to_stamp(date)
        expect = "2019-04-18 06:00"
        self.assertEqual(expect, result)

    def test_to_time(self):
        stamp = "2019-04-18 06:00"
        result = main.to_time(stamp)
        expect = dt.datetime(2019, 4, 18, 6)
        self.assertEqual(expect, result)

    def test_lengths(self):
        times = [
                dt.datetime(2019, 1, 1),
                dt.datetime(2019, 1, 1, 3)]
        result = main.to_lengths(times)
        expect = np.array([0, 3], dtype='timedelta64[h]')
        np.testing.assert_array_equal(expect, result)

    def test_format_length(self):
        value = np.timedelta64(3, 'h')
        result = main.format_length(value)
        expect = "T+3"
        self.assertEqual(expect, result)
