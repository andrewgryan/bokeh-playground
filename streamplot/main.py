import numpy as np
import bokeh.plotting
import matplotlib.collections
import matplotlib.pyplot as plt
from contextlib import contextmanager


def main():
    x = np.linspace(0, 1, 3)
    y = np.linspace(0, 1, 3)

    bokeh_figure = bokeh.plotting.figure(sizing_mode="stretch_both")

    u, v = np.meshgrid(x, y)
    streamplot(bokeh_figure, x, y, u, v,
               line_color="CadetBlue")

    u, v = np.meshgrid(x, y)
    u = u + v
    streamplot(bokeh_figure, x, y, u, v,
               line_color="Coral")

    document = bokeh.plotting.curdoc()
    document.add_root(bokeh_figure)


def streamplot(bokeh_figure, x, y, u, v,
        line_color="black",
        head_size=12):
    with save_patches():
        artist = plt.streamplot(x, y, u, v)
        posA_posBs = [p._posA_posB for p in artist.arrows.patches]

    xs = []
    ys = []
    for path in artist.lines.get_paths():
        x, y = path.vertices.T
        xs.append(x)
        ys.append(y)
    bokeh_figure.multi_line(xs=xs, ys=ys, line_color=line_color)

    # Open arrow head
    for posA_posB in posA_posBs:
        (x_start, y_start), (x_end, y_end) = posA_posB
        arrow = bokeh.models.Arrow(
                end=bokeh.models.OpenHead(
                    size=head_size,
                    line_color=line_color),
                x_start=x_start,
                y_start=y_start,
                x_end=x_end,
                y_end=y_end,
                line_color=line_color)
        bokeh_figure.add_layout(arrow)


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
