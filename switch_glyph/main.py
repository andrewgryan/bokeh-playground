import bokeh.plotting
import bokeh.models
import bokeh.layouts
import numpy as np
import layer


class LayerLoader(object):
    """I/O layer data from disk"""
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
    groups = []
    dropdowns = []
    loader = LayerLoader()
    for color in ["orange", "yellow", "blue"]:
        model = layer.Layer()
        dropdown = bokeh.models.Dropdown(menu=[(k, k) for k in file_names])
        dropdown.on_change("value", pipe(model, loader))
        views = []
        for figure in figures:
            view = layer.View(model, figure, color=color)
            dropdown.on_change("value", view.on_change)
            views.append(view)
        dropdowns.append(dropdown)

        # Control L/R visibility
        def on_change(views):
            def on_change(attr, old, new):
                for i, view in enumerate(views):
                    view.visible = i in new
            return on_change
        group = bokeh.models.CheckboxButtonGroup(labels=["L", "R"])
        group.on_change("active", on_change(views))
        groups.append(group)

    column = bokeh.layouts.column(
            bokeh.layouts.row(*dropdowns),
            bokeh.layouts.row(*groups),
            bokeh.layouts.row(*figures))
    document = bokeh.plotting.curdoc()
    document.add_root(column)


def pipe(layer, loader):
    """Connect sources to file system"""
    def callback(attr, old, file_name):
        source = layer.get_source(file_name)
        source.data = loader.load(file_name)
    return callback


if __name__.startswith("bk"):
    main()
