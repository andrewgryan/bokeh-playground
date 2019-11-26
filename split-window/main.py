import bokeh.plotting
from forest import geo

def figure():
    lon_range = (0, 30)
    lat_range = (0, 30)
    x_range, y_range = geo.web_mercator(
        lon_range,
        lat_range)
    figure = bokeh.plotting.figure(
        x_range=x_range,
        y_range=y_range,
        x_axis_type="mercator",
        y_axis_type="mercator",
        active_scroll="wheel_zoom")
    figure.axis.visible = False
    figure.toolbar.logo = None
    figure.toolbar_location = None
    figure.min_border = 3
    tile = bokeh.models.WMTSTileSource(
        url="https://maps.wikimedia.org/osm-intl/{Z}/{X}/{Y}.png",
        attribution=""
    )
    figure.add_tile(tile)

    legend = bokeh.models.Legend()
    figure.add_layout(legend)
    return figure

if True:
    figures = [
        [figure()], [figure(), figure()]
    ]
else:
    figures = [
        [
            [figure()], [figure(), figure()]
        ]
    ]
# figures[1][0].x_range = figures[1][1].x_range
# figures[1][0].y_range = figures[1][1].y_range
document = bokeh.plotting.curdoc()
root = bokeh.layouts.layout(
    figures,
    sizing_mode="stretch_both")
document.add_root(root)


from bokeh.core.properties import Override, Int
from bokeh.events import ButtonClick
class FontAwesomeButton(bokeh.models.AbstractButton):
    __implementation__ = 'font_awesome_button.ts'

    label = Override(default="FontAwesomeButton")
    clicks = Int(0)
    def on_click(self, handler):
        ''' Set up a handler for button clicks.

        Args:
            handler (func) : handler function to call when button is clicked.

        Returns:
            None

        '''
        self.on_event(ButtonClick, handler)


    def js_on_click(self, handler):
        ''' Set up a JavaScript handler for button clicks. '''
        self.js_on_event(ButtonClick, handler)


gear = u"\u2699"
user_btn = FontAwesomeButton(label="fa-user", width=10)
cog_btn = FontAwesomeButton(label="fa-cog", width=10)
layer_group_btn = FontAwesomeButton(label="fa-layer-group", width=10)

root = bokeh.layouts.row(user_btn,
                         bokeh.models.Div(width=20),
                         cog_btn,
                         bokeh.models.Div(width=20),
                         layer_group_btn,
                         name="custom")
document.add_root(root)


