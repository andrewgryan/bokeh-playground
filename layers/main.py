"""
Any geospatial application can benefit from a simple
layer implementation. Allowing users to craft, add, remove and even
save layers is very important for exploring data.
"""
import bokeh.plotting
import numpy as np


class Application(object):
    """Object to encapsulate various menus, data structures and views"""
    def __init__(self):
        self.figure = bokeh.plotting.figure()
        self.layers = []
        self.buttons = {
            "add": bokeh.models.Button(label="Add layer"),
        }
        self.buttons["add"].on_click(self.add_layer)
        self.checkbox_group = bokeh.models.CheckboxGroup(
            labels=[],
            active=[]
        )
        self.checkbox_group.on_change("active", self.on_checkbox)
        self.dropdowns = {
            "layer": bokeh.models.Dropdown(label="Layers")
        }
        autolabel(self.dropdowns["layer"])
        self.dropdowns["layer"].on_change("value", self.on_layer)
        self.editor = Editor()
        self.root = bokeh.layouts.column(
            self.figure,
            self.editor.dropdowns["color"],
            bokeh.layouts.row(
                self.buttons["add"],
                self.editor.buttons["edit"],
                self.dropdowns["layer"],
            ),
            self.checkbox_group
        )
        self._i = 0

    def on_checkbox(self, attr, old, new):
        for i, layer in enumerate(self.layers):
            for renderer in layer.renderers:
                renderer.visible = i in new

    def add_layer(self):
        name = "Layer: {}".format(self._i)
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
        self.checkbox_group.labels.append(name)
        self.checkbox_group.active.append(self._i)
        self.dropdowns["layer"].menu.append((name, name))
        self._i += 1

    def on_layer(self, attr, old, new):
        for i, (key, value) in enumerate(self.dropdowns["layer"].menu):
            if value != new:
                continue
            self.editor.layer = self.layers[i]
            return


class Editor(object):
    """Responsible for editing layer settings"""
    def __init__(self, line_color="black"):
        self.active = False
        self.layer = None
        self.line_color = line_color
        self.buttons = {
            "edit": bokeh.models.CheckboxButtonGroup(labels=["Edit layer"])
        }
        self.buttons["edit"].on_change("active", self.on_active)
        self.dropdowns = {
            "color": bokeh.models.Dropdown(label="Color", menu=[
                ("red", "red"),
                ("orange", "orange"),
                ("yellow", "yellow"),
                ("green", "green"),
                ("blue", "blue"),
                ("black", "black"),
            ])
        }
        self.dropdowns["color"].on_change("value", self.on_color)
        for dropdown in self.dropdowns.values():
            autolabel(dropdown)

    def on_active(self, attr, old, new):
        self.active = 0 in new

    def on_color(self, attr, old, new):
        self.line_color = new
        if (self.active) and (self.layer is not None):
            self.layer.source.data["line_color"] = [self.line_color]


class Layer(object):
    """Thin wrapper to reference objects related to a layer"""
    def __init__(self, source):
        self.renderers = []
        self.source = source
        self.glyph = bokeh.models.MultiLine(
            xs="xs", ys="ys", line_color="line_color")

    def attach(self, figure):
        renderer = figure.add_glyph(self.source, self.glyph)
        self.renderers.append(renderer)


def autolabel(dropdown):
    """Helper to update dropdown label when choice is made"""
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
