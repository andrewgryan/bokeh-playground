# pylint: disable=missing-docstring, invalid-name
import unittest
import numpy as np
import main


def initial_resolution(circumference, pixels_per_tile):
    return circumference / pixels_per_tile


class TestMain(unittest.TestCase):
    def test_main_is_callable(self):
        main.main()


class TestPixelIndex(unittest.TestCase):
    def test_pixel_index(self):
        x, y, dp = 0, 0, 1
        result = main.pixel_index(x, y, dp)
        expect = (0, 0)
        self.assertEqual(expect, result)

    def test_pixel_index_given_position_along_x_axis(self):
        result = main.pixel_index(101, 0, 100)
        expect = (1, 0)
        self.assertEqual(expect, result)

    def test_pixel_index_given_position_along_x_axis(self):
        result = main.pixel_index(0, 97, 10)
        expect = (0, 9)
        self.assertEqual(expect, result)


class TestResolution(unittest.TestCase):
    def test_resolution_given_level_0(self):
        self.check(initial=2, level=0, expect=2)

    def test_resolution_given_level_1(self):
        self.check(initial=2, level=1, expect=1)

    def test_resolution_given_level_2(self):
        self.check(initial=2, level=2, expect=0.5)

    def test_resolution_given_level_3(self):
        self.check(initial=2, level=3, expect=0.25)

    def check(self, initial, level, expect):
        result = main.resolution(initial, level)
        self.assertEqual(expect, result)


class TestGlobalResolution(unittest.TestCase):
    def test_global_resolution(self):
        circumference = 1
        tile_size = 2
        result = main.global_resolution(circumference, tile_size)
        expect = 0.5
        self.assertEqual(expect, result)


class TestTileIndices(unittest.TestCase):
    def test_tile_indices(self):
        result = list(main.tile_indices((0, 0), (2, 1)))
        expect = [
            (0, 0),
            (0, 1),
            (1, 0),
            (1, 1),
            (2, 0),
            (2, 1)
        ]
        self.assertEqual(expect, result)
