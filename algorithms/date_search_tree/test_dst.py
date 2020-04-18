import pytest
import datetime as dt
import dst


@pytest.fixture
def tree():
    return dst.DatetimeSearchTree()

def test_dst(tree):
    t = dt.datetime.now()
    tree.insert(t)


def test_dst_neighbours(tree):
    t = dt.datetime.now()
    tree.insert(t)
    assert tree.neighbours(t) == set([t])


def test_dst_neighbours(tree):
    ref = dt.datetime(2020, 1, 1)
    times = [
        dt.datetime(2020, 1, 1, 0),
        dt.datetime(2020, 1, 1, 5),
        dt.datetime(2020, 1, 4),
        dt.datetime(2020, 2, 1),
        dt.datetime(2021, 3, 1)]
    for time in times:
        tree.insert(time)
    assert tree.neighbours(ref, 'year') == set([2020, 2021])
    assert tree.neighbours(ref, 'month') == set([1, 2])
    assert tree.neighbours(ref, 'day') == set([1, 4])
    assert tree.neighbours(ref, 'hour') == set([0, 5])
    assert tree.neighbours(ref, 'raw') == set([ref])
