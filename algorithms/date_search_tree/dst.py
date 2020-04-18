"""Datetime search tree"""
from collections import defaultdict


class DatetimeSearchTree:
    """Data structure to quickly search/compress collections of datetimes"""
    def __init__(self):
        self.root = defaultdict(
            lambda: defaultdict(
                lambda: defaultdict(
                    lambda: defaultdict(set))))
        # Useful to protect data structure during queries
        self.elements = set()

    def insert(self, date):
        self.root[date.year][date.month][date.day][date.hour].add(date)
        self.elements.add(date)

    def neighbours(self, date, depth='raw'):
        """represent all datetimes"""
        if date not in self.elements:
            return set()
        # self.root[date.year][date.month][date.day][date.hour]
        nodes = self.root
        for key in ("year", "month", "day", "hour", "raw"):
            if key == depth:
                break
            nodes = nodes[getattr(date, key)]
        if isinstance(nodes, dict):
            return set(nodes.keys())
        else:
            return nodes
