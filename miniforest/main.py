import asyncio
import netCDF4
import os
import bokeh.plotting
import bokeh.models
import bokeh.colors
import cartopy
import numpy as np
import time
from threading import Thread
from tornado import gen
from functools import partial
from bokeh.document import without_document_lock
from concurrent.futures import ThreadPoolExecutor


class Environment(object):
    def __init__(self, **kwargs):
        self.__dict__.update(**kwargs)


def parse_env():
    return Environment(path=os.environ["FOREST_FILE"])


def main():
    figure = full_screen_figure(
        lon_range=(-20, 60),
        lat_range=(-30, 20))
    source = bokeh.models.ColumnDataSource({
        "x": [],
        "y": [],
        "dw": [],
        "dh": [],
        "image": []
    })
    color_mapper = bokeh.models.LinearColorMapper(
        palette="Viridis256",
        nan_color=bokeh.colors.RGB(0, 0, 0, a=0)
    )

    figure.image(
        x="x",
        y="y",
        dw="dw",
        dh="dh",
        image="image",
        source=source,
        color_mapper=color_mapper)

    document = bokeh.plotting.curdoc()
    document.add_root(figure)

    messenger = Messenger(figure)
    controller = Controller(
        document,
        source,
        messenger)
    document.add_root(bokeh.layouts.column(
        *controller.buttons,
        name="controls"))


class Controller(object):
    def __init__(self, document, source, messenger):
        self.executor = ThreadPoolExecutor(max_workers=2)
        self.document = document
        self.source = source
        self.messenger = messenger
        self.i = None
        next_button = bokeh.models.Button(label="Next")
        next_button.on_click(self.on_next)
        prev_button = bokeh.models.Button(label="Previous")
        prev_button.on_click(self.on_previous)
        self.buttons = [
            next_button,
            prev_button
        ]

    def on_next(self):
        if self.i is None:
            self.i = 0
        else:
            self.i += 1
        self.render()

    def on_previous(self):
        if self.i is None:
            self.i = 0
        else:
            self.i -= 1
        self.render()

    def render(self):
        blocking_task = partial(load_data, self.i)
        self.document.add_next_tick_callback(
            unlocked_task(
                self.executor,
                blocking_task,
                self.document,
                self.source,
                self.messenger))


def unlocked_task(executor, blocking_task, document, source, messenger):
    @gen.coroutine
    @without_document_lock
    def task():
        document.add_next_tick_callback(messenger.on_load)
        data = yield executor.submit(blocking_task)
        document.add_next_tick_callback(partial(set_data, source, data))
        document.add_next_tick_callback(messenger.on_complete)
    return task


class Messenger(object):
    def __init__(self, figure):
        self.figure = figure
        self.label = bokeh.models.Label(
            x=0,
            y=0,
            text="")
        self.figure.add_layout(self.label)

    @gen.coroutine
    def on_load(self):
        self.render("Loading...")

    @gen.coroutine
    def on_complete(self):
        self.render("")

    def render(self, text):
        self.label.x = (
            self.figure.x_range.start +
            self.figure.x_range.end) / 2
        self.label.y = (
            self.figure.y_range.start +
            self.figure.y_range.end) / 2
        self.label.text = text


@gen.coroutine
def set_data(source, data):
    """locked update to safely modify document objects"""
    source.data = data


def load_data(i):
    path = (
        "/data/local/frrn/buckets/stephen-sea-public-london/model_data/"
        "highway_takm4p4_20190304T0000Z.nc")
    with netCDF4.Dataset(path) as dataset:
        lons = dataset.variables["longitude_0"][:]
        lats = dataset.variables["latitude_0"][:]
        values = dataset.variables["stratiform_rainfall_rate"][i]
        image = np.ma.masked_array(values, values == 0.)
        gx, _ = transform(
            lons,
            np.zeros(len(lons), dtype="d"),
            cartopy.crs.PlateCarree(),
            cartopy.crs.Mercator.GOOGLE)
        _, gy = transform(
            np.zeros(len(lats), dtype="d"),
            lats,
            cartopy.crs.PlateCarree(),
            cartopy.crs.Mercator.GOOGLE)
        x = gx.min()
        y = gy.min()
        dw = gx.max() - gx.min()
        dh = gy.max() - gy.min()
    data = {
        "x": [x],
        "y": [y],
        "dw": [dw],
        "dh": [dh],
        "image": [image]
    }
    return data


def full_screen_figure(
        lon_range=(-180, 180),
        lat_range=(-80, 80)):
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
