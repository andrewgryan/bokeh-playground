import datetime as dt
import bokeh.plotting
import bokeh.models
import bokeh.events
import os
import sys
sys.path.insert(0, os.path.dirname(__file__))
import rx
import chronometer


def main():
    document = bokeh.plotting.curdoc()
    source = bokeh.models.ColumnDataSource({
        "valid": [
            dt.datetime(2018, 1, 1, 12),
            dt.datetime(2018, 1, 2, 0),
            dt.datetime(2018, 1, 2, 6),
            dt.datetime(2018, 1, 2, 12),
            dt.datetime(2018, 1, 3, 0),
            ],
        "offset": [12, 0, 6, 12, 0],
        "start": [
            dt.datetime(2018, 1, 1),
            dt.datetime(2018, 1, 2),
            dt.datetime(2018, 1, 2),
            dt.datetime(2018, 1, 2),
            dt.datetime(2018, 1, 3)]
        })
    widgets = chronometer.chronometer(
            valid="valid",
            offset="offset",
            start="start",
            source=source)
    figure, radio_group, plus_button, minus_button = widgets
    layout = bokeh.layouts.layout([
        [radio_group, plus_button, minus_button],
        [figure]])

    div = bokeh.models.Div()
    def view(div):
        def wrapper(state):
            x, y, z = state
            template = "<p>Valid date: {}</br>Start date: {}</br>Offset: {}</p>"
            msg = template.format(x, z, "T+{}".format(str(y)))
            div.text = msg
        return wrapper

    def model(source,
            valid="x",
            offset="y",
            start="z"):
        def wrapper(new):
            i = new[0]
            x, y, z = (
                    source.data[valid][i],
                    source.data[offset][i],
                    source.data[start][i])
            if not isinstance(x, dt.datetime):
                x = dt.datetime.fromtimestamp(x / 1000.)
            if not isinstance(z, dt.datetime):
                z = dt.datetime.fromtimestamp(z / 1000.)
            return x, y, z
        return wrapper

    stream = rx.Stream()
    source.selected.on_change('indices', rx.callback(stream))
    stream = stream.map(model(
        source,
        valid="valid",
        offset="offset",
        start="start")).map(view(div))

    source.selected.indices = [0]

    document.add_root(bokeh.layouts.widgetbox(div))
    document.add_root(layout)


if __name__.startswith('bk'):
    main()
