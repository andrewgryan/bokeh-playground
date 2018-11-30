# pylint: disable=missing-docstring, invalid-name
import unittest
import scipy.ndimage
import numpy as np


class TestMapCoordinates(unittest.TestCase):
    def test_scipy_ndimage_map_coordinates(self):
        values = np.array([
            [0, 1, 2],
            [3, 4, 5]
        ])
        i = [1]
        j = [2]
        result = scipy.ndimage.map_coordinates(values, (i, j))
        expect = 5
        np.testing.assert_array_almost_equal(expect, result)

    def test_scipy_ndimage_map_coordinates_given_all_indices(self):
        values = np.array([
            [0, 1, 2],
            [3, 4, 5]
        ])
        i = [[0, 0, 0],
             [1, 1, 1]]
        j = [[0, 1, 2],
             [0, 1, 2]]
        result = scipy.ndimage.map_coordinates(values, (i, j))
        expect = values
        np.testing.assert_array_almost_equal(expect, result)

    def test_scipy_ndimage_map_coordinates_given_non_integer_index(self):
        values = np.array([
            [0, 1, 2],
            [3, 4, 5]
        ], dtype=np.float)
        i = [[0, 0, 0],
             [0.5, 0.5, 0.5]]
        j = [[0, 1, 2],
             [0, 1, 2]]
        result = scipy.ndimage.map_coordinates(values, (i, j))
        expect = np.array([
            [0, 1, 2],
            [1.5, 2.5, 3.5]
        ])
        np.testing.assert_array_almost_equal(expect, result)

    def test_scipy_ndimage_map_coordinates_given_different_axis(self):
        values = np.array([
            [0, 1, 2],
            [3, 4, 5]
        ], dtype=np.float)
        i = np.array([[0, 0, 0],
                      [1, 1, 1]], dtype=np.float)
        j = np.array([[0, 0.5, 2],
                      [0, 1, 2]], dtype=np.float)
        result = scipy.ndimage.map_coordinates(values, (i, j), order=1)
        expect = np.array([
            [0, 0.5, 2],
            [3, 4, 5]
        ], dtype=np.float)
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
