import bokeh.plotting
import bokeh.models
import bokeh.layouts
import netCDF4
import numpy as np
import glob


STATS_FILES = sorted(glob.glob("/scratch/oceanver/class4/copernicus/*/stats/product_quality_*.nc"))


def main():
    figure = bokeh.plotting.figure(
        x_axis_type="datetime",
        plot_width=1200,
        plot_height=300)
    figure.toolbar_location = "below"
    hover_tool = bokeh.models.HoverTool(
        tooltips=[
            ('date', '@x{%F}'),
            ('value', '@y')
        ],
        formatters={'x': 'datetime'},
    )
    figure.add_tools(hover_tool)
    source = bokeh.models.ColumnDataSource({
        "x": [],
        "y": []
    })
    figure.line(x="x", y="y", source=source)
    figure.circle(x="x", y="y", source=source)

    dropdowns = []

    model = Model()

    view = View(source)
    model.register(view)

    title = Title(figure)
    model.register(title)

    items = find_attributes(STATS_FILES, "product")
    menu = [(item.strip(), item) for item in items]
    dropdown = bokeh.models.Dropdown(menu=menu, label="Products")
    dropdown.on_click(model.on_experiment)
    dropdowns.append(dropdown)

    items = find_variables(STATS_FILES)
    menu = [(item.strip(), item) for item in items]
    dropdown = bokeh.models.Dropdown(menu=menu, label="Variables")
    dropdown.on_click(model.on_variable)
    dropdowns.append(dropdown)

    items = find_names(STATS_FILES, "metric_names")
    menu = [(item.strip(), item) for item in items]
    dropdown = bokeh.models.Dropdown(menu=menu, label="Metrics")
    dropdown.on_click(model.on_metric)
    dropdowns.append(dropdown)

    items = find_names(STATS_FILES, "area_names")
    menu = [(item.strip(), item) for item in items]
    dropdown = bokeh.models.Dropdown(menu=menu, label="Regions")
    dropdown.on_click(model.on_region)
    dropdowns.append(dropdown)

    row = bokeh.layouts.row(dropdowns)
    root = bokeh.layouts.column(row, figure)
    document = bokeh.plotting.curdoc()
    document.add_root(root)


class Model(object):
    def __init__(self):
        self.experiment = None
        self.metric = None
        self.variable = None
        self.region = None
        self.subscribers = []

    def register(self, subscriber):
        self.subscribers.append(subscriber)

    def on_experiment(self, value):
        self.experiment = value
        self.notify()

    def on_metric(self, value):
        self.metric = value
        self.notify()

    def on_variable(self, value):
        self.variable = value
        self.notify()

    def on_region(self, value):
        self.region = value
        self.notify()

    def notify(self):
        for subscriber in self.subscribers:
            subscriber.notify(self)


class View(object):
    def __init__(self, source):
        self.source = source

    def notify(self, model):
        if self.valid(model):
            self.render(model)

    def valid(self, model):
        for attr in ["experiment", "metric", "variable", "region"]:
            if getattr(model, attr) is None:
                return False
        return True

    def render(self, model):
        x, y = read(select(STATS_FILES, "product", model.experiment),
                    model.variable,
                    model.metric,
                    model.region)
        self.source.data = {
            "x": x,
            "y": y
        }


class Title(object):
    def __init__(self, figure):
        self.figure = figure
        self.title = bokeh.models.Title(text_font_size="12pt")
        self.suptitle = bokeh.models.Title(text_font_style="italic")
        self.figure.add_layout(self.suptitle, "above")
        self.figure.add_layout(self.title, "above")

    def notify(self, model):
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
