import bokeh.plotting
import bokeh.models
import bokeh.layouts
import netCDF4
import numpy as np
import glob
import os


class MissingEnvironmentVariable(Exception):
    pass


class Environment(object):
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)


def parse_env():
    return Environment(
        stats_files=parse_env_variable("STATS_FILES", nargs="+"),
        attribute=parse_env_variable("ATTRIBUTE", default="product")
    )


def parse_env_variable(variable, nargs=None, default=None):
    if variable not in os.environ:
        if default is None:
            message = "'{}' environment variable not set".format(variable)
            raise MissingEnvironmentVariable(message)
        else:
            return default
    value = os.getenv(variable)
    if nargs == "+":
        return value.split()
    else:
        return value


class Observable(object):
    def __init__(self):
        self.subscribers = []

    def register(self, subscriber):
        self.subscribers.append(subscriber)

    def notify(self, message):
        for subscriber in self.subscribers:
            subscriber.update(message)


class TimePicker(Observable):
    def __init__(self, source):
        self.source = source
        super().__init__()

    def on_selection_change(self, attr, old, new):
        times = self.source.data['x'][new]
        print(times, self.subscribers)
        self.notify(times)


def main():
    env = parse_env()

    figure = bokeh.plotting.figure(
        tools='pan,xwheel_zoom,box_zoom,save,reset,help',
        x_axis_type="datetime",
        plot_width=960,
        plot_height=300)
    figure.toolbar_location = "above"
    hover_tool = bokeh.models.HoverTool(
        tooltips=[
            ('date', '@x{%F}'),
            ('value', '@y')
        ],
        formatters={'x': 'datetime'},
        mode="vline"
    )
    figure.add_tools(hover_tool)
    source = bokeh.models.ColumnDataSource({
        "x": [],
        "y": []
    })

    picker = TimePicker(source)
    source.selected.on_change("indices", picker.on_selection_change)

    figure.line(x="x", y="y", source=source)
    circles = figure.circle(
        x="x", y="y", source=source,
        hover_fill_color="red",
        hover_line_color="red")
    circles.selection_glyph = bokeh.models.Square(
        fill_color="red",
        line_color="red")
    label = bokeh.models.Label(
        x=figure.plot_width / 2,
        y=figure.plot_height / 3,
        text="",
        x_units="screen",
        y_units="screen")
    figure.add_layout(label)

    tool = bokeh.models.BoxSelectTool()
    figure.add_tools(tool)

    dropdowns = []

    model = Model()
    picker.register(model)

    view = View(
        env.stats_files,
        env.attribute,
        source,
        label)
    model.register(view)

    title = Title(figure)
    model.register(title)

    default_menu = [("Select PRODUCT", "")]

    items = find_attributes(env.stats_files, env.attribute)
    menu = [(item.strip(), item) for item in items]
    dropdown = bokeh.models.Dropdown(menu=menu, label="Products")
    dropdown.on_click(model.on_experiment)
    dropdowns.append(dropdown)

    dropdown = bokeh.models.Dropdown(
        menu=default_menu,
        label="Variables")
    model.register(Variables(
        env.stats_files,
        env.attribute,
        dropdown))
    dropdown.on_click(model.on_variable)
    dropdowns.append(dropdown)

    dropdown = bokeh.models.Dropdown(
        menu=default_menu,
        label="Metrics")
    model.register(Names(
        env.stats_files,
        env.attribute,
        dropdown,
        "metric_names"))
    dropdown.on_click(model.on_metric)
    dropdowns.append(dropdown)

    dropdown = bokeh.models.Dropdown(
        menu=default_menu,
        label="Regions")
    model.register(Names(
        env.stats_files,
        env.attribute,
        dropdown,
        "area_names"))
    dropdown.on_click(model.on_region)
    dropdowns.append(dropdown)

    profile_figure = bokeh.plotting.figure()
    profile_figure.toolbar_location = "below"

    profile = Profile(env.stats_files, figure=profile_figure)
    model.register(profile)

    profile_selection = ProfileSelection(
        env.stats_files,
        env.attribute,
        figure=profile_figure)
    model.register(profile_selection)

    leadtime_figure = bokeh.plotting.figure()
    leadtime_figure.toolbar_location = "below"
    leadtime = Leadtime(env.stats_files, figure=leadtime_figure)
    model.register(leadtime)

    row = bokeh.layouts.row(dropdowns, sizing_mode="scale_width")
    document = bokeh.plotting.curdoc()
    document.title = "CMEMS Product quality statistics"
    document.add_root(row)
    document.add_root(figure)
    document.add_root(bokeh.layouts.row(
        profile_figure,
        leadtime_figure,
        sizing_mode="scale_width"))


