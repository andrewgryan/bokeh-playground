import unittest
import unittest.mock
import bokeh.models
import main


class Observable(object):
    def __init__(self, on_value):
        self.on_value = on_value

    def notify(self, value):
        self.on_value(value)


class Stream(object):
    def __init__(self):
        self.subscribers = []

    def register(self, subscriber):
        self.subscribers.append(subscriber)

    def subscribe(self, on_value):
        self.register(Observable(on_value))

    def emit(self, value=None):
        for subscriber in self.subscribers:
            subscriber.notify(value)

    def map(self, value):
        return Map(self, value)

    def merge(self, stream):
        return Merge(self, stream)

    def scan(self, initial, combinator):
        return Scan(self, initial, combinator)


class Map(Stream):
    def __init__(self, stream, method):
        if not hasattr(method, '__call__'):
            self.method = lambda x: method
        else:
            self.method = method
        stream.register(self)
        super().__init__()

    def notify(self, value):
        self.emit(self.method(value))


class Merge(Stream):
    def __init__(self, *streams):
        self.streams = streams
        for i, stream in enumerate(streams):
            stream.subscribe(self.notify)
        super().__init__()

    def notify(self, value):
        self.emit(value)


class Scan(Stream):
    def __init__(self, stream, initial, combinator):
        self.state = initial
        self.combinator = combinator
        stream.register(self)
        super().__init__()

    def notify(self, value):
        self.state = self.combinator(self.state, value)
        self.emit(self.state)


def click(stream):
    def wrapper():
        stream.emit(None)
    return wrapper


class TestMain(unittest.TestCase):
    def test_main(self):
        main.main()

    def test_click_stream(self):
        stream = unittest.mock.Mock()
        callback = click(stream)
        callback()
        stream.emit.assert_called_once_with(None)

    def test_stream_map_one(self):
        stream = Stream()
        mapped_stream = stream.map(1)
        mapped_stream.emit = unittest.mock.Mock()
        stream.emit("Foo")
        mapped_stream.emit.assert_called_once_with(1)

    def test_stream_scan_two_streams(self):
        plus = Stream()
        minus = Stream()
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
