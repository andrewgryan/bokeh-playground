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

    model = Model(
        env.stats_files,
        env.attribute)
    picker.register(model)

    view = TimeSeries(source, label)
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
    model.register(Variables(dropdown))
    dropdown.on_click(model.on_variable)
    dropdowns.append(dropdown)

    dropdown = bokeh.models.Dropdown(
        menu=default_menu,
        label="Metrics")
    model.register(Names(dropdown, "metric_names"))
    dropdown.on_click(model.on_metric)
    dropdowns.append(dropdown)

    dropdown = bokeh.models.Dropdown(
        menu=default_menu,
        label="Regions")
    model.register(Names(dropdown, "area_names"))
    dropdown.on_click(model.on_region)
    dropdowns.append(dropdown)

    profile_figure = bokeh.plotting.figure()
    profile_figure.toolbar_location = "below"

    profile = Profile(figure=profile_figure)
    model.register(profile)

    profile_selection = ProfileSelection(figure=profile_figure)
    model.register(profile_selection)

    leadtime_figure = bokeh.plotting.figure()
    leadtime_figure.toolbar_location = "below"
    leadtime = Leadtime(figure=leadtime_figure)
    model.register(leadtime)

    # Table
    columns = [
        bokeh.models.TableColumn(field="t", title="Time",
                                 formatter=bokeh.models.DateFormatter()),
        bokeh.models.TableColumn(field="y", title="Depth"),
        bokeh.models.TableColumn(field="x", title="Value")
    ]
    table = bokeh.models.DataTable(
        columns=columns,
        source=profile_selection.circle_source,
        width=960)

    # Delete button
    def on_click():
        experiment = model.experiment.strip()
        variable = model.variable.strip()
        region = model.region.strip()
        metric = model.metric.strip()
        variable = model.variable.strip()
        forecast_mode = model.forecast_mode.strip()
        forecast_length = model.forecast_length
        print("Deleting selected statistics:\n")
        print("\t".join([
            experiment,
            variable,
            region,
            metric,
            forecast_mode,
            str(forecast_length)]))
        pts = profile_selection.circle_source.selected.indices
        times = profile_selection.circle_source.data["t"][pts]
        count = 0
        for path in model.paths:
            print("+ editing: {}".format(path))
            with netCDF4.Dataset(path, "r+") as dataset:
                for time in times:
                    print("- deleting: {}".format(time))
                    remove_statistic(
                        dataset,
                        variable,
                        forecast_mode,
                        forecast_length,
                        metric,
                        region,
                        time)
                    count += 1
        print("finished {} deletions".format(count))

    button = bokeh.models.Button(
        label="Delete selected values")
    button.on_click(on_click)

    # Forecast navigation
    dropdown = bokeh.models.Dropdown(
        menu=[("Forecast", "forecast")],
        label="Forecast mode")
    dropdown.on_click(model.on_forecast_mode)
    slider = bokeh.models.Slider(
        start=12,
        end=132,
        value=12,
        step=24,
        title="Forecast length")
    slider.on_change("value", model.on_forecast_length)

    document = bokeh.plotting.curdoc()
    document.title = "CMEMS Product quality statistics"
    document.add_root(bokeh.layouts.row(
        dropdowns,
        sizing_mode="scale_width"))
    document.add_root(bokeh.layouts.row(
        [dropdown, slider],
        sizing_mode="scale_width"))
    document.add_root(figure)
    document.add_root(bokeh.layouts.row(
        profile_figure,
        leadtime_figure,
        sizing_mode="scale_width"))
    document.add_root(bokeh.layouts.column(
        button,
        table,
        sizing_mode="scale_width"))


class Leadtime(object):
    def __init__(self, source=None, figure=None):
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
                model.paths,
                model.variable,
                model.metric,
                model.region)

    def render(
            self,
            paths,
            variable,
            metric,
            region):
        xs, ys = [], []
        for path in paths:
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
                xs.append(x)
                ys.append(y)
        x = np.mean(xs, axis=0)
        y = np.mean(ys, axis=0)
        self.source.data = {
            "x": x,
            "y": y
        }


class Profile(object):
    def __init__(self, source=None, figure=None):
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
        if model.forecast_mode is None:
            return
        if model.forecast_length is None:
            return
        if model.valid():
            self.render(
                model.paths,
                model.variable,
                model.metric,
                model.region,
                model.forecast_mode,
                model.forecast_length)

    def render(self, paths, variable, metric, region, mode, length):
        for path in paths:
            with netCDF4.Dataset(path) as dataset:
                var = dataset.variables[variable]
                if "surface" in var.dimensions:
                    y = [0]
                else:
                    y = dataset.variables["depths"][:]
                x = read(
                    dataset,
                    variable,
                    metric,
                    region,
                    mode,
                    length)
                x = x.mean(axis=0)
                self.source.data = {
                    "x": x,
                    "y": y
                }
            break