class Leadtime(object):
    def __init__(self, stats_files, source=None, figure=None):
        self.stats_files = stats_files
        if source is None:
            source = bokeh.models.ColumnDataSource({
                "x": [],
                "y": []
            })
        self.source = source
        if figure is None:
            figure = bokeh.plotting.figure()
        self.figure = figure
        self.figure.line(x="x", y="y", source=source)
        self.figure.circle(x="x", y="y", source=source)

    def update(self, model):
        if model.valid():
            self.render(
                model.variable,
                model.metric,
                model.region)

    def render(self, variable, metric, region):
        for path in self.stats_files:
            with netCDF4.Dataset(path) as dataset:
                mi = index(dataset.variables["metric_names"][:], metric)
                ai = index(dataset.variables["area_names"][:], region)
                names = np.char.strip(
                    netCDF4.chartostring(
                        dataset.variables["forecast_names"][:]))
                fi = names == "forecast"
                y = dataset.variables[variable][:, fi, :, mi, ai]
                y = y.mean(axis=(0, 2))
                x = dataset.variables["forecasts"][fi]
                self.source.data = {
                    "x": x,
                    "y": y
                }
            break


class Profile(object):
    def __init__(self, stats_files, source=None, figure=None):
        self.stats_files = stats_files
        if source is None:
            source = bokeh.models.ColumnDataSource({
                "x": [],
                "y": []
            })
        self.source = source
        if figure is None:
            figure = bokeh.plotting.figure()
        self.figure = figure
        self.figure.y_range.flipped = True
        self.figure.line(x="x", y="y", source=source)
        self.figure.circle(x="x", y="y", source=source)

    def update(self, model):
        if model.valid():
            self.render(
                model.variable,
                model.metric,
                model.region)

    def render(self, variable, metric, region):
        for path in self.stats_files:
            with netCDF4.Dataset(path) as dataset:
                var = dataset.variables[variable]
                if "surface" in var.dimensions:
                    y = [0]
                else:
                    y = dataset.variables["depths"][:]
                mi = index(dataset.variables["metric_names"][:], metric)
                ai = index(dataset.variables["area_names"][:], region)
                x = var[:, 0, :, mi, ai]
                x = x.mean(axis=0)
                self.source.data = {
                    "x": x,
                    "y": y
                }
            break


