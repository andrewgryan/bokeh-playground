import bokeh.plotting
import chronometer

widget = chronometer.Chronometer()
document = bokeh.plotting.curdoc()
document.add_root(widget)
