import unittest
import unittest.mock
import datetime as dt
import numpy as np
import bokeh.models
import main
import rx
from functools import partial


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


class TestChronometer(unittest.TestCase):
    def test_chronometer_given_no_dates(self):
        source = bokeh.models.ColumnDataSource({
            "valid": [],
            "start": [],
            "offset": []
            })
        widget = main.chronometer(
                valid="valid",
                start="start",
                offset="offset",
                source=source)


class TestPartial(unittest.TestCase):
    def test_partial_kwargs(self):
        def method(dummy, a=None):
            return dummy, a
        f = partial(method, a=1)
        result = f("foo")
        expect = "foo", 1
        self.assertEqual(expect, result)


class TestTicker(unittest.TestCase):
    def test_ticks_given_max_zero(self):
        self.check(0, [0])

    def test_ticks_given_max_nine(self):
        self.check(9, [0, 3, 6, 9])

    def test_ticks_given_max_eleven(self):
        self.check(11, [0, 3, 6, 9])

    def test_ticks_given_non_integer(self):
        self.check(3.5, [0, 3])

    def test_ticks_given_max_below_24(self):
        self.check(21, [0, 6, 12, 18])

    def test_ticks_given_max_above_24(self):
        self.check(24, [0, 12, 24])

    def test_ticks_given_max_greater_than_48_hours(self):
        self.check(54, [0, 24, 48])

    def test_ticks_given_max_greater_than_96_hours(self):
        self.check(108, [0, 48, 96])

    def check(self, max_hour, expect):
        result = main.ticks(max_hour)
        self.assertEqual(expect, result)
