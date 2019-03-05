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
    x, y = transform(0, 0,
                     cartopy.crs.PlateCarree(),
                     cartopy.crs.Mercator.GOOGLE)
    label = bokeh.models.Label(
        x=x[0],
        y=y[0],
        text="")
    figure.add_layout(label)

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

    controller = Controller(
        document,
        source,
        label)
    document.add_root(bokeh.layouts.column(
        *controller.buttons,
        name="controls"))


class Controller(object):
    def __init__(self, document, source, label):
        self.executor = ThreadPoolExecutor(max_workers=2)
        self.document = document
        self.source = source
        self.label = label
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
                self.label))


def unlocked_task(executor, blocking_task, document, source, label):
    load_label = LoadLabel(label)
    @gen.coroutine
    @without_document_lock
    def task():
        document.add_next_tick_callback(load_label.render("Loading"))
        data = yield executor.submit(blocking_task)
        document.add_next_tick_callback(partial(set_data, source, data))
        document.add_next_tick_callback(load_label.render(""))
    return task


class LoadLabel(object):
    def __init__(self, label):
        self.label = label

    def render(self, text):
        @gen.coroutine
        def task():
            self.label.text = text
        return task


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
