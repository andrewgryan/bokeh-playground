"""A simple user interface component to control layers"""
from __future__ import annotations
import copy
import bokeh.plotting
import bokeh.models
import bokeh.layouts
from typing import Callable, Any

Action = dict
State = dict

# Constants to distinguish actions
ADD = "ADD"
REMOVE = "REMOVE"


def on_add() -> Action:
    """Create an ADD action"""
    return {"kind": ADD}


def on_remove() -> Action:
    """Create a REMOVE action"""
    return {"kind": REMOVE}


def reducer(state: State, action: Action) -> State:
    """Take a state and an action to produce a new state"""
    state = copy.deepcopy(state)
    n = state.get("n", 0)
    if action["kind"] == ADD:
        state["n"] = n + 1
    elif action["kind"] == REMOVE:
        state["n"] = n - 1
    return state


class Observable:
    """Observer design pattern"""
    def __init__(self):
        self.listeners = []

    def subscribe(self, listener: Callable[..., Any]):
        """Register listener with observable"""
        self.listeners.append(listener)

    def notify(self, value: Any):
        """Notify all listeners"""
        for listener in self.listeners:
            listener(value)


class Store(Observable):
    """Redux design pattern store"""
    def __init__(self, reducer: Callable[[dict, dict], dict]):
        self.state = {}
        self.reducer = reducer
        super().__init__()

    def dispatch(self, action: Action) -> None:
        self.state = self.reducer(self.state, action)
        self.notify(self.state)


class Component:
    """A component to control visible layers"""
    def __init__(self):
        self.layout = bokeh.layouts.column()

    def connect(self, store) -> Component:
        """Register component with store"""
        store.subscribe(self.on_state)
        return self

    def on_state(self, state: State):
        """State change event handler"""
        self.render(*self.to_props(state))

    @staticmethod
    def to_props(state: State) -> tuple:
        """Map state to values needed by render"""
        return (state.get("n", 0),)

    def render(self, nlayers: int):
        """Update widgets in response to state changes"""
        nrows = len(self.layout.children)
        if nrows < nlayers:
            # Add missing rows
            for _ in range(nlayers - nrows):
                self.add_row()
        elif nrows > nlayers:
            # Remove excess rows
            for _ in range(nrows - nlayers):
                self.remove_row()

    def add_row(self):
        """Construct and append row to component"""
        row = bokeh.layouts.row(bokeh.models.Div(text="Row"))
        self.layout.children.append(row)

    def remove_row(self):
        """Pop row off component"""
        self.layout.children.pop()


def main():
    """Example of using a redux design pattern"""
    store = Store(reducer)
    component = Component().connect(store)
    
    def on_click():
        store.dispatch(on_add())

    btn = bokeh.models.Button(label="Add")
    btn.on_click(on_click)

    root = bokeh.layouts.column(
        component.layout,
        btn)
    document = bokeh.plotting.curdoc()
    document.add_root(root)


if __name__.startswith("bk"):
    main()
