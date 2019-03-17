import bokeh.plotting
import bokeh.models


class Write(object):
    def __init__(self, div, text, history):
        self.div = div
        self.text = text
        self.history = history

    def execute(self):
        self.div.text = self.text
        self.history.texts.append(self.text)


class History(object):
    def __init__(self):
        self.texts = []


def main():
    history = History()

    div = bokeh.models.Div()
    command = Write(div, "Hello, world!", history)
    command.execute()

    dropdown = bokeh.models.Dropdown(
        label="Choices",
        menu=[
            ("Item 1", "Item 1"),
            ("Item 2", "Item 2"),
            ("Item 3", "Item 3"),
        ])
    dropdown.on_change("value", on_change(div, history))

    button = bokeh.models.Button(label="Undo")
    button.on_click(undo(div, history))

    root = bokeh.layouts.column(
        button,
        dropdown,
        div)
    document = bokeh.plotting.curdoc()
    document.add_root(root)


def on_change(div, history):
    def wrapped(attr, old, new):
        command = Write(div, new, history)
        command.execute()
    return wrapped


def undo(div, history):
    def wrapper():
        history.texts.pop(-1)
        div.text = history.texts[-1]
    return wrapper


if __name__.startswith("bk"):
    main()
