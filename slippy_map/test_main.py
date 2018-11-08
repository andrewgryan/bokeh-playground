import unittest
import main
import math


def tile(zoom_level, row, column):
    dw = (0.5) ** zoom_level
    return (0, 0, dw, dw)


def zoom_level(map_area, screen_area):
    if screen_area >= map_area:
        return 0
    return math.floor(math.log(map_area / screen_area, 4))


def center(x_start, x_end, y_start, y_end):
    return (x_start + x_end) / 2, (y_start + y_end) / 2


def area(x_start, x_end, y_start, y_end):
    return (x_end - x_start) * (y_end - y_start)


class TestTiles(unittest.TestCase):
    def test_tile(self):
        zoom_level = 0
        row = 0
        column = 0
        result = tile(zoom_level, row, column)
        expect = (0, 0, 1, 1)
        self.assertEqual(expect, result)

    def test_tile_given_zoom_level_1(self):
        zoom_level = 1
        row = 0
        column = 0
        result = tile(zoom_level, row, column)
        expect = (0, 0, 0.5, 0.5)
        self.assertEqual(expect, result)

    def test_zoom_level(self):
        self.check_zoom_level(map_area=1, screen_area=1, expect=0)

    def test_zoom_level_given_screen_one_quarter_of_map_area(self):
        self.check_zoom_level(map_area=1, screen_area=0.25, expect=1)

    def test_zoom_level_given_screen_one_sixteenth_of_map_area(self):
        self.check_zoom_level(map_area=1, screen_area=1/16, expect=2)

    def test_zoom_level_given_intermediate_size(self):
        self.check_zoom_level(map_area=1, screen_area=1/10, expect=1)

    def check_zoom_level(self, map_area, screen_area, expect):
        result = zoom_level(map_area, screen_area)
        self.assertEqual(expect, result)

    def test_center(self):
        x_start, x_end, y_start, y_end = 0, 1, 0, 1
        result = center(x_start, x_end, y_start, y_end)
        expect = (0.5, 0.5)
        self.assertEqual(expect, result)

    def test_area(self):
        x_start, x_end, y_start, y_end = 0, 1, 0, 1
        result = area(x_start, x_end, y_start, y_end)
        expect = 1
        self.assertEqual(expect, result)
