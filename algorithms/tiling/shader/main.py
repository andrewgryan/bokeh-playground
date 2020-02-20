import numpy as np
import netCDF4
import datashader
import xarray
import bokeh.plotting
import bokeh.colors
from functools import partial
from tornado import gen


class EIDA50:
    def __init__(self, paths):
        self.paths = paths
        with netCDF4.Dataset(paths[0]) as dataset:
            self.lons = dataset.variables["longitude"][:]
            self.lats = dataset.variables["latitude"][:]
        self.recordings = []
        for path in paths:
            with netCDF4.Dataset(path) as dataset:
                data = dataset.variables["data"][0, :]
                self.recordings.append(data)


class OldView:
    """Classic FOREST"""
    def __init__(self, color_mapper, loader):
        self.loader = loader
        self.color_mapper = color_mapper
        self.source = bokeh.models.ColumnDataSource({
            "x": [],
            "y": [],
            "dw": [],
            "dh": [],
            "image": []
        })

    def render(self, index):
        self.source.data = self._to_image(
            self.loader.lons,
            self.loader.lats,
            self.loader.recordings[index])

    @staticmethod
    def _to_image(lons, lats, data):
        xr = xarray.DataArray(data, coords=[("y", lats), ("x", lons)], name="Z")
        return image_data(xr, (-20, 60), (-20, 40))

    def add_figure(self, figure):
        figure.image(x="x",
                     y="y",
                     dw="dw",
                     dh="dh",
                     image="image",
                     source=self.source,
                     color_mapper=self.color_mapper)


class NewView:
    """Tiled/Animated FOREST"""
    def __init__(self, color_mapper, loader):
        self.loader = loader
        self.color_mapper = color_mapper
        self.source = bokeh.models.ColumnDataSource({
            "x": [],
            "y": [],
            "dw": [],
            "dh": [],
            "image": []
        })

    def add_figure(self, figure):
        figure.image(x="x",
                     y="y",
                     dw="dw",
                     dh="dh",
                     image="image",
                     source=self.source,
                     color_mapper=self.color_mapper)

    def render(self, index):
        document = bokeh.plotting.curdoc()
        if len(self.source.data["x"]) == 0:
            method = "stream"
        else:
            method = "patch"

        print(index)
        for i, data in enumerate(self.iter_images(
                self.loader.lons,
                self.loader.lats,
                self.loader.recordings[index])):
            print(data["image"][0].dtype)
            document.add_next_tick_callback(partial(self.callback, i, data,
                                                    method))

    @gen.coroutine
    def callback(self, i, data, method="stream"):
        if method == "stream":
            self.source.stream(data)
        else:
            patches = {
                "image": [(i, data["image"][0])]
            }
            self.source.patch(patches)

    @staticmethod
    def iter_images(lons, lats, data):
        xr = xarray.DataArray(data, coords=[("y", lats), ("x", lons)], name="Z")
        for x_range, y_range in NewView._quad((-20, 60), (-20, 40)):
            for xx_range, yy_range in NewView._quad(x_range, y_range):
                if min(xx_range) > max(lons):
                    continue
                if min(yy_range) > max(lats):
                    continue
                if min(lons) > max(xx_range):
                    continue
                if min(lats) > max(yy_range):
                    continue
                yield image_data(xr, xx_range, yy_range)

    @staticmethod
    def _quad(x_range, y_range):
        x0, x1 = x_range
        y0, y1 = y_range
        xm = int(sum(x_range) / 2)
        ym = int(sum(y_range) / 2)
        return [
            ((x0, xm), (y0, ym)),
            ((xm, x1), (y0, ym)),
            ((xm, x1), (ym, y1)),
            ((x0, xm), (ym, y1)),
        ]


def main():
    paths = [
        "/scratch/meso/forest/eida50/stage/EIDA50_takm4p4_20200205T0000Z.nc",
        "/scratch/meso/forest/eida50/stage/EIDA50_takm4p4_20200205T0100Z.nc",
        "/scratch/meso/forest/eida50/stage/EIDA50_takm4p4_20200205T0200Z.nc",
        "/scratch/meso/forest/eida50/stage/EIDA50_takm4p4_20200205T0300Z.nc",
        "/scratch/meso/forest/eida50/stage/EIDA50_takm4p4_20200205T0400Z.nc",
        "/scratch/meso/forest/eida50/stage/EIDA50_takm4p4_20200205T0500Z.nc",
        "/scratch/meso/forest/eida50/stage/EIDA50_takm4p4_20200205T0600Z.nc",
        "/scratch/meso/forest/eida50/stage/EIDA50_takm4p4_20200205T0700Z.nc",
        "/scratch/meso/forest/eida50/stage/EIDA50_takm4p4_20200205T0800Z.nc",
        "/scratch/meso/forest/eida50/stage/EIDA50_takm4p4_20200205T0900Z.nc",
        "/scratch/meso/forest/eida50/stage/EIDA50_takm4p4_20200205T1000Z.nc",
        "/scratch/meso/forest/eida50/stage/EIDA50_takm4p4_20200205T1100Z.nc",
        "/scratch/meso/forest/eida50/stage/EIDA50_takm4p4_20200205T1200Z.nc",
    ]
    eida50 = EIDA50(paths)

    # Color mapper
    color_mapper = bokeh.models.LinearColorMapper(
            low=eida50.recordings[0].min(),
            high=eida50.recordings[0].max(),
            palette=bokeh.palettes.Plasma[256])
    color_mapper.nan_color = bokeh.colors.RGB(0, 0, 0, a=0)

    figures = {}
    figures["left"] = bokeh.plotting.figure(
        x_range=(-20, 60),
        y_range=(-20, 40),
        match_aspect=True)

    # Existing solution
    old = OldView(color_mapper, eida50)
    old.add_figure(figures["left"])
    old.render(0)

    # Tiled solution
    figures["right"] = bokeh.plotting.figure(
        x_range=figures["left"].x_range,
        y_range=figures["left"].y_range,
        match_aspect=True)
    new = NewView(color_mapper, eida50)
    new.add_figure(figures["right"])
    # new.render(0)

    # Buttons
    i = 1
    def on_next():
        print("Next")
        nonlocal i
        new.render(i)
        old.render(i)
        i = (i + 1) % len(paths)

    buttons = {}
    buttons["next"] = bokeh.models.Button(label="Next")
    buttons["next"].on_click(on_next)

    document = bokeh.plotting.curdoc()
    document.add_root(
        bokeh.layouts.column(
            bokeh.layouts.row(
                buttons["next"],
                sizing_mode="stretch_width"),
            bokeh.layouts.row(
                figures["left"],
                figures["right"],
                sizing_mode="stretch_width"),
            sizing_mode="stretch_width"
        ))


def image_data(xr, x_range, y_range):
    """Create a tile"""
    canvas = datashader.Canvas(plot_width=256,
                               plot_height=256,
                               x_range=x_range,
                               y_range=y_range)
    xri = canvas.quadmesh(xr)
    image = np.ma.masked_array(xri.values, np.isnan(xri.values))
    image = image.astype(np.float32)  # Reduce bandwith needed to send values
    return {
        "x": [x_range[0]],
        "y": [y_range[0]],
        "dw": [x_range[1] - x_range[0]],
        "dh": [y_range[1] - y_range[0]],
        "image": [image]
    }


if __name__.startswith('bk'):
    main()