class ProfileSelection(object):
    def __init__(self,
                 figure=None,
                 multiline_glyph=None,
                 circle_glyph=None):
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
                "region",
                "forecast_mode",
                "forecast_length"]]):
            self.render(
                model.paths,
                model.variable,
                model.metric,
                model.region,
                model.forecast_mode,
                model.forecast_length,
                model.times)

    def render(self,
               paths,
               variable,
               metric,
               region,
               forecast_mode,
               forecast_length,
               times):
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

        for path in paths:
            with netCDF4.Dataset(path) as dataset:
                var = dataset.variables[variable]
                if "surface" in var.dimensions:
                    z = np.array([0])
                else:
                    z = dataset.variables["depths"][:]
                    z[np.isinf(z)] = 2000.
                fi = (
                    (dataset.variables["forecasts"][:] == forecast_length) &
                    (read_names(dataset, "forecast_names") == forecast_mode))
                mi = index(dataset.variables["metric_names"][:], metric)
                ai = index(dataset.variables["area_names"][:], region)
                dataset_times = netCDF4.num2date(
                    dataset.variables["time"][:],
                    units=dataset.variables["time"].units)
                ti = time_mask(dataset_times, times)
                lines = var[ti, fi, :, mi, ai]
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
    def __init__(self, stats_files, netcdf_attribute):
        self.stats_files = stats_files
        self.netcdf_attribute = netcdf_attribute
        self.experiment = None
        self.metric = None
        self.variable = None
        self.region = None
        self.times = None
        self.forecast_mode = None
        self.forecast_length = None
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

    def on_forecast_length(self, attr, old, new):
        self.forecast_length = new
        self.notify(self)

    def on_forecast_mode(self, value):
        self.forecast_mode = value
        self.notify(self)

    def update(self, times):
        self.times = times
        self.notify(self)

    @property
    def paths(self):
        return select(
            self.stats_files,
            self.netcdf_attribute,
            self.experiment)

    def valid(self):
        for attr in ["experiment", "metric", "variable", "region"]:
            if getattr(self, attr) is None:
                return False
        return True


class Variables(object):
    def __init__(self, dropdown):
        self.dropdown = dropdown

    def update(self, model):
        if model.experiment is None:
            return
        items = find_variables(model.paths)
        menu = [(item.strip(), item) for item in items]
        self.dropdown.menu = menu


class Names(object):
    def __init__(self, dropdown, variable):
        self.dropdown = dropdown
        self.variable = variable

    def update(self, model):
        if model.experiment is None:
            return
        items = find_names(model.paths, self.variable)
        menu = [(item.strip(), item) for item in items]
        self.dropdown.menu = menu


class TimeSeries(object):
    def __init__(self,
                 source,
                 label):
        self.source = source
        self.label = label

    def update(self, model):
        if model.valid() and (model.forecast_length is not None):
            self.render(model)

    def render(self, model):
        try:
            x, y = self.read(
                model.paths,
                model.variable,
                model.metric,
                model.region,
                model.forecast_mode,
                model.forecast_length)
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

    @staticmethod
    def read(paths, variable, metric, area, forecast_mode, forecast_length):
        ys = []
        xs = []
        for path in paths:
            with netCDF4.Dataset(path) as dataset:
                print("reading: {}".format(path))
                var = dataset.variables["time"]
                times = netCDF4.num2date(var[:], units=var.units)
                values = read(
                    dataset,
                    variable,
                    metric,
                    area,
                    forecast_mode,
                    forecast_length)[:, 0]
            xs.append(times)
            ys.append(values)
        x = np.ma.concatenate(xs)
        y = np.ma.concatenate(ys)
        return x, y


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
        for attr in ["variable", "metric", "region", "forecast_mode", "forecast_length"]:
            if getattr(model, attr) is None:
                continue
            words.append(str(getattr(model, attr)).strip())
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


def select(paths, attr, value):
    for path in paths:
        # Note: continue statement used to close Dataset prior to yield
        with netCDF4.Dataset(path) as dataset:
            if getattr(dataset, attr) != value:
                continue
        yield path


def index(chars, item):
    strings = netCDF4.chartostring(chars)
    items = [s.strip() for s in strings]
    return items.index(item.strip())


def remove_statistic(
        dataset,
        variable,
        forecast_mode,
        forecast_length,
        metric,
        area,
        time):
    var = dataset.variables["time"]
    ti = netCDF4.num2date(var[:], units=var.units) == time
    fi = (
        (dataset.variables["forecasts"][:] == forecast_length) &
        (read_names(dataset, "forecast_names") == forecast_mode))
    mi = read_names(dataset, "metric_names") == metric
    ai = read_names(dataset, "area_names") == area
    pts = (ti, fi, slice(None), mi, ai)
    values = dataset.variables[variable][pts]
    dataset.variables[variable][pts] = np.ma.masked_all_like(values)


def read_names(dataset, variable):
    return np.char.strip(netCDF4.chartostring(dataset.variables[variable][:]))


def read(dataset, variable, metric, area, forecast_mode, forecast_length):
    mi = index(dataset.variables["metric_names"][:], metric)
    ai = index(dataset.variables["area_names"][:], area)
    fi = (
        (dataset.variables["forecasts"][:] == forecast_length) &
        (read_names(dataset, "forecast_names") == forecast_mode))
    return dataset.variables[variable][:, fi, :, mi, ai]


if __name__.startswith('bk'):
    main()
