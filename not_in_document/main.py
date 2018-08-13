import bokeh.plotting
import bokeh.models

def main():
    figure = bokeh.plotting.figure()
    figure.circle([1, 2, 3], [1, 2, 3])
    layout = bokeh.layouts.column(figure)
    bokeh.plotting.curdoc().add_root(layout)

if __name__ == '__main__' or __name__.startswith("bk"):
    main()
