import bokeh.plotting
import bokeh.models
document = bokeh.plotting.curdoc()
for i in range(10):
    if i % 2 == 0:
        name = "top"
    else:
        name = "bottom"
    button = bokeh.models.Button(label="Button: {}".format(i),
                                 name=name)
    document.add_root(button)
