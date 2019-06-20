import unittest
import unittest.mock
import redux


class TestRedux(unittest.TestCase):
    def test_observer(self):
        store = redux.Store()
        listener = unittest.mock.Mock()
        store.subscribe(listener)
        store.dispatch("A")
        listener.assert_called_once_with({"value": "A"})

    def test_reducer(self):
        result = redux.reducer({}, "A")
        expect = {"value": "A"}
        self.assertEqual(expect, result)

    def test_dedupe_middleware(self):
        store = redux.Store(middlewares=[
            redux.dedupe
        ])
        listener = unittest.mock.Mock()
        store.subscribe(listener)
        store.dispatch("A")
        store.dispatch("A")
        listener.assert_called_once_with({"value": "A"})

    def test_dedupe_multiple_calls(self):
        store = redux.Store(middlewares=[
            redux.dedupe
        ])
        listener = unittest.mock.Mock()
        store.subscribe(listener)
        store.dispatch("A")
        store.dispatch("B")
        store.dispatch("C")
        calls = [
            unittest.mock.call({"value": "A"}),
            unittest.mock.call({"value": "B"}),
            unittest.mock.call({"value": "C"})
        ]
        listener.assert_has_calls(calls)

    def test_action_log(self):
        log = redux.Log()
        store = redux.Store(middlewares=[
            log
        ])
        store.dispatch("A")
        store.dispatch("B")
        result = log.actions
        expect = ["A", "B"]
        self.assertEqual(expect, result)

    def test_log_after_dedupe(self):
        log = redux.Log()
        store = redux.Store(middlewares=[
            redux.dedupe,
            log
        ])
        listener = unittest.mock.Mock()
        store.subscribe(listener)
        store.dispatch("A")
        store.dispatch("B")
        store.dispatch("B")
        store.dispatch("C")
        result = log.actions
        expect = ["A", "B", "C"]
        self.assertEqual(expect, result)
        calls = [
            unittest.mock.call({"value": "A"}),
            unittest.mock.call({"value": "B"}),
            unittest.mock.call({"value": "C"})
        ]
        listener.assert_has_calls(calls)

    def test_log_before_dedupe(self):
        log = redux.Log()
        store = redux.Store(middlewares=[
            log,
            redux.dedupe
        ])
        listener = unittest.mock.Mock()
        store.subscribe(listener)
        store.dispatch("A")
        store.dispatch("B")
        store.dispatch("B")
        store.dispatch("C")
        result = log.actions
        expect = ["A", "B", "B", "C"]
        self.assertEqual(expect, result)
        calls = [
            unittest.mock.call({"value": "A"}),
            unittest.mock.call({"value": "B"}),
            unittest.mock.call({"value": "C"})
        ]
        listener.assert_has_calls(calls)

    def test_log_echo(self):
        log = redux.Log()
        store = redux.Store(middlewares=[
            redux.echo,
            log
        ])
        listener = unittest.mock.Mock()
        store.subscribe(listener)
        store.dispatch("A")
        store.dispatch("B")
        store.dispatch("C")
        result = log.actions
        expect = ["A", "A", "B", "B", "C", "C"]
        self.assertEqual(expect, result)
        calls = [
            unittest.mock.call({"value": "A"}),
            unittest.mock.call({"value": "A"}),
            unittest.mock.call({"value": "B"}),
            unittest.mock.call({"value": "B"}),
            unittest.mock.call({"value": "C"}),
            unittest.mock.call({"value": "C"})
        ]
        listener.assert_has_calls(calls)
