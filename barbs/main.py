import matplotlib.pyplot as plt
import matplotlib.quiver
import numpy as np
import bokeh.plotting
# import forest
import custom

figure = bokeh.plotting.figure(
        match_aspect=True,
        sizing_mode="stretch_both")

# ax = plt.gca()
# angle = 30
# C = 65
# U = C * np.cos(np.deg2rad(angle))
# V = C * np.sin(np.deg2rad(angle))
# mpl_barbs = matplotlib.quiver.Barbs(ax, U, V)
#
# xs, ys = forest.bokeh_barbs(mpl_barbs)
# figure.patches(xs=xs, ys=ys)

for i, (x, y) in enumerate([(0, 0), (1, 0)]):
    if i == 0:
        xs = [0, -7, -7.875, -7, 0]
        ys = [0, 0, 2.8, 0, 0]
    else:
        xs = [0, 0, -1.4, 0, 0, 0]
        ys = [0, -5.6875, -6.125, -5.6875, -7, 0]
    glyph = custom.Barbs(x=x, y=y, barb_x=xs, barb_y=ys, size=10)
    figure.add_glyph(glyph)

document = bokeh.plotting.curdoc()
document.add_root(figure)
