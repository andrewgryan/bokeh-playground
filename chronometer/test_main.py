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

    def test_main_click_plus(self):
        btn = bokeh.models.Button()
        main.main(plus_button=btn)
        btn.trigger('clicks', None, None)

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
    def test_chronometer_click_minus(self):
        source = bokeh.models.ColumnDataSource({
            "valid": [0, 1, 2],
            "offset": [12, 12, 12],
            "start": [0, 1, 2]
            })
        btn = bokeh.models.Button()
        radio_group = bokeh.models.RadioGroup(
                labels=["Key"], active=0)
        selectors = {
            0: main.select("offset")
        }
        main.chronometer(
                valid="valid",
                start="start",
                offset="offset",
                source=source,
                minus_button=btn,
                radio_group=radio_group,
                selectors=selectors)
        btn.trigger('clicks', None, None)
        self.assertEqual(source.selected.indices, [2])

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

    def test_chronometer_returns_widgets(self):
        source = bokeh.models.ColumnDataSource({
            "valid": [],
            "start": [],
            "offset": []
            })
        widgets = main.chronometer(
                valid="valid",
                start="start",
                offset="offset",
                source=source)
        figure, radio_group, plus, minus = widgets
        self.assertIsInstance(figure, bokeh.plotting.Figure)

    def test_chronometer_streaming_dates(self):
        """should keep selection up to date"""
        button = bokeh.models.Button()
        radio_group = bokeh.models.RadioGroup(labels=["Run"], active=0)
        source = bokeh.models.ColumnDataSource({
            "valid": [],
            "start": [],
            "offset": []
            })
        main.chronometer(
                valid="valid",
                start="start",
                offset="offset",
                source=source,
                radio_group=radio_group,
                selectors={
                    0: main.select("start")
                },
                plus_button=button)
        source.stream({
            "valid": [dt.datetime(2018, 1, 1), dt.datetime(2018, 1, 1, 12)],
            "start": [dt.datetime(2018, 1, 1), dt.datetime(2018, 1, 1)],
            "offset": [dt.timedelta(hours=0), dt.timedelta(hours=12)]
            })
        source.selected.indices = [0]
        button.trigger('clicks', None, None)
        result = source.selected.indices
        expect = [1]
        self.assertEqual(expect, result)


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
