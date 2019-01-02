import unittest
import main


class TestMain(unittest.TestCase):
    def test_called(self):
        main.main()


class TestBoxX(unittest.TestCase):
    def test_box_x_given_zero_boxes(self):
        self.check([], [])

    def test_box_x_given_one_box(self):
        self.check([1], [0.5])

    def test_box_x_given_two_widths(self):
        self.check([0.4, 0.8], [0.2, 1.8])

    def check(self, n, expect):
        result = main.box_x(n)
        self.assertEqual(expect, result)

