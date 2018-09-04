import bokeh.plotting
import bokeh.models
from bokeh.models import HoverTool, TapTool

def callback(attr, old, new):
    print("selected callback called")
    print(new.indices)

figure = bokeh.plotting.figure(tools=[HoverTool(tooltips=None),
                                      TapTool()])
renderer = figure.circle([1, 2, 3], [1, 2, 3], size=50)
renderer.selection_glyph = bokeh.models.Circle(fill_color="lightblue",
                                               line_color=None)
renderer.hover_glyph = bokeh.models.Square(fill_color="lightgreen",
                                           line_color=None)
renderer.data_source.on_change('selected', callback)
document = bokeh.plotting.curdoc()
document.add_root(figure)
