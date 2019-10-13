# pylint: disable=missing-docstring, invalid-name
import unittest
from main import *


class TestTimeIndex(unittest.TestCase):
    def test_get_time(self):
        label = "Label"
        state = {
            "groups": {
                2: label,
                "all": [2]
            },
            "coords": {
                2: {
                    "time": 5
                }
            },
            "time": {
                5: "2019-01-01 00:00:00",
                6: "2019-01-01 00:02:00"
            }
        }
        result = get_time(state, label)
        expect = "2019-01-01 00:00:00"
        self.assertEqual(expect, result)

    def test_insert_dimensions(self):
        label_0 = "Label 0"
        label_1 = "Label 1"
        names = ["initial_time", "valid_time"]
        state = {}
        for action in [
                insert_group(label_0),
                insert_group(label_1),
                insert_dimensions(label_1, names),
            ]:
            state = reducer(state, action)
        result = state
        expect = {
            "groups": {
                0: label_0,
                1: label_1,
                "all": [0, 1]
            },
            "dimensions": {
                1: names
            }
        }
        self.assertEqual(expect, result)

    def test_insert_axis(self):
        label = "Label"
        names = ["initial_time", "valid_time"]
        initial_times = [
            "2019-01-01 00:00:00"
        ]
        valid_times = [
            "2019-01-01 00:00:00",
            "2019-01-01 03:00:00",
            "2019-01-01 06:00:00",
        ]
        state = {}
        for action in [
                insert_group(label),
                insert_dimensions(label, names),
                insert_axis(label, "initial_time", initial_times),
                insert_axis(label, "valid_time", valid_times)
            ]:
            state = reducer(state, action)
        result = get_axis(state, label, "valid_time")
        expect = valid_times
        self.assertEqual(expect, result)

    def test_insert_axis_given_multiple_groups(self):
        label = "Label"
        names = ["initial_time", "valid_time"]
        initial_times = [
            "2019-01-01 00:00:00"
        ]
        valid_times = [
            "2019-01-01 00:00:00",
            "2019-01-01 03:00:00",
            "2019-01-01 06:00:00",
        ]
        state = {}
        for action in [
                insert_group(label),
                insert_dimensions(label, names),
                insert_axis(label, "initial_time", initial_times),
                insert_axis(label, "valid_time", valid_times)
            ]:
            state = reducer(state, action)
        result = get_axis(state, label, "valid_time")
        expect = valid_times
        self.assertEqual(expect, result)


class TestSelector(unittest.TestCase):
    def test_insert_group(self):
        result = reducer({}, insert_group("Label"))
        expect = {
            "groups": {
                0: "Label",
                "all": [0]
            }
        }
        self.assertEqual(expect, result)

    def test_insert_group_twice(self):
        state = {}
        for action in [
                    insert_group("A"),
                    insert_group("B"),
                ]:
            state = reducer(state, action)
        result = state
        expect = {
            "groups": {
                0: "A",
                1: "B",
                "all": [0, 1]
            }
        }
        self.assertEqual(expect, result)

    def test_insert_same_group_twice(self):
        state = {}
        for action in [
                    insert_group("A"),
                    insert_group("A"),
                ]:
            state = reducer(state, action)
        result = state
        expect = {
            "groups": {
                0: "A",
                "all": [0]
            }
        }
        self.assertEqual(expect, result)

    def test_labels(self):
        state = {
            "groups": {
                0: "A",
                1: "B",
                "all": [0, 1]
            }
        }
        result = group_labels(state)
        expect = ["A", "B"]
        self.assertEqual(expect, result)

    def test_labels_uses_all_ordering(self):
        state = {
            "groups": {
                0: "A",
                1: "B",
                2: "C",
                "all": [1, 0, 2]
            }
        }
        result = group_labels(state)
        expect = ["B", "A", "C"]
        self.assertEqual(expect, result)
