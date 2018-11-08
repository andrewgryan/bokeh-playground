import numpy as np
import bokeh.plotting


def perimeter(x, y, dw, dh):
    return ([x, x + dw, x + dw, x, x],
            [y, y, y + dh, y + dh, y])


def area(x_start, x_end, y_start, y_end):
    dw = x_end - x_start
    dh = y_end - y_start
    return dw * dh


def valid_range(figure):
    return all(value is not None for value in [
        figure.x_range.start,
        figure.x_range.end,
        figure.y_range.start,
        figure.y_range.end
    ])


def color(dw):
    if dw == 1:
        return "blue"
    elif dw == 0.5:
        return "red"
    elif dw == 0.25:
        return "purple"


source = bokeh.models.ColumnDataSource({
    "xs": [],
    "ys": [],
    "color": []
})
def draw_squares(figure):
    if valid_range(figure):
        colors = []
        xs, ys = [], []
        for x, y, dw, dh in tiles(
                figure.x_range.start,
                figure.x_range.end,
                figure.y_range.start,
                figure.y_range.end):
            xp, yp = perimeter(x, y, dw, dh)
            xs.append(xp)
            ys.append(yp)
            colors.append(color(dw))
        source.data = {
            "xs": xs,
            "ys": ys,
            "color": colors
        }


def tiles(x_start, x_end, y_start, y_end):
    if area(x_start, x_end, y_start, y_end) < 4 * (0.25)**2:
        dw, dh = 0.25, 0.25
        if x_start < 0:
            x0 = 0
        else:
            x0 = np.floor(x_start / dw) * dw
        if y_start < 0:
            y0 = 0
        else:
            y0 = np.floor(y_start / dh) * dh
        x = dw * np.array([0, 1, 1, 0], dtype="f") + x0
        y = dh * np.array([0, 0, 1, 1], dtype="f") + y0
        xys = zip(x, y)
    elif area(x_start, x_end, y_start, y_end) < 4 * (0.5)**2:
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
figure.multi_line(xs="xs", ys="ys", color="color", source=source)
add_zoom(figure)
document = bokeh.plotting.curdoc()
document.add_root(figure)
