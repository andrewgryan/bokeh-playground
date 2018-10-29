import bokeh.plotting
import cartopy
import numpy as np


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


def main():
    xs, ys = coastlines()
    figure = bokeh.plotting.figure(sizing_mode="stretch_both")
    figure.multi_line(xs, ys)
    document = bokeh.plotting.curdoc()
    document.add_root(figure)


if __name__ == '__main__' or __name__.startswith('bk'):
    main()
