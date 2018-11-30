# pylint: disable=missing-docstring, invalid-name
import unittest
import numpy as np
import main


@unittest.skip('rethinking')
class TestRegrid(unittest.TestCase):
    def test_regular_grid_given_unit_square(self):
        x = np.arange(2)
        y = np.arange(2)
        x, y = np.meshgrid(x, y)
        z = [[1, 2], [3, 4]]
        rx, ry, rz = main.regular_grid(x, y, z)
        ex = [[0, 1], [0, 1]]
        ey = [[0, 0], [1, 1]]
        ez = [[1, 2], [3, 4]]
        self.assert_grids_equal((ex, ey, ez), (rx, ry, rz))

    def test_regular_grid_given_uneven_y_dimension(self):
        x = np.arange(2)
        y = np.array([1., 4., 5.])
        x, y = np.meshgrid(x, y)
        z = [[1, 2], [3, 4], [5, 6]]
        rx, ry, rz = main.regular_grid(x, y, z)
        ex = [[0, 1], [0, 1], [0, 1]]
        ey = [[1, 1], [3, 3], [5, 5]]
        ez = [[1, 2], [7/3, 10/3], [5, 6]]
        self.assert_grids_equal((ex, ey, ez), (rx, ry, rz))

    def assert_grids_equal(self, expect, result):
        ex, ey, ez = expect
        rx, ry, rz = result
        np.testing.assert_array_almost_equal(ex, rx)
        np.testing.assert_array_almost_equal(ey, ry)
        np.testing.assert_array_almost_equal(ez, rz)
