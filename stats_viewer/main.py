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

    metrics = []
    for path in STATS_FILES:
        with netCDF4.Dataset(path) as dataset:
            chars = dataset.variables["metric_names"][:]
            names = netCDF4.chartostring(chars)
            for name in names:
                if name not in metrics:
                    metrics.append(name)
    menu = [(item.strip(), item) for item in metrics]
    dropdown = bokeh.models.Dropdown(menu=menu)
    dropdown.on_click(select_metric(source))
    dropdown.on_click(set_title(figure))

    root = bokeh.layouts.column(dropdown, figure)
    document = bokeh.plotting.curdoc()
    document.add_root(root)

def select_metric(source):
    def wrapper(new):
        print(new)
        x, y = read_metric(new)
        source.data = {
            "x": x,
            "y": y
        }
    return wrapper


def set_title(figure):
    def wrapper(new):
        figure.title.text = new
    return wrapper


def read_metric(metric):
    ys = []
    xs = []
    for path in STATS_FILES:
        with netCDF4.Dataset(path) as dataset:
            print("reading: {}".format(path))
            var = dataset.variables["time"]
            times = netCDF4.num2date(var[:], units=var.units)
            strings = netCDF4.chartostring(dataset.variables["metric_names"][:])
            metrics = [s.strip() for s in strings]
            mi = metrics.index(metric.strip())
            values = dataset.variables["stats_sst_all"][:, 0, 0, mi, 0]
        xs.append(times)
        ys.append(values)
    x = np.ma.concatenate(xs)
    y = np.ma.concatenate(ys)
    return x, y


if __name__.startswith('bk'):
    main()
