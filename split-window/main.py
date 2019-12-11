import bokeh.plotting
from forest import geo
from font_awesome import FontAwesomeButton

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


gear = u"\u2699"
user_btn = FontAwesomeButton(label="fas fa-user", width=10)
cog_btn = FontAwesomeButton(label="fas fa-cog", width=10)
layer_group_btn = FontAwesomeButton(label="fas fa-layer-group", width=10)
save_btn = FontAwesomeButton(label="far fa-save", width=10)
trash_btn = FontAwesomeButton(label="fas fa-trash", width=10)

root = bokeh.layouts.row(user_btn,
                         bokeh.models.Div(width=20),
                         cog_btn,
                         bokeh.models.Div(width=20),
                         layer_group_btn,
                         bokeh.models.Div(width=20),
                         save_btn,
                         bokeh.models.Div(width=20),
                         trash_btn,
                         name="custom")
document.add_root(root)


