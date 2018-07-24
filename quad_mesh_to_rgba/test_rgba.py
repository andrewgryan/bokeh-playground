import unittest
import numpy as np
import matplotlib.pyplot as plt


def rgba(ni, nj):
    return np.zeros((ni, nj, 4), dtype=np.uint8)


class Test(unittest.TestCase):
    def test_rgba_dtype_is_unit8(self):
        ni, nj = 3, 4
        result = rgba(ni, nj)
        self.assertEqual(result.dtype, np.uint8)

    def test_rgba_shape(self):
        ni, nj = 3, 4
        result = rgba(ni, nj)
        self.assertEqual(result.shape, (ni, nj, 4))

    def test_from_quad_mesh(self):
        values = np.ones((1, 1))
        quad_mesh = plt.pcolormesh(values)
        result = quad_mesh.to_rgba(quad_mesh.get_array(),
                                   bytes=True)
        expect = [[68, 1, 84, 255]]
        np.testing.assert_array_almost_equal(result, expect)
        self.assertEqual(result.dtype, np.uint8)
