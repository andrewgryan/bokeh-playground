import bokeh.plotting
import cartopy
import numpy as np
from functools import partial


def coastlines(scale="110m"):
    xs, ys = [], []
    feature = cartopy.feature.COASTLINE
    feature.scale = scale
    for geometry in feature.geometries():
        for g in geometry:
            x, y = g.xy
            x, y = np.asarray(x), np.asarray(y)
            xs.append(x)
            ys.append(y)
    return xs, ys


def any_none(items):
    return any(item is None for item in items)


def combine_latest():
    state = [None, None, None, None]
    def callback(axis, attr, value):
        index = {
            ("x", "start"): 0,
            ("x", "end"): 1,
            ("y", "start"): 2,
            ("y", "end"): 3,
        }
        i = index[(axis, attr)]
        state[i] = value
        if any_none(state):
            return
        print(state)
    return callback


def main():
    xs, ys = coastlines()
    figure = bokeh.plotting.figure(sizing_mode="stretch_both")
    figure.multi_line(xs, ys)

    combinator = combine_latest()
    def on_change(axis, attr, old, new):
        combinator(axis, attr, new)

    figure.x_range.on_change("start", partial(on_change, "x"))
    figure.x_range.on_change("end", partial(on_change, "x"))
    figure.y_range.on_change("start", partial(on_change, "y"))
    figure.y_range.on_change("end", partial(on_change, "y"))

    document = bokeh.plotting.curdoc()
    document.add_root(figure)


if __name__ == '__main__' or __name__.startswith('bk'):
    main()
