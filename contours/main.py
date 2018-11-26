import bokeh.plotting
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.contour

figure = bokeh.plotting.figure(
        sizing_mode="stretch_both")

x = np.linspace(-1, 1, 100)
y = np.linspace(-1, 1, 100)
X, Y = np.meshgrid(x, y)
Z = X**2 + Y

ax = plt.gca()
qcs = matplotlib.contour.QuadContourSet(ax, X, Y, Z)
xs = [ss[:, 0].tolist() for s in qcs.allsegs for ss in s]
ys = [ss[:, 1].tolist() for s in qcs.allsegs for ss in s]
for c in qcs.collections:
    ax.collections.remove(c)

figure.multi_line(xs=xs, ys=ys)

document = bokeh.plotting.curdoc()
document.add_root(figure)
