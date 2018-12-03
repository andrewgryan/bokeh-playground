import numpy as np
import bokeh.plotting
import matplotlib.pyplot as plt

x = np.linspace(0, 1, 3)
y = np.linspace(0, 1, 3)
u, v = np.meshgrid(x, y)

artist = plt.streamplot(x, y, u, v)

bokeh_figure = bokeh.plotting.figure(sizing_mode="stretch_both")
xs = []
ys = []
for path in artist.lines.get_paths():
    x, y = path.vertices.T
    xs.append(x)
    ys.append(y)
ax = plt.gca()
for patch in ax.patches:
    path = patch.get_path()
    x, y = path.vertices.T
    xs.append(x)
    ys.append(y)
bokeh_figure.multi_line(xs=xs, ys=ys)
document = bokeh.plotting.curdoc()
document.add_root(bokeh_figure)
