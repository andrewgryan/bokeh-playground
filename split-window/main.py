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

gear = u"\u2699"
btn = bokeh.models.Button(width=10, label=u"")

def on_click():
    print("Hello, settings!")

btn.on_click(on_click)

root = bokeh.layouts.column(btn, name="custom")
document.add_root(root)


