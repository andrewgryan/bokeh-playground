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
    colors = ["orange", "pink", "blue", "teal"]
    controls = layer.Controls(figures, menu)
    dropdowns, groups = [], []
    for color in colors:
        dropdown, views = controls.add_control(color)
        dropdowns.append(dropdown)
        left_right = layer.LeftRight(views)
        groups.append(left_right.group)

    column = bokeh.layouts.column(
            bokeh.layouts.row(*dropdowns),
            bokeh.layouts.row(*groups),
            bokeh.layouts.row(*figures))
    document = bokeh.plotting.curdoc()
    document.add_root(column)


class Expandable(object):
    def __init__(self):
        self.add_button = bokeh.models.Button(label="Add")
        self.add_button.on_click(self.on_click_add)
        self.remove_button = bokeh.models.Button(label="Remove")
        self.remove_button.on_click(self.on_click_remove)
        self.row = bokeh.layouts.row(self.add_button, self.remove_button)

    def on_click_add(self):
        self.row.children.append(bokeh.models.Button())

    def on_click_remove(self):
        if len(self.row.children) > 2:
            self.row.children.pop(-1)


if __name__.startswith("bk"):
    main()
