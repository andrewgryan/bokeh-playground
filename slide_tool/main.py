import numpy as np
import bokeh.plotting
import bokeh.models
import slide
span = bokeh.models.Span(
        location=1.5,
        dimension="height")
figure = bokeh.plotting.figure(tools=[
    slide.SlideTool(span=span)])
figure.circle(x=[1, 2, 3], y=[1, 2, 3])
figure.add_layout(span)
document = bokeh.plotting.curdoc()
document.add_root(figure)
