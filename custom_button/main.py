import bokeh.plotting
import bokeh.models
document = bokeh.plotting.curdoc()
for i in range(5):
    button = bokeh.models.Button(label="Button: {}".format(i))
    document.add_root(button)
