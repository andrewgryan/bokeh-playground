# pylint: disable=missing-docstring, invalid-name
import unittest
import scipy.ndimage
import numpy as np


class TestMapCoordinates(unittest.TestCase):
    def setUp(self):
        self.values = np.array([
            [0, 1, 2],
            [3, 4, 5]
        ], dtype=np.float)

    def test_scipy_ndimage_map_coordinates(self):
        i = [1]
        j = [2]
        result = scipy.ndimage.map_coordinates(self.values, (i, j))
        expect = 5
        np.testing.assert_array_almost_equal(expect, result)

    def test_scipy_ndimage_map_coordinates_given_all_indices(self):
        i = [[0, 0, 0],
             [1, 1, 1]]
        j = [[0, 1, 2],
             [0, 1, 2]]
        result = scipy.ndimage.map_coordinates(self.values, (i, j))
        expect = self.values
        np.testing.assert_array_almost_equal(expect, result)

    def test_scipy_ndimage_map_coordinates_no_spline_filter(self):
        """
        A spline filter is only used when order is greater than 1

        Calling map_coordinates with order=1 is equivalent to
        a bilinear interpolator
        """
        i = np.array([[0, 0, 0],
                      [1, 1, 1]], dtype=np.float)
        j = np.array([[0, 0.5, 2],
                      [0, 1, 2]], dtype=np.float)
        result = scipy.ndimage.map_coordinates(self.values, (i, j), order=1)
        expect = np.array([
            [0, 0.5, 2],
            [3, 4, 5]
        ], dtype=np.float)
        np.testing.assert_array_almost_equal(expect, result)

    def test_scipy_ndimage_map_coordinates_bilinear_example(self):
        """order=1 equivalent to bilinear interpolation

        0---1---2
        | x |   |
        3---4---5

        x = 2 under bilinear interpolation
        """
        i = np.array([[0.5]], dtype=np.float)
        j = np.array([[0.5]], dtype=np.float)
        result = scipy.ndimage.map_coordinates(self.values, (i, j), order=1)
        expect = np.array([[2.]], dtype=np.float)
        np.testing.assert_array_almost_equal(expect, result)


class TestMeshgrid(unittest.TestCase):
    def test_meshgrid_indexing_ij(self):
        i = [0, 1]
        j = [0, 1, 2]
        result_i, result_j = np.meshgrid(i, j, indexing="ij")
        expect_i = [
            [0, 0, 0],
            [1, 1, 1],
        ]
        expect_j = [
            [0, 1, 2],
            [0, 1, 2],
        ]
        np.testing.assert_array_almost_equal(expect_i, result_i)
        np.testing.assert_array_almost_equal(expect_j, result_j)
