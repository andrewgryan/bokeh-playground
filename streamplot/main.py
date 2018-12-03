import numpy as np
import bokeh.plotting
import matplotlib.collections
import matplotlib.pyplot as plt
from contextlib import contextmanager


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


def main():
    x = np.linspace(0, 1, 3)
    y = np.linspace(0, 1, 3)
    u, v = np.meshgrid(x, y)

    with save_patches():
        artist = plt.streamplot(x, y, u, v)
        posA_posBs = [p._posA_posB for p in artist.arrows.patches]


    line_color = "black"

    bokeh_figure = bokeh.plotting.figure(sizing_mode="stretch_both")
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
                end=bokeh.models.OpenHead(),
                x_start=x_start,
                y_start=y_start,
                x_end=x_end,
                y_end=y_end,
                line_color=line_color)
        bokeh_figure.add_layout(arrow)

    document = bokeh.plotting.curdoc()
    document.add_root(bokeh_figure)


if __name__.startswith('bk'):
    main()
