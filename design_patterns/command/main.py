import bokeh.plotting
import bokeh.models


def main():
    root = bokeh.models.Dropdown()
    document = bokeh.plotting.curdoc()
    document.add_root(root)


if __name__.startswith("bk"):
    main()
