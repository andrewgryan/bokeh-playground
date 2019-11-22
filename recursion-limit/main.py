import numpy as np
import bokeh.plotting
import bokeh.layouts
import bokeh.models


figure = bokeh.plotting.figure()
source = bokeh.models.ColumnDataSource({})

def update(attr, old, new):
    source.data = {
        "x": np.random.randn(3),
        "y": np.random.randn(3),
    }

def on_click():
    update(None, None, None)

btn = bokeh.models.Button()
btn.on_click(on_click)

source.on_change("data", update)

root = bokeh.layouts.column(
        btn,
        figure)

document = bokeh.plotting.curdoc()
document.add_root(root)
