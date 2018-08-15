import bokeh.plotting
document = bokeh.plotting.curdoc()
figure = bokeh.plotting.figure(match_aspect=True,
                               aspect_scale=1)
figure.circle([1, 2, 3], [1, 2, 3])
document.add_root(figure)
