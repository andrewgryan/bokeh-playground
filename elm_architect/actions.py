

UNDO = "UNDO"
REDO = "REDO"
SET_INDEX = "SET_INDEX"
ADD_ROW = "ADD_ROW"
REMOVE_ROW = "REMOVE_ROW"


def set_index(index):
    return {
        "kind": SET_INDEX,
        "payload": {
            "index": index
        }
    }


def add_row():
    return dict(kind=ADD_ROW)


def remove_row():
    return dict(kind=REMOVE_ROW)


def undo():
    return dict(kind=UNDO)


def redo():
    return dict(kind=REDO)
