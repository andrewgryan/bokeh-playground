import unittest
import unittest.mock
import main


class TestCombineStreams(unittest.TestCase):
    def test_combine_given_two_streams_emits_from_first_stream(self):
        stream_1 = main.Stream()
        stream_2 = main.Stream()
        stream = main.combine(stream_1, stream_2)
        stream.emit = unittest.mock.Mock()
        stream_1.emit(0)
        stream.emit.assert_called_once_with(0)

    def test_combine_given_two_streams_emits_from_second_stream(self):
        stream_1 = main.Stream()
        stream_2 = main.Stream()
        stream = main.combine(stream_1, stream_2)
        stream.emit = unittest.mock.Mock()
        stream_2.emit(0)
        stream.emit.assert_called_once_with(0)

    def test_combine_latest(self):
        stream_1 = main.Stream()
        stream_2 = main.Stream()
        stream = main.combine_latest(stream_1, stream_2)
        stream.emit = unittest.mock.Mock()
        stream_2.emit(0)
        stream.emit.assert_called_once_with((None, 0))

    def test_combine_latest_given_multiple_emits(self):
        stream_1 = main.Stream()
        stream_2 = main.Stream()
        listener = unittest.mock.Mock()
        stream = main.combine_latest(stream_1, stream_2)
        stream.map(listener)
        stream_1.emit(0)
        stream_2.emit(0)
        stream_2.emit(1)
        expect = [(0, None), (0, 0), (0, 1)]
        listener.assert_has_calls([unittest.mock.call(args)
                                   for args in expect])
