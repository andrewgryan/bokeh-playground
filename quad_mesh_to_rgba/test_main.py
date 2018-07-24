import unittest
import numpy as np
import matplotlib.pyplot as plt


class TestQuadMeshToBokehRGBA(unittest.TestCase):
    """Mapping from matplotlib.pcolormesh to bokeh image_rgba"""
    def test_quad_mesh_to_image_rgba(self):
        values = np.ones((1, 1))
        quad_mesh = plt.pcolormesh(values)
        result = quad_mesh.to_rgba(quad_mesh.get_array(),
                                   bytes=True).reshape((1, 1, 4))
        expect = [[[68, 1, 84, 255]]]
        np.testing.assert_array_almost_equal(result, expect)
        self.assertEqual(result.dtype, np.uint8)

    def test_imshow_to_rgba(self):
        values = np.ones((1, 1))
        quad_mesh = plt.imshow(values)
        result = quad_mesh.to_rgba(quad_mesh.get_array(),
                                   bytes=True).reshape((1, 1, 4))
        expect = [[[68, 1, 84, 255]]]
        np.testing.assert_array_almost_equal(result, expect)
        self.assertEqual(result.dtype, np.uint8)
