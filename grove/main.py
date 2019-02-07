import argparse
import bokeh.plotting
import bokeh.models
import bokeh.palettes
import bokeh.colors
import cartopy
import numpy as np
import netCDF4


GOOGLE = cartopy.crs.Mercator.GOOGLE
PLATE_CARREE = cartopy.crs.PlateCarree()


def parse_args(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("paths", nargs="+")
    return parser.parse_args(args=argv)


def main():
    args = parse_args()
    x_range, y_range = google_mercator([-180, 180], [-80, 80])
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

    # Plot Class 4 positions
    source = bokeh.models.ColumnDataSource({
        "x": [],
        "y": [],
        "v": []
    })
    color_mapper = bokeh.models.LinearColorMapper(
        palette=bokeh.palettes.Plasma[256],
        nan_color=bokeh.colors.RGB(0, 0, 0, a=0),
    )
    view = View(args.paths, source, color_mapper, figure)
    figure.circle(
        x="x",
        y="y",
        source=source,
        color={"field": "v", "transform": color_mapper},
        line_color={"field": "v", "transform": color_mapper})
    color_bar = bokeh.models.ColorBar(
        color_mapper=color_mapper,
        orientation='horizontal',
        background_fill_alpha=0,
        location='bottom_center',
        major_tick_line_color='black',
        bar_line_color='black')
    figure.add_layout(color_bar, 'center')

    widgets = []
    check_box = bokeh.models.CheckboxGroup(labels=["quality control"])
    check_box.on_change('active', view.on_change_quality)
    widgets.append(check_box)

    radio_group = bokeh.models.RadioGroup(labels=view.fields)
    radio_group.on_change('active', view.on_change_field)
    widgets.append(radio_group)

    radio_group = bokeh.models.RadioGroup(labels=view.models)
    radio_group.on_change('active', view.on_change_model)
    widgets.append(radio_group)

    controls = bokeh.layouts.column(*widgets, name="hello")

    second_figure = bokeh.plotting.figure(
        name="hello",
        plot_width=300,
        plot_height=300)
    line_source = bokeh.models.ColumnDataSource({
        "x": [],
        "y": []})
    second_figure.line(x="x", y="y", source=line_source)
    second_figure.toolbar.logo = None
    second_figure.toolbar_location = None
    second_figure.min_border_left = 20
    second_figure.min_border_right = 20
    second_figure.border_fill_alpha = 0

    def on_change(attr, old, new):
        values = np.ma.copy(source.data["v"]).compressed()
        values.sort()
        line_source.data = {
            "x": np.arange(len(values)),
            "y": values
        }
    source.on_change("data", on_change)

    document = bokeh.plotting.curdoc()
    document.title = "Geo-relational ocean verification exploration tool"
    document.add_root(figure)
    document.add_root(second_figure)
    document.add_root(controls)

def categorise(paths):
    pass

class Line(object):
    def __init__(self, models):
        self.models = models

    def render(self):
        pass


class View(object):
    def __init__(self, paths, source, color_mapper, figure):
        self.model = None
        self.field = None
        self.paths = paths
        self.source = source
        self.color_mapper = color_mapper
        self.figure = figure
        self.store = {}
        for path in self.paths:
            with netCDF4.Dataset(path) as dataset:
                key = " ".join([
                    dataset.system,
                    dataset.version,
                    dataset.configuration])
                self.store[key] = path
        self.models = list(sorted(self.store.keys()))
        self.fields = ["observation", "forecast", "forecast - observation"]
        self.quality_control = False

    def on_change_field(self, attr, old, new):
        self.field = self.fields[new]
        self.render()

    def on_change_quality(self, attr, old, new):
        self.quality_control = 0 in new
        self.render()

    def on_change_model(self, attr, old, new):
        self.model = self.models[new]
        self.render()

    def render(self):
        if self.field is None:
            return
        if self.model is None:
            return
        path = self.store[self.model]
        print(path, self.field)
        with netCDF4.Dataset(path) as dataset:
            lats = dataset.variables["latitude"][:]
            lons = dataset.variables["longitude"][:]
            if self.field == "forecast - observation":
                f = dataset.variables["forecast"][:, 0, 0, 0]
                o = dataset.variables["observation"][:, 0, 0]
                v = f - o
            elif self.field == "forecast":
                v = dataset.variables["forecast"][:, 0, 0, 0]
            elif self.field == "observation":
                v = dataset.variables["observation"][:, 0, 0]
            else:
                raise Exception("unknown field: {}".format(self.field))
            if self.quality_control:
                flags = dataset.variables["qc"][:, 0, 0]
                pts = np.ma.where(flags == 0)
                lons = lons[pts]
                lats = lats[pts]
                v = v[pts]
        x, y = google_mercator(lons, lats)

        # Geographic filtering
        pts = np.ma.where(
            (x >= self.figure.x_range.start) &
            (x <= self.figure.x_range.end) &
            (y >= self.figure.y_range.start) &
            (y <= self.figure.y_range.end))
        x = x[pts]
        y = y[pts]
        v = v[pts]

        self.source.data = {
            "x": x,
            "y": y,
            "v": v
        }
        self.color_mapper.low = v.min()
        self.color_mapper.high = v.max()


def google_mercator(lons, lats):
    return transform(PLATE_CARREE, GOOGLE, lons, lats)


def plate_carree(x, y):
    return transform(GOOGLE, PLATE_CARREE, x, y)


def transform(src_crs, dst_crs, x, y):
    x, y = np.asarray(x), np.asarray(y)
    xt, yt, _ = dst_crs.transform_points(src_crs, x.flatten(), y.flatten()).T
    return xt, yt


if __name__.startswith("bk"):
    main()
