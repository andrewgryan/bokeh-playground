import bokeh.plotting
import bokeh.models


class History(object):
    def __init__(self):
        self.texts = []


def main():
    history = History()

    div = bokeh.models.Div()
    text = "Hello, world!"
    div.text = text
    history.texts.append(text)

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
        div.text = new
        history.texts.append(new)
    return wrapped


def undo(div, history):
    def wrapper():
        history.texts.pop(-1)
        div.text = history.texts[-1]
    return wrapper


if __name__.startswith("bk"):
    main()
