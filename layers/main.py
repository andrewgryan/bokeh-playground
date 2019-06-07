"""Scoping idea for layered interface"""
import bokeh.plotting
import numpy as np


class Application(object):
    def __init__(self):
        self.line_color = "black"
        self.figure = bokeh.plotting.figure()
        self.layers = []
        self.buttons = {
            "layer": bokeh.models.Button(label="Add layer")
        }
        self.buttons["layer"].on_click(self.add_layer)
        self.checkbox_group = bokeh.models.CheckboxGroup(
            labels=[],
            active=[]
        )
        self.checkbox_group.on_change("active", self.on_checkbox)
        self.editor = Editor()
        self.root = bokeh.layouts.column(
            self.figure,
            bokeh.layouts.row(
                self.editor.dropdowns["color"],
                self.buttons["layer"]),
            self.checkbox_group
        )
        self._i = 0

    def on_checkbox(self, attr, old, new):
        for i, layer in enumerate(self.layers):
            layer.renderers[0].visible = i in new

    def add_layer(self):
        xs = np.array([[0, 1, 1, 0, 0]]) + self._i
        ys = np.array([[0, 0, 1, 1, 0]]) + self._i
        source = bokeh.models.ColumnDataSource({
            "xs": xs,
            "ys": ys,
            "line_color": [self.editor.line_color]
        })
        layer = Layer(source)
        layer.attach(self.figure)
        self.layers.append(layer)
        self.checkbox_group.labels.append("Layer: {}".format(self._i))
        self.checkbox_group.active.append(self._i)
        self._i += 1


class Editor(object):
    def __init__(self, line_color="black"):
        self.line_color = line_color
        self.dropdowns = {
            "color": bokeh.models.Dropdown(label="Color", menu=[
                ("red", "red"),
                ("green", "green"),
                ("blue", "blue"),
                ("black", "black"),
            ])
        }
        self.dropdowns["color"].on_change("value", self.on_color)
        for dropdown in self.dropdowns.values():
            autolabel(dropdown)

    def on_color(self, attr, old, new):
        self.line_color = new


class Layer(object):
    def __init__(self, source):
        self.source = source
        self.glyph = bokeh.models.MultiLine(
            xs="xs", ys="ys", line_color="line_color")
        self.renderers = []

    def attach(self, figure):
        renderer = figure.add_glyph(self.source, self.glyph)
        self.renderers.append(renderer)


def autolabel(dropdown):
    def on_change(attr, old, new):
        for key, value in dropdown.menu:
            if value == new:
                dropdown.label = key
    dropdown.on_change("value", on_change)


def main():
    app = Application()
    document = bokeh.plotting.curdoc()
    document.add_root(app.root)


if __name__.startswith("bk"):
    main()
