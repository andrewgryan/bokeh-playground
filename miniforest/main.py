import asyncio
import os
import bokeh.plotting
import cartopy
import numpy as np


class Environment(object):
    def __init__(self, **kwargs):
        self.__dict__.update(**kwargs)


def parse_env():
    return Environment(path=os.environ["FOREST_FILE"])


def main():
    figure = full_screen_figure()
    x, y = transform(0, 0,
                     cartopy.crs.PlateCarree(),
                     cartopy.crs.Mercator.GOOGLE)
    print(x, y)
    label = bokeh.models.Label(
        x=x[0],
        y=y[0],
        text="Loading data")
    figure.add_layout(label)
    document = bokeh.plotting.curdoc()
    document.add_root(figure)
    document.add_next_tick_callback(next_tick(label))


def next_tick(label):
    async def callback():
        await asyncio.sleep(10)
        label.text = "Next tick finished"
    return callback


class UM(object):
    def __init__(self, dataset):
        self.dataset = dataset

    def longitudes(self):
        return self.dataset.variables["longitude_0"][:]

    def latitudes(self):
        return self.dataset.variables["latitude_0"][:]

    def values(self, variable):
        return self.dataset.variables[variable][0, :]


def full_screen_figure():
    lon_range = [-180, 180]
    lat_range = [-80, 80]
    x_range, y_range = transform(
        lon_range,
        lat_range,
        cartopy.crs.PlateCarree(),
        cartopy.crs.Mercator.GOOGLE)
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


def transform(x, y, src_crs, dst_crs):
    x, y = np.asarray(x), np.asarray(y)
    xt, yt, _ = dst_crs.transform_points(src_crs, x.flatten(), y.flatten()).T
    return xt, yt


if __name__.startswith("bk"):
    main()
