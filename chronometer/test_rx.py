import unittest
import rx


class History(rx.Stream):
    def __init__(self):
        self.events = []
        super().__init__()

    def notify(self, value):
        self.events.append(value)


class TestRx(unittest.TestCase):
    def test_combine_streams(self):
        clicks = rx.Stream()
        indices = rx.Stream()
        result = rx.scan_reset(
                clicks,
                accumulator=lambda a, i: a + i,
                reset=indices)

        history = History()
        result.register(history)
        indices.emit(10)
        indices.emit(20)
        clicks.emit(+0)
        indices.emit(30)
        clicks.emit(+1)

        result = history.events
        expect = [20, 31]
        self.assertEqual(expect, result)

    def test_combine_streams_with_seed_values(self):
        clicks = rx.Stream()
        indices = rx.Stream()
        result = rx.scan_reset_emit_seed(
                clicks, lambda a, i: a + i,
                reset=indices)

        history = History()
        result.register(history)

        indices.emit(10)
        indices.emit(20)
        indices.emit(30)

        result = history.events
        expect = [10, 20, 30]
        self.assertEqual(expect, result)

    def test_general_case(self):
        clicks = rx.Stream()
        indices = rx.Stream()
        result = rx.scan_reset_emit_seed(
                clicks, lambda a, i: a + i,
                reset=indices)

        history = History()
        result.register(history)

        indices.emit(10)
        clicks.emit(1)
        clicks.emit(-1)
        indices.emit(20)
        clicks.emit(1)
        indices.emit(30)
        clicks.emit(-1)

        result = history.events
        expect = [10, 11, 10, 20, 21, 30, 29]
        self.assertEqual(expect, result)
