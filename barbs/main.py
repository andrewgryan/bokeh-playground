import matplotlib.pyplot as plt
import matplotlib.quiver
import numpy as np
import bokeh.plotting
import custom

figure = bokeh.plotting.figure(
        match_aspect=True,
        sizing_mode="stretch_both")

ax = plt.gca()
angle = 30
X = np.array([1, 2, 3, 4, 5, 6, 7])
Y = np.array([1, 4, 3, 2, 5, 6, 1])
C = np.array([10, 20, 30, 40, 50, 60, 70])
U = C * np.cos(np.deg2rad(angle))
V = C * np.sin(np.deg2rad(angle))


X = np.arange(-10, 10, 1)
Y = np.arange(-10, 10, 1)
U, V = np.meshgrid(X, Y)

mpl_barbs = matplotlib.quiver.Barbs(ax, X, Y, U, V)

def bokeh_barbs(mpl_barb):
    """Convert matplotlib.quiver.Barbs to bokeh multiline/patches data"""
    xo, yo = mpl_barb.get_offsets().T
    paths = mpl_barb.get_paths()
    xs, ys = [], []
    for path in paths:
        x, y = path.vertices.T
        xs.append(x)
        ys.append(y)
    return xo, yo, xs, ys

x, y, a, b = bokeh_barbs(mpl_barbs)
glyph = custom.Barbs(
        x="x",
        y="y",
        a="a",
        b="b",
        size=10)
source = bokeh.models.ColumnDataSource(dict(
        x=x,
        y=y,
        a=a,
        b=b,
    ))
figure.add_glyph(source, glyph)
document = bokeh.plotting.curdoc()
document.add_root(figure)
