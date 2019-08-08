import bokeh.plotting
import bokeh.models
import bokeh.layouts
import layer


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
    menu = [(k, k) for k in file_names]
    controls = Controls(figures, menu, ["orange", "pink", "blue", "teal"])
    column = bokeh.layouts.column(
            bokeh.layouts.row(*controls.dropdowns),
            bokeh.layouts.row(*controls.groups),
            bokeh.layouts.row(*figures))
    document = bokeh.plotting.curdoc()
    document.add_root(column)


class Controls(object):
    def __init__(self, figures, menu, colors):
        self.dropdowns = []
        self.groups = []
        loader = layer.LayerLoader()
        for color in colors:
            model = layer.Layer()
            dropdown = bokeh.models.Dropdown(menu=menu)
            dropdown.on_change("value", pipe(model, loader))
            views = []
            for figure in figures:
                view = layer.View(model, figure, color=color)
                dropdown.on_change("value", view.on_change)
                views.append(view)
            left_right = layer.LeftRight(views)
            self.dropdowns.append(dropdown)
            self.groups.append(left_right.group)


def pipe(layer, loader):
    """Connect sources to file system"""
    def callback(attr, old, file_name):
        source = layer.get_source(file_name)
        source.data = loader.load(file_name)
    return callback


if __name__.startswith("bk"):
    main()
