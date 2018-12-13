import unittest
import unittest.mock
import bokeh.models
import main
import rx


class TestMain(unittest.TestCase):
    def test_main(self):
        main.main()

    def test_click_stream(self):
        stream = unittest.mock.Mock()
        callback = rx.click(stream)
        callback()
        stream.emit.assert_called_once_with()

    def test_stream_map_one(self):
        stream = rx.Stream()
        mapped_stream = stream.map(1)
        mapped_stream.emit = unittest.mock.Mock()
        stream.emit("Foo")
        mapped_stream.emit.assert_called_once_with(1)

    def test_stream_scan_two_streams(self):
        plus = rx.Stream()
        minus = rx.Stream()
        total = plus.map(1).merge(minus.map(-1)).scan(0, lambda a, i: a + i)
        total.emit = unittest.mock.Mock()
        plus.emit()
        minus.emit()
        plus.emit()
        plus.emit()
        total.emit.assert_has_calls([
            unittest.mock.call(1),
            unittest.mock.call(0),
            unittest.mock.call(1),
            unittest.mock.call(2)])


class TestTicker(unittest.TestCase):
    def test_ticks_given_hours(self):
        self.check([0, 0, 0], [0])

    def test_ticks_given_ten_hourlies(self):
        self.check([0, 1, 2, 3, 4, 5, 6, 7, 8, 9], [0, 3, 6, 9])

    def test_ticks_given_eleven_hourlies(self):
        self.check([0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11], [0, 3, 6, 9])

    def test_ticks_given_non_integer_values(self):
        self.check([1.5, 3.5], [0, 3])

    def test_ticks_given_forecasts_shorter_than_24_hours(self):
        self.check([6, 9, 12, 15, 18, 21], [0, 6, 12, 18])

    def test_ticks_given_greater_than_24_hours(self):
        self.check([6, 9, 12, 15, 18, 21, 24], [0, 12, 24])

    def test_ticks_given_greater_than_48_hours(self):
        self.check([6, 12, 18, 24, 30, 36, 42, 48, 54], [0, 24, 48])

    def test_ticks_given_greater_than_96_hours(self):
        self.check([12, 36, 60, 84, 108], [0, 48, 96])

    def check(self, hours, expect):
        result = main.ticks(hours)
        self.assertEqual(expect, result)
