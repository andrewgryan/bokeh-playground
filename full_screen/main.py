import bokeh.plotting
document = bokeh.plotting.curdoc()
figure = bokeh.plotting.figure()
figure.circle([1, 2, 3], [1, 2, 3])
document.add_root(figure)
