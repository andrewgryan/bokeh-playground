import bokeh.plotting
import cartopy
import numpy as np


def main():
    figure = full_screen_figure()
    document = bokeh.plotting.curdoc()
    document.add_root(figure)


def full_screen_figure():
    lon_range = [-180, 180]
    lat_range = [-80, 80]
    x_range, y_range = transform(
        cartopy.crs.PlateCarree(),
        cartopy.crs.Mercator.GOOGLE,
        lon_range,
        lat_range)
    figure = bokeh.plotting.figure(
        sizing_mode="stretch_both",
        x_range=x_range,
        y_range=y_range,
        x_axis_type="mercator",
        y_axis_type="mercator",
        active_scroll="wheel_zoom")
    figure.toolbar_location = None
    figure.axis.visible = False
    figure.min_border = 0
    tile = bokeh.models.WMTSTileSource(
        url='http://c.tile.openstreetmap.org/{Z}/{X}/{Y}.png',
        attribution="Attribution text goes here"
    )
    figure.add_tile(tile)
    return figure


def transform(src_crs, dst_crs, x, y):
    x, y = np.asarray(x), np.asarray(y)
    xt, yt, _ = dst_crs.transform_points(src_crs, x.flatten(), y.flatten()).T
    return xt, yt


if __name__.startswith("bk"):
    main()
