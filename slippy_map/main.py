import numpy as np
import bokeh.plotting


def perimeter(x, y, dw, dh):
    return ([x, x + dw, x + dw, x, x],
            [y, y, y + dh, y + dh, y])


def area(figure):
    dw = figure.x_range.end - figure.x_range.start
    dh = figure.y_range.end - figure.y_range.start
    return dw * dh


def valid_range(figure):
    return all(value is not None for value in [
        figure.x_range.start,
        figure.x_range.end,
        figure.y_range.start,
        figure.y_range.end
    ])

source = bokeh.models.ColumnDataSource({
    "xs": [],
    "ys": []
})
def draw_squares(figure):
    if valid_range(figure):
        xs, ys = [], []
        for x, y, dw, dh in tiles(figure):
            xp, yp = perimeter(x, y, dw, dh)
            xs.append(xp)
            ys.append(yp)
        source.data = {
            "xs": xs,
            "ys": ys
        }


def tiles(figure):
    if area(figure) < 1:
        xys = [(0, 0), (0.5, 0.), (0.5, 0.5), (0, 0.5)]
        dw, dh = 0.5, 0.5
    else:
        xys = [(0, 0)]
        dw, dh = 1, 1
    tiles = []
    for x, y in xys:
        tiles.append((x, y, dw, dh))
    return tiles


def add_zoom(figure):
    counter = 0
    def callback(attr, old, new):
        nonlocal counter
        if counter % 50 == 0:
            draw_squares(figure)
        counter += 1
    figure.x_range.on_change("start", callback)
    figure.x_range.on_change("end", callback)
    figure.y_range.on_change("start", callback)
    figure.y_range.on_change("end", callback)


figure = bokeh.plotting.figure(
        x_range=(0, 1),
        y_range=(0, 1),
        active_scroll="wheel_zoom",
        sizing_mode="stretch_both")
figure.multi_line(xs="xs", ys="ys", source=source)
add_zoom(figure)
document = bokeh.plotting.curdoc()
document.add_root(figure)
