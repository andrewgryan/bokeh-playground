import unittest
import rx


class History(rx.Stream):
    def __init__(self):
        self.events = []
        super().__init__()

    def notify(self, value):
        self.events.append(value)


def scan_with_reset(stream, accumulator, reset):
    return reset.flat_map_latest(lambda seed: stream.scan(seed, accumulator))


class TestRx(unittest.TestCase):
    def test_combine_streams(self):
        clicks = rx.Stream()
        indices = rx.Stream()
        result = scan_with_reset(
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
