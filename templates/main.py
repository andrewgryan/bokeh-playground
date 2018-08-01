import bokeh.plotting
import bokeh.layouts
from bokeh.models.widgets import Button, Dropdown

# Bokeh document to be served
bokeh_document = bokeh.plotting.curdoc()

# Figure root
figure = bokeh.plotting.figure(name="figure",
                               css_classes=["figure"])
figure.circle([1, 2, 3], [1, 2, 3])
bokeh_document.add_root(figure)

# Navbar root
widgets = [Button(label="Next"),
           Button(label="Previous"),
           Dropdown()]
navbar = bokeh.layouts.row(*widgets,
                           name="navbar")
bokeh_document.add_root(navbar)
