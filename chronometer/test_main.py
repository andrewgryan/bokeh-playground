import unittest
import unittest.mock
import bokeh.models
import main
import rx


def click(stream):
    def wrapper():
        stream.emit()
    return wrapper


class TestMain(unittest.TestCase):
    def test_main(self):
        main.main()

    def test_click_stream(self):
        stream = unittest.mock.Mock()
        callback = click(stream)
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
