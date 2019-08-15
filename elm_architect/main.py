import bokeh.plotting
import bokeh.models
import bokeh.layouts
from observe import Observable
from redux import Store
import actions


class View(Observable):
    def __init__(self):
        self.layout = bokeh.layouts.column()
        super().__init__()

    def render(self, state):
        counter = state.get("counter", 0)
        if len(self.rows) > counter:
            self.layout.children.pop(-1)
        elif len(self.rows) < counter:
            index = len(self.rows)
            self.layout.children.append(self.row(index))

    @property
    def rows(self):
        return self.layout.children

    def row(self, index):
        button = bokeh.models.Button(label="Button: {}".format(str(index)))
        button.on_click(self.on_click(index))
        return bokeh.layouts.row(button)

    def on_click(self, index):
        def callback():
            self.notify(actions.set_index(index))
        return callback


class AddRemove(Observable):
    def __init__(self):
        buttons = {
            "add": bokeh.models.Button(label="Add"),
            "remove": bokeh.models.Button(label="Remove")
        }
        buttons["add"].on_click(self.on_add)
        buttons["remove"].on_click(self.on_remove)
        self.layout = bokeh.layouts.row(buttons["add"], buttons["remove"])
        super().__init__()

    def on_add(self):
        self.notify(actions.add_row())

    def on_remove(self):
        self.notify(actions.remove_row())


class Text(object):
    def __init__(self):
        self.div = bokeh.models.Div()
        self.layout = bokeh.layouts.column(self.div)

    def render(self, state):
        print("Text.render({})".format(state))
        texts = []
        for key in ["counter", "index"]:
            if key in state:
                value = str(state[key])
                texts.append("{}: {}".format(key, value))
        self.div.text = " ".join(texts)


def main():
    store = Store(reducer)
    undo_button = bokeh.models.Button(label="Undo")
    undo_button.on_click(lambda: store.dispatch(actions.undo()))
    redo_button = bokeh.models.Button(label="Redo")
    redo_button.on_click(lambda: store.dispatch(actions.redo()))
    add_remove = AddRemove()
    add_remove.subscribe(store.dispatch)
    text = Text()
    view = View()
    view.subscribe(store.dispatch)
    for method in [
            text.render,
            view.render]:
        store.subscribe(method)
    column = bokeh.layouts.column(
        bokeh.layouts.row(undo_button, redo_button),
        bokeh.layouts.row(text.layout),
        bokeh.layouts.row(view.layout),
        add_remove.layout)
    document = bokeh.plotting.curdoc()
    document.add_root(column)


def history(reducer):
    """Reducer decorator to make time-travel possible

    .. note:: App must be able to re-render initial state

             past, present, future = [], s0, []
    <action> past, present, future = [s0], s1, []
    <action> past, present, future = [s0, s1], s2, []
    <undo>   past, present, future = [s0], s1, [s2]
    <redo>   past, present, future = [s0, s1], s2, []
    """
    past, present, future = [], {}, []
    def wrapped(state, action):
        nonlocal past, present, future
        kind = action["kind"]
        if kind == actions.UNDO:
            if len(past) > 0:
                future.append(dict(present))
                present = past.pop()
                return present
            else:
                return state
        elif kind == actions.REDO:
            if len(future) > 0:
                past.append(dict(present))
                present = future.pop()
                return present
            else:
                return state
        else:
            future = []
            past.append(dict(present))
            present = reducer(state, action)
            return present
    return wrapped


@history
def reducer(state, action):
    kind = action["kind"]
    state = dict(state)
    if "ROW" in kind:
        counter = state.get("counter", 0)
        if kind == actions.ADD_ROW:
            counter += 1
        elif kind == actions.REMOVE_ROW:
            if counter >= 1:
                counter += -1
        state["counter"] = counter
    elif kind == actions.SET_INDEX:
        state["index"] = action["payload"]["index"]
    return state


if __name__.startswith("bk"):
    main()
