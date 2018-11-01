import bokeh.plotting

figure = bokeh.plotting.figure()
figure.x_range.range_padding = 0.
figure.y_range.range_padding = 0.
figure.circle(x=[1, 2, 3], y=[1, 2, 3])

document = bokeh.plotting.curdoc()
document.add_root(figure)
