"""Normalised State

Nested state is complex to traverse and duplicated
information is difficult to keep in sync

"""
from operator import itemgetter


INSERT_GROUP = "INSERT_GROUP"
INSERT_DIMENSIONS = "INSERT_DIMENSIONS"
INSERT_AXIS = "INSERT_AXIS"


def insert_group(label):
    return dict(kind=INSERT_GROUP, payload=locals())


def insert_dimensions(label, names):
    return dict(kind=INSERT_DIMENSIONS, payload=locals())


def insert_axis(label, name, values):
    return dict(kind=INSERT_AXIS, payload=locals())


def reducer(state, action):
    kind = action["kind"]
    if kind == INSERT_GROUP:
        return reducer_insert_group(state, action)
    elif kind == INSERT_DIMENSIONS:
        return reducer_insert_dimensions(state, action)
    elif kind == INSERT_AXIS:
        return reducer_insert_axis(state, action)
    return state


def reducer_insert_group(state, action):
    groups = state.get("groups", {})
    label = action["payload"]["label"]
    if label in group_labels(state):
        return state
    i = next_id(groups)
    groups[i] = label
    ids = groups.get("all", [])
    ids.append(i)
    groups["all"] = ids
    state["groups"] = groups
    return state


def reducer_insert_dimensions(state, action):
    label, names = itemgetter('label', 'names')(action['payload'])
    dimensions = state.get("dimensions", {})
    gid = group_id(state, label)
    dimensions[gid] = names
    state["dimensions"] = dimensions
    return state


def reducer_insert_axis(state, action):
    payload = action['payload']
    name, values = itemgetter('name', 'values')(payload)
    state["axis"] = {name: values}
    return state


def get_axis(state, label, name):
    return state["axis"][name]


def next_id(groups):
    ids = [k for k in groups.keys() if k != "all"]
    if len(ids) == 0:
        return 0
    else:
        return max(ids) + 1


def group_labels(state):
    if "groups" not in state:
        return []
    groups = state["groups"]
    return [groups[i] for i in groups["all"]]


def get_time(state, label):
    gid = group_id(state, label)
    tid = state["coords"][gid]["time"]
    return state["time"][tid]


def group_id(state, label):
    groups = state["groups"]
    for k, v in groups.items():
        if v == label:
            return k
