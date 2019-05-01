import numpy as np
import data
import datetime as dt
import bokeh.plotting
import bokeh.layouts
from collections import namedtuple
from observer import Observable


FORMAT = "%Y-%m-%d %H:%M"


def main():
    date_picker = bokeh.models.DatePicker()
    button = bokeh.models.Button()

    def on_click():
        date_picker.value = dt.datetime(1986, 1, 12)
    button.on_click(on_click)

    model_nav = ModelNavigation()
    model_nav.render()
    view = View()
    model_nav.subscribe(view.on_state)
    document = bokeh.plotting.curdoc()
    document.add_root(
            bokeh.layouts.column(
                button,
                date_picker,
                model_nav.layout,
                view.div,
                sizing_mode="stretch_width"))


State = namedtuple("State", (
            "model",
            "variable",
            "initial",
            "valid",
            "length",
            "pressure"))


class View(object):
    def __init__(self):
        self.div = bokeh.models.Div()

    def on_state(self, state):
        print("on_state()")
        self.div.text = """
            <ul>
                <li>Model: {}</li>
                <li>Variable: {}</li>
                <li>Initial: {}</li>
                <li>Valid: {}</li>
                <li>Length: {}</li>
                <li>Pressure: {}</li>
            </ul>
        """.format(
                str(state.model),
                str(state.variable),
                str(state.initial),
                str(state.valid),
                str(state.length),
                str(state.pressure))


class ModelNavigation(Observable):
    def __init__(self):
        self.name = None
        self.variable = None
        self.initial_time = None
        self.valid_time = None
        self.pressure = None
        self.variables = []
        self.initial_times = []
        self.valid_times = []
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
        super().__init__()

    def on_run(self, attr, old, new):
        print(new)
        valid_dropdown = self.dropdowns["valid"]
        valid_dropdown.menu = [("loading", "loading")]
        self.initial_time = to_time(new)
        path = data.PATHS[(self.name, self.initial_time)]
        self.valid_times = data.valid_times(path)
        self.render()

    def on_valid(self, attr, old, new):
        values = [v for _, v in self.dropdowns["valid"].menu]
        i = values.index(new)
        self.valid_time = self.valid_times[i]
        self.render()

    def on_name(self, attr, old, new):
        print(new)
        self.name = new
        self.variables = data.VARIABLES[self.name]
        self.initial_times = data.RUN_TIMES[self.name]
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
        if len(self.initial_times) == 0:
            labels = [("Select model")]
        else:
            labels = [to_stamp(t) for t in self.initial_times]
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

        if len(self.valid_times) > 0:
            if self.valid_time is not None:
                if self.units == "T+":
                    label = format_length(self.length)
                else:
                    label = to_stamp(self.valid_time)
                self.dropdowns["valid"].label = label

        if len(self.variables) == 0:
            self.dropdowns["variable"].menu = menu(["Select model"])
        else:
            self.dropdowns["variable"].menu = menu(self.variables)

        if len(self.pressures) == 0:
            self.dropdowns["pressure"].menu = menu(["Select variable"])

        self.announce(self.state)

    @property
    def length(self):
        if self.initial_time is None:
            return
        if self.valid_time is None:
            return
        t0 = np.datetime64(self.initial_time, 's')
        t1 = np.datetime64(self.valid_time, 's')
        return (t1 - t0).astype('timedelta64[h]')

    @property
    def state(self):
        return State(
                self.name,
                self.variable,
                self.initial_time,
                self.valid_time,
                self.length,
                self.pressure)


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
