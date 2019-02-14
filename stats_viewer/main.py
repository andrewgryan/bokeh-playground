import bokeh.plotting
import bokeh.models
import bokeh.layouts
import netCDF4
import numpy as np
import glob


STATS_FILES = sorted(glob.glob("/scratch/oceanver/class4/copernicus/glo/stats/product_quality_stats_GLOBAL_ANALYSIS_FORECAST_PHYS_001_015_*.nc"))


def main():
    figure = bokeh.plotting.figure(
        x_axis_type="datetime",
        plot_width=800,
        plot_height=200)
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

    view = View(source)

    items = find_variables(STATS_FILES)
    menu = [(item.strip(), item) for item in items]
    dropdown = bokeh.models.Dropdown(menu=menu, label="Variables")
    dropdown.on_click(view.on_variable)
    dropdowns.append(dropdown)

    items = find_names(STATS_FILES, "metric_names")
    menu = [(item.strip(), item) for item in items]
    dropdown = bokeh.models.Dropdown(menu=menu, label="Metrics")
    dropdown.on_click(view.on_metric)
    dropdown.on_click(set_title(figure))
    dropdowns.append(dropdown)

    items = find_names(STATS_FILES, "area_names")
    menu = [(item.strip(), item) for item in items]
    dropdown = bokeh.models.Dropdown(menu=menu, label="Regions")
    dropdown.on_click(view.on_region)
    dropdowns.append(dropdown)

    row = bokeh.layouts.row(dropdowns)
    root = bokeh.layouts.column(row, figure)
    document = bokeh.plotting.curdoc()
    document.add_root(root)


class View(object):
    def __init__(self, source):
        self.source = source
        self.metric = None
        self.variable = None
        self.region = None

    def on_metric(self, value):
        self.metric = value
        self.render()

    def on_variable(self, value):
        self.variable = value
        self.render()

    def on_region(self, value):
        self.region = value
        self.render()

    def render(self):
        if self.metric is None:
            return
        if self.variable is None:
            return
        if self.region is None:
            return
        x, y = read(self.variable, self.metric, self.region)
        self.source.data = {
            "x": x,
            "y": y
        }


def set_title(figure):
    def wrapper(new):
        figure.title.text = new
    return wrapper


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

def find_variables(paths):
    variables = []
    for path in paths:
        with netCDF4.Dataset(path) as dataset:
            for variable in dataset.variables:
                if variable.startswith("stats_"):
                    if variable not in variables:
                        variables.append(variable)
    return variables


def read(variable, metric, area):
    ys = []
    xs = []
    for path in STATS_FILES:
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
