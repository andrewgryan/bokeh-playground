import bokeh.plotting
import bokeh.models
import bokeh.layouts
import numpy as np


class Model(object):
    def __init__(self):
        self.sources = {}

    def get_source(self, file_name):
        return self.select(self.key(file_name))

    @staticmethod
    def key(file_name):
        if file_name.endswith(".json"):
            return "geojson"
        else:
            return "column_data_source"

    def select(self, key):
        if key not in self.sources:
            self.sources[key] =  bokeh.models.ColumnDataSource({
                "x": [],
                "y": [],
            })
        return self.sources[key]


class View(object):
    def __init__(self, model, figure, color):
        self.model = model
        self.figure = figure
        self.color = color
        self.glyphs = {}

    def on_change(self, attr, old, new):
        # Select/construct glyph_renderer on demand
        glyph_key = self.glyph_key(new)
        if glyph_key not in self.glyphs:
            source = self.model.get_source(new)
            self.glyphs[glyph_key] = self.glyph(glyph_key, source)

        # Mute unselected glyphs
        for key, glyph in self.glyphs.items():
            glyph.visible = key == glyph_key

    def glyph(self, key, source):
        if key == "circle":
            return self.figure.circle(x="x", y="y", source=source, fill_color=self.color)
        elif key == "line":
            return self.figure.line(x="x", y="y", source=source, line_color=self.color)
        elif key == "square":
            return self.figure.square(x="x", y="y", source=source, fill_color=self.color)

    @staticmethod
    def glyph_key(file_name):
        if file_name.endswith(".nc"):
            return "line"
        elif file_name.endswith(".json"):
            return "circle"
        else:
            return "square"


class Loader(object):
    def __init__(self):
        self.cache = {}

    def load(self, file_name):
        if file_name not in self.cache:
            # Random data per file
            self.cache[file_name] = {
                "x": np.random.randn(10),
                "y": np.random.randn(10)
            }
        return self.cache[file_name]


def main():
    file_names = [
        "file_0.nc",
        "file_1.nc",
        "file.json",
        "file_2.nc",
        "other.json",
        "lightning.txt",
    ]
    figures = [
        bokeh.plotting.figure(),
        bokeh.plotting.figure()
    ]
    dropdowns = []
    loader = Loader()
    for color in ["orange", "yellow", "blue"]:
        model = Model()
        dropdown = bokeh.models.Dropdown(menu=[(k, k) for k in file_names])

        def load_data(model, loader):
            def callback(attr, old, new):
                source = model.get_source(new)
                source.data = loader.load(new)
            return callback

        dropdown.on_change("value", load_data(model, loader))
        for figure in figures:
            view = View(model, figure, color=color)
            dropdown.on_change("value", view.on_change)
        dropdowns.append(dropdown)

    column = bokeh.layouts.column(
            bokeh.layouts.row(*dropdowns),
            bokeh.layouts.row(*figures))
    document = bokeh.plotting.curdoc()
    document.add_root(column)


if __name__.startswith("bk"):
    main()
