import numpy as np
import data
import datetime as dt
import bokeh.plotting
import bokeh.layouts


FORMAT = "%Y-%m-%d %H:%M"


def main():
    div = bokeh.models.Div()

    model_times = ModelTimes()
    model_times.render()

    document = bokeh.plotting.curdoc()
    document.add_root(
            bokeh.layouts.column(
                model_times.layout,
                div,
                sizing_mode="stretch_width"))


class ModelTimes(object):
    def __init__(self):
        self.name = None
        self.run_times = []
        self.valid_time = None
        self.valid_times = []
        self.variables = []
        self.pressures = []
        self.units = "YYYYMMDD"

        self.dropdowns = {}
        dropdown = bokeh.models.Dropdown(
                label="Model",
                menu=menu(data.MODEL_NAMES))
        dropdown.on_change("value", self.on_name)
        dropdown.on_change("value", select(dropdown))
        self.dropdowns["name"] = dropdown

        dropdown = bokeh.models.Dropdown(
                label="Initial time")
        dropdown.on_change("value", self.on_run)
        dropdown.on_change("value", select(dropdown))
        self.dropdowns["run"] = dropdown

        dropdown = bokeh.models.Dropdown(
                label="Variable")
        dropdown.on_change("value", self.on_variable)
        dropdown.on_change("value", select(dropdown))
        self.dropdowns["variable"] = dropdown

        dropdown = bokeh.models.Dropdown(
                label="Pressure")
        dropdown.on_change("value", self.on_pressure)
        dropdown.on_change("value", select(dropdown))
        self.dropdowns["pressure"] = dropdown

        dropdown = bokeh.models.Dropdown(
                label="Valid time")
        dropdown.on_change("value", self.on_valid)
        dropdown.on_change("value", select(dropdown))
        self.dropdowns["valid"] = dropdown

        dropdown = bokeh.models.Dropdown(
                label="Time format",
                menu=menu(["YYYYMMDD", "T+"]))
        dropdown.on_change("value", self.on_unit)
        dropdown.on_change("value", select(dropdown))
        self.dropdowns["unit"] = dropdown

        self.layout = bokeh.layouts.column(
                bokeh.layouts.row(
                    self.dropdowns["name"],
                    self.dropdowns["variable"],
                    self.dropdowns["run"],
                    self.dropdowns["valid"],
                    self.dropdowns["unit"],
                    self.dropdowns["pressure"],
                    sizing_mode="stretch_width"),
                sizing_mode="stretch_width")

    def on_run(self, attr, old, new):
        print(new)
        valid_dropdown = self.dropdowns["valid"]
        valid_dropdown.menu = [("loading", "loading")]
        time = to_time(new)
        path = data.PATHS[(self.name, time)]
        self.valid_times = data.valid_times(path)
        self.render()

    def on_valid(self, attr, old, new):
        values = [v for _, v in self.dropdowns["valid"].menu]
        i = values.index(new)
        self.valid_time = self.valid_times[i]
        print(self.valid_time)

    def on_name(self, attr, old, new):
        print(new)
        self.name = new
        self.run_times = data.RUN_TIMES[self.name]
        self.valid_times = []
        self.render()

    def on_variable(self, attr, old, new):
        print(new)
        self.variable = new
        if self.name is not None:
            self.valid_times = []
        self.render()

    def on_pressure(self, attr, old, new):
        print(new)

    def on_unit(self, attr, old, new):
        print(new)
        self.units = new
        self.render()

    def render(self):
        if len(self.run_times) == 0:
            labels = [("Select model")]
        else:
            labels = [to_stamp(t) for t in self.run_times]
        self.dropdowns["run"].menu = menu(labels)
        if len(self.valid_times) == 0:
            labels = [("Select initial time")]
        else:
            if self.units == "T+":
                lengths = to_lengths(self.valid_times)
                labels = [
                        format_length(l) for l in lengths]
            else:
                times = self.valid_times
                labels = [
                        to_stamp(t) for t in times]
        dropdown = self.dropdowns["valid"]
        dropdown.menu = menu(labels)

        if self.valid_time is not None:
            if self.units == "T+":
                t0 = np.datetime64(self.valid_times[0], 's')
                t1 = np.datetime64(self.valid_time, 's')
                length = (t1 - t0).astype('timedelta64[h]')
                label = format_length(length)
            else:
                label = to_stamp(self.valid_time)
            self.dropdowns["valid"].label = label

        if len(self.variables) == 0:
            self.dropdowns["variable"].menu = menu(["Select model"])
        if len(self.pressures) == 0:
            self.dropdowns["pressure"].menu = menu(["Select variable"])


def select(dropdown):
    def on_change(attr, old, new):
        for key, value in dropdown.menu:
            if value == new:
                dropdown.label = key
    return on_change


def menu(words):
    return list(zip(words, words))


def to_stamp(time, fmt=FORMAT):
    return time.strftime(fmt)


def to_time(stamp, fmt=FORMAT):
    return dt.datetime.strptime(stamp, fmt)


def to_lengths(times):
    if isinstance(times, list):
        times = np.array(times, dtype="datetime64[s]")
    if times.dtype == 'O':
        times = times.astype("datetime64[s]")
    return (times - times[0]).astype('timedelta64[h]')


def format_length(hours):
    try:
        x = int(hours)
    except TypeError:
        x = hours.astype(int)
    return "T{:+}".format(x)


if __name__.startswith('bk'):
    main()
