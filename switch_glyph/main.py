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
    for color in colors:
        controls.add_control(color)
    column = bokeh.layouts.column(
            bokeh.layouts.row(*controls.dropdowns),
            bokeh.layouts.row(*controls.groups),
            bokeh.layouts.row(*figures))
    document = bokeh.plotting.curdoc()
    document.add_root(column)


if __name__.startswith("bk"):
    main()
