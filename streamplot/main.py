import numpy as np
import bokeh.plotting
import matplotlib.collections
import matplotlib.pyplot as plt
from contextlib import contextmanager
import os
import sys


def main():
    bokeh_figure = bokeh.plotting.figure(sizing_mode="stretch_both")

    x = np.linspace(0, 1, 3)
    y = np.linspace(0, 1, 3)
    u, v = np.meshgrid(x, y)
    line_source, arrow_source = streamplot(
            x, y, u, v,
            bokeh_figure=bokeh_figure,
            line_color="CadetBlue")

    button = bokeh.models.Button()
    button.on_click(on_click(line_source, arrow_source))

    document = bokeh.plotting.curdoc()
    document.add_root(button)
    document.add_root(bokeh_figure)


def on_click(line_source, arrow_source):
    click = 0
    def wrapper():
        nonlocal click
        x = np.linspace(0, 1, 5)
        y = np.linspace(0, 1, 5)

        u, v = np.meshgrid(x, y)
        if click % 2 == 0:
            u = u + v
        else:
            u = u - v
        streamplot(x, y, u, v,
                   line_color="Coral",
                   line_source=line_source,
                   arrow_source=arrow_source)
        click += 1
    return wrapper


def streamplot(x, y, u, v,
        line_color="black",
        head_size=12,
        line_source=None,
        arrow_source=None,
        bokeh_figure=None):
    """Convert matplotlib.streamplot.streamplot to bokeh"""
    if bokeh_figure is None:
        msg = 'please specify line_source and arrow_source'
        assert (arrow_source is not None) and (line_source is not None), msg
    line_data, arrow_data = streamplot_data(x, y, u, v)
    if line_source is not None:
        line_source.data = line_data
    else:
        line_source = bokeh.models.ColumnDataSource(line_data)
        bokeh_figure.multi_line(xs="xs",
                                ys="ys",
                                line_color=line_color,
                                source=line_source)
    if arrow_source is not None:
        arrow_source.data = arrow_data
    else:
        arrow_source = bokeh.models.ColumnDataSource(arrow_data)
        arrow = bokeh.models.Arrow(
                end=bokeh.models.OpenHead(
                    size=head_size,
                    line_color=line_color),
                x_start="x_start",
                y_start="y_start",
                x_end="x_end",
                y_end="y_end",
                line_alpha=0,
                source=arrow_source)
        bokeh_figure.add_layout(arrow)
    return line_source, arrow_source


def streamplot_data(x, y, u, v):
    """Data that drives streamplot glyphs"""
    if isinstance(x, list):
        x = np.asarray(x)
    if isinstance(y, list):
        y = np.asarray(y)
    if isinstance(u, list):
        u = np.asarray(u)
    if isinstance(v, list):
        v = np.asarray(v)

    with save_patches():
        artist = plt.streamplot(x, y, u, v)
        posA_posBs = [p._posA_posB for p in artist.arrows.patches]

    xs = []
    ys = []
    tolerance = 0.01
    previous = None
    for path in artist.lines.get_paths():
        current = path.vertices
        if previous is None:
            # First segment contains two points
            x = list(current[:, 0])
            y = list(current[:, 1])
        elif all(np.abs(current[0] - previous[1]) < tolerance):
            # Append next point to existing segment
            x.append(current[1, 0])
            y.append(current[1, 1])
        else:
            # Save old segment
            xs.append(x)
            ys.append(y)
            # Start new segment
            x = list(current[:, 0])
            y = list(current[:, 1])
        previous = current

    if len(x) > 0:
        # Save final segment
        xs.append(x)
        ys.append(y)

    line_data = {
        "xs": xs,
        "ys": ys
    }

    x_starts, y_starts, x_ends, y_ends = [], [], [], []
    for posA_posB in posA_posBs:
        (x_start, y_start), (x_end, y_end) = posA_posB
        x_starts.append(x_start)
        y_starts.append(y_start)
        x_ends.append(x_end)
        y_ends.append(y_end)
    arrow_data = {
        "x_start": x_starts,
        "y_start": y_starts,
        "x_end": x_ends,
        "y_end": y_ends,
    }
    return line_data, arrow_data


@contextmanager
def save_patches():
    original = matplotlib.collections.PatchCollection
    matplotlib.collections.PatchCollection = _decorate(original)
    yield
    matplotlib.collections.PatchCollection = original


def _decorate(Collection):
    def wrapper(*args, **kwargs):
        c = Collection(*args, **kwargs)
        c.patches = args[0]
        return c
    return wrapper


if __name__.startswith('bk'):
    main()
