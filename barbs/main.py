import matplotlib.pyplot as plt
import matplotlib.quiver
import numpy as np
import bokeh.plotting
import forest

figure = bokeh.plotting.figure(
        match_aspect=True,
        sizing_mode="stretch_both")

ax = plt.gca()
angle = 30
C = 65
U = C * np.cos(np.deg2rad(angle))
V = C * np.sin(np.deg2rad(angle))
mpl_barbs = matplotlib.quiver.Barbs(ax, U, V)

xs, ys = forest.bokeh_barbs(mpl_barbs)
figure.patches(xs=xs, ys=ys)

document = bokeh.plotting.curdoc()
document.add_root(figure)
