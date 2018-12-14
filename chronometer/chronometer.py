"""

Chronometer
===========

Navigation tools to explore forecast and time dimensions. Valid and
start times can be specified by datetime objects while the offsets
are represented as ints, specifically hours since forecast
initialisation time

"""
import numpy as np
import bokeh.plotting
import bokeh.models
import rx


def chronometer(
        valid=None,
        offset=None,
        start=None,
        source=None,
        radio_group=None,
        plus_button=None,
        minus_button=None,
        selectors=None):
    """
    Time/forecast exploration widget

    Creates a figure with glyphs for each point in
    time/forecast space along with +/- buttons and a
    radio group to navigate subsets of available
    forecasts

    >>> source = bokeh.models.ColumnDataSource({
    ...     "valid": [],
    ...     "start": [],
    ...     "offset": []
    ... })
    >>> figure, radio_group, plus, minus = chronometer(
    ...     valid="valid",
    ...     start="start",
    ...     offset="offset",
    ...     source=source)
    >>> isinstance(figure, bokeh.plotting.Figure)
    True

    The associated glyphs react to changes in
    the `source.selected.indices` and the appropriate
    clicks from the radio group, plus and minus buttons

    >>> import datetime as dt
    >>> source.stream({
    ...     "valid": [dt.datetime(2018, 1, 1, 12)],
    ...     "start": [dt.datetime(2018, 1, 1, 0)],
    ...     "offset": [12]
    ... })
    >>> source.selected.indices = [0]

    **Selectors**

    The radio group allows the user to choose between
    time/forecast selection algorithms

    >>> selectors = {
    ...     0: select("key")
    ... }

    The keys of the selectors dict maps radio
    group active index to functions that select
    points in the column data source

    **Widgets**

    A figure, a radio group and buttons for navigating
    backwards/forwards inside a selection are returned
    to allow the user to craft their own layout

    :param valid: key in source
    :param start: key in source
    :param offset: key in source
    :param source: ColumnDataSource

    :returns: figure, radio group, plus button and
              minus button bokeh widgets
    """
    msg = ("please specify 'valid', 'start' and 'offset' "
           "keywords")
    assert valid is not None, msg
    assert start is not None, msg
    assert offset is not None, msg
    if radio_group is None:
        radio_group = bokeh.models.RadioGroup(labels=[
            "Time", "Forecast", "Run"],
            inline=True,
            width=210,
            active=2)
    if selectors is None:
        selectors = {
            0: select(valid),
            1: select(offset),
            2: select(start),
        }
    if plus_button is None:
        plus_button = bokeh.models.Button(
                label="+",
                width=50)
    if minus_button is None:
        minus_button = bokeh.models.Button(
                label="-",
                width=50)
    hover_tool = bokeh.models.HoverTool(
            tooltips=[
                ('valid', '@' + valid + '{%F %T}'),
                ('start', '@' + start + '{%F %T}'),
                ('length', 'T+@' + offset)
                ],
            formatters={
                valid: 'datetime',
                start: 'datetime'
                })
    pan_tool = bokeh.models.PanTool(dimensions="width")
    tap_tool = bokeh.models.TapTool()
    figure = bokeh.plotting.figure(x_axis_type='datetime',
                                   plot_height=200,
                                   plot_width=350,
                                   tools=[
                                       tap_tool,
                                       hover_tool,
                                       pan_tool,
                                       "xwheel_zoom"],
                                   active_scroll="xwheel_zoom",
                                   toolbar_location=None)
    figure.toolbar.active_inspect = hover_tool
    figure.ygrid.grid_line_color = None
    figure.xaxis.axis_label = "Validity time"
    figure.xaxis.axis_label_text_font_size = "10px"
    figure.yaxis.axis_label = "Forecast length"
    figure.yaxis.axis_label_text_font_size = "10px"
    offsets = source.data[offset][:]
    if len(offsets) > 0:
        figure.yaxis.ticker = ticks(max(offsets))
    renderer = figure.square(
            x=valid,
            y=offset,
            source=source,
            size=8,
            line_color=None,
            nonselection_alpha=1,
            nonselection_line_color=None)
    tap_tool.renderers = [renderer]

    second_source = bokeh.models.ColumnDataSource({
        valid: [],
        offset: [],
        start: []})
    renderer = figure.square(
            x=valid,
            y=offset,
            size=8,
            source=second_source)
    renderer.selection_glyph = bokeh.models.Square(
            fill_alpha=1,
            fill_color="Red",
            line_color="Black")
    renderer.nonselection_glyph = bokeh.models.Square(
            fill_alpha=1,
            fill_color="White",
            line_color="Black")

    selected = rx.Stream()
    source.selected.on_change('indices', rx.callback(selected))

    active = rx.Stream()
    radio_group.on_change("active", rx.callback(active))
    changes = rx.combine_latest(
            active.map(lambda i: selectors[i]),
            selected).filter(all_not_none)

    def render(source, second_source):
        """Updates secondary source used to highlight selection"""
        def wrapper(event):
            selector, indices = event
            if len(indices) == 0:
                indices = []
                data = {k: [] for k in source.data.keys()}
            else:
                index = indices[0]
                pts = selector(source, index)
                indices = [pts[0].tolist().index(index)]
                data = {k: np.asarray(v)[pts] for k, v in source.data.items()}
            second_source.data = data
            second_source.selected.indices = indices
        return wrapper

    changes.map(render(source, second_source))

    plus = rx.Stream()
    plus_button.on_click(rx.click(plus))
    plus = plus.map(+1)

    minus = rx.Stream()
    minus_button.on_click(rx.click(minus))
    minus = minus.map(-1)

    steps = rx.Merge(plus, minus)
    steps.map(move(second_source)).map(sync(
        source,
        second_source,
        valid=valid,
        offset=offset))

    if radio_group.active is not None:
        active.emit(radio_group.active)
    return figure, radio_group, plus_button, minus_button


def all_not_none(items):
    return all(item is not None for item in items)


def ticks(max_hour):
    """Choose appropriate tick locations for forecasts"""
    step_size = 3
    while max_hour >= (4 * step_size):
        step_size *= 2
    hour = 0
    ticks = []
    while (hour <= max_hour):
        ticks.append(hour)
        hour += step_size
    return ticks


def sync(large, small, valid="x", offset="y"):
    def wrapper(event):
        if len(small.selected.indices) == 0:
            return
        si = small.selected.indices[0]
        li = large.selected.indices[0]
        sx = np.asarray(small.data[valid][:])
        sy = np.asarray(small.data[offset][:])
        lx = np.asarray(large.data[valid][:])
        ly = np.asarray(large.data[offset][:])
        if ((lx[li] == sx[si]) and (ly[li] == sy[si])):
            return
        pts = np.where((lx == sx[si]) & (ly == sy[si]))
        large.selected.indices = pts[0].tolist()
    return wrapper


def move(source):
    def wrapper(steps):
        if len(source.selected.indices) > 0:
            i = source.selected.indices[0]
            key = list(source.data.keys())[0]
            n = len(source.data[key])
            source.selected.indices = [(i + steps) % n]
        return source.selected.indices
    return wrapper


def select(key):
    """Select all values in source that match 'key' at index"""
    def wrapper(source, index):
        values = np.asarray(source.data[key])
        return np.where(values == values[index])
    return wrapper