class ProfileSelection(object):
    def __init__(self,
                 stats_files,
                 netcdf_attribute,
                 figure=None,
                 multiline_glyph=None,
                 circle_glyph=None):
        self.stats_files = stats_files
        self.netcdf_attribute = netcdf_attribute
        if figure is None:
            figure = bokeh.plotting.figure()
        self.figure = figure
        self.circle_source = bokeh.models.ColumnDataSource({
            "x": [],
            "y": [],
            "t": []
        })
        self.multiline_source = bokeh.models.ColumnDataSource({
            "xs": [],
            "ys": []
        })
        if multiline_glyph is None:
            multiline_glyph = bokeh.models.MultiLine(
                xs="xs",
                ys="ys",
                line_color="red")
        self.multiline_glyph = multiline_glyph
        self.figure.add_glyph(
            self.multiline_source,
            self.multiline_glyph)
        if circle_glyph is None:
            self.circle_glyph = bokeh.models.Circle(
                x="x",
                y="y",
                fill_color="red")
        else:
            self.circle_glyph = circle_glyph
        circle_renderer = self.figure.add_glyph(
            self.circle_source,
            self.circle_glyph)
        hover_tool = bokeh.models.HoverTool(
            tooltips=[
                ('value', '@x'),
                ('depth', '@y'),
                ('time', '@t{%F}')
            ],
            formatters={'t': 'datetime'},
            renderers=[circle_renderer]
        )
        self.figure.add_tools(hover_tool)

    def update(self, model):
        if all([getattr(model, attr) is not None for attr in [
                "times",
                "variable",
                "metric",
                "region"]]):
            self.render(
                model.experiment,
                model.variable,
                model.metric,
                model.region,
                model.times)

    def render(self, experiment, variable, metric, region, times):
        if len(times) == 0:
            self.multiline_source.data = {
                "xs": [],
                "ys": []
            }
            self.circle_source.data = {
                "x": [],
                "y": [],
                "t": []
            }
            return

        for path in select(
                self.stats_files,
                self.netcdf_attribute,
                experiment):
            with netCDF4.Dataset(path) as dataset:
                var = dataset.variables[variable]
                if "surface" in var.dimensions:
                    z = np.array([0])
                else:
                    z = dataset.variables["depths"][:]
                    z[np.isinf(z)] = 2000.
                mi = index(dataset.variables["metric_names"][:], metric)
                ai = index(dataset.variables["area_names"][:], region)
                dataset_times = netCDF4.num2date(
                    dataset.variables["time"][:],
                    units=dataset.variables["time"].units)
                ti = time_mask(dataset_times, times)
                lines = var[ti, 0, :, mi, ai]
                xs, ys = [], []
                for line in lines:
                    xs.append(line.tolist())
                    ys.append(z.tolist())
                x = np.ma.asarray(xs).flatten()
                y = np.ma.asarray(ys).flatten()
                t = np.repeat(dataset_times[ti], len(z))
                self.multiline_source.data = {
                    "xs": xs,
                    "ys": ys
                }
                self.circle_source.data = {
                    "x": x,
                    "y": y,
                    "t": t
                }
            break


def time_mask(time_axis, times):
    if isinstance(time_axis, list):
        time_axis = np.array(time_axis, dtype=object)
    if len(times) == 0:
        return np.zeros_like(time_axis, dtype=np.bool)
    elif len(times) == 1:
        return time_axis == times[0]
    else:
        return np.logical_or.reduce([time_axis == t for t in times])


class Model(Observable):
    def __init__(self):
        self.experiment = None
        self.metric = None
        self.variable = None
        self.region = None
        self.times = None
        super().__init__()

    def on_experiment(self, value):
        self.experiment = value
        self.notify(self)

    def on_metric(self, value):
        self.metric = value
        self.notify(self)

    def on_variable(self, value):
        self.variable = value
        self.notify(self)

    def on_region(self, value):
        self.region = value
        self.notify(self)

    def update(self, times):
        print("update", times)
        self.times = times
        self.notify(self)

    def valid(self):
        for attr in ["experiment", "metric", "variable", "region"]:
            if getattr(self, attr) is None:
                return False
        return True


class Variables(object):
    def __init__(self,
                 stats_files,
                 netcdf_attribute,
                 dropdown):
        self.stats_files = stats_files
        self.netcdf_attribute = netcdf_attribute
        self.dropdown = dropdown

    def update(self, model):
        if model.experiment is None:
            return
        items = find_variables(select(
            self.stats_files,
            self.netcdf_attribute,
            model.experiment))
        menu = [(item.strip(), item) for item in items]
        self.dropdown.menu = menu


class Names(object):
    def __init__(self,
                 stats_files,
                 netcdf_attribute,
                 dropdown,
                 variable):
        self.stats_files = stats_files
        self.netcdf_attribute = netcdf_attribute
        self.dropdown = dropdown
        self.variable = variable

    def update(self, model):
        if model.experiment is None:
            return
        items = find_names(select(
            self.stats_files,
            self.netcdf_attribute,
            model.experiment), self.variable)
        menu = [(item.strip(), item) for item in items]
        self.dropdown.menu = menu


class View(object):
    def __init__(self,
                 stats_files,
                 netcdf_attribute,
                 source,
                 label):
        self.stats_files = stats_files
        self.netcdf_attribute = netcdf_attribute
        self.source = source
        self.label = label

    def update(self, model):
        if model.valid():
            self.render(model)

    def render(self, model):
        try:
            x, y = read(select(
                self.stats_files,
                self.netcdf_attribute,
                model.experiment),
                        model.variable,
                        model.metric,
                        model.region)
            self.source.data = {
                "x": x,
                "y": y
            }
            self.label.text = ""
        except (KeyError, ValueError):
            self.source.data = {
                "x": [],
                "y": []
            }
            self.label.text = "Invalid menu combination"


class Title(object):
    def __init__(self, figure):
        self.figure = figure
        self.title = bokeh.models.Title(text_font_size="12pt")
        self.suptitle = bokeh.models.Title(text_font_style="italic")
        self.figure.add_layout(self.suptitle, "above")
        self.figure.add_layout(self.title, "above")

    def update(self, model):
        self.render(model)

    def render(self, model):
        words = []
        for attr in ["experiment"]:
            if getattr(model, attr) is None:
                continue
            words.append(getattr(model, attr).strip())
        self.title.text = "\n".join(words)
        words = []
        for attr in ["variable", "metric", "region"]:
            if getattr(model, attr) is None:
                continue
            words.append(getattr(model, attr).strip())
        self.suptitle.text = "\n".join(words)


def find_names(paths, variable):
    metrics = []
    for path in paths:
        with netCDF4.Dataset(path) as dataset:
            chars = dataset.variables[variable][:]
            names = netCDF4.chartostring(chars)
            for name in names:
                if name not in metrics:
                    metrics.append(name)
    return metrics


def find_attributes(paths, attr):
    values = []
    for path in paths:
        with netCDF4.Dataset(path) as dataset:
            if not hasattr(dataset, attr):
                continue
            value = getattr(dataset, attr)
            if value not in values:
                values.append(value)
    return values


def find_variables(paths):
    variables = []
    for path in paths:
        with netCDF4.Dataset(path) as dataset:
            for variable in dataset.variables:
                if variable.startswith("stats_"):
                    if variable not in variables:
                        variables.append(variable)
    return variables


def read_forecasts(dataset):
    return dataset.variables["forecasts"][:]


def read_forecast_names(dataset):
    var = dataset.variables["forecast_names"]
    return netCDF4.chartostring(var[:])


def select(paths, attr, value):
    for path in paths:
        with netCDF4.Dataset(path) as dataset:
            if getattr(dataset, attr) == value:
                yield path


def read(paths, variable, metric, area):
    ys = []
    xs = []
    for path in paths:
        with netCDF4.Dataset(path) as dataset:
            print("reading: {}".format(path))
            var = dataset.variables["time"]
            times = netCDF4.num2date(var[:], units=var.units)
            mi = index(dataset.variables["metric_names"][:], metric)
            ai = index(dataset.variables["area_names"][:], area)
            values = dataset.variables[variable][:, 0, 0, mi, ai]
        xs.append(times)
        ys.append(values)
    x = np.ma.concatenate(xs)
    y = np.ma.concatenate(ys)
    return x, y


def index(chars, item):
    strings = netCDF4.chartostring(chars)
    items = [s.strip() for s in strings]
    return items.index(item.strip())


if __name__.startswith('bk'):
    main()
