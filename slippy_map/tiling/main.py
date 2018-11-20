import bokeh.plotting
import numpy as np


EARTH_CIRCUMFERENCE = 2 * np.pi * 6378137


def axis_listener(figure):
    def wrapper(attr, old, new):
        print(
            figure.x_range.start,
            figure.x_range.end,
            figure.y_range.start,
            figure.y_range.end,
        )
    return wrapper


def square(xc, yc, side):
    return rectangle(xc, yc, side, side)


def rectangle(xc, yc, dx, dy):
    x = xc + dx * np.array([0, 1, 1, 0, 0])
    y = yc + dy * np.array([0, 0, 1, 1, 0])
    return x, y


def tile(i, j, level):
    """Coordinates of tile in x, y space"""
    tile_size = 256
    initial_resolution = 5 / tile_size
    resolution = initial_resolution / (2 ** level)
    side_length = resolution * tile_size
    x = i * side_length
    y = j * side_length
    return x, y, side_length


def tile_index(px, py):
    """Given coordinates in pixel space return index in tile space"""
    tile_size = 256
    tx = int(np.ceil(px / tile_size)) - 1
    ty = int(np.ceil(py / tile_size)) - 1
    return tx, ty


def pixel_index(x, y, dp):
    return np.floor(x / dp), np.floor(y / dp)


def resolution(initial, level):
    return initial / (2 ** level)


def global_resolution(circumference, pixels_per_tile):
    return circumference / pixels_per_tile


def main():
    figure = bokeh.plotting.figure(
        sizing_mode="stretch_both",
        match_aspect=True
    )
    callback = axis_listener(figure)
    figure.x_range.on_change("start", callback)
    figure.x_range.on_change("end", callback)
    figure.y_range.on_change("start", callback)
    figure.y_range.on_change("end", callback)

    lc = {
        2: "green",
        3: "red",
        4: "orange"
    }
    level = 4
    xs, ys = [], []
    for i in range(2**level):
        for j in range(2**level):
            xc, yc, length = tile(i, j, level)
            x, y = square(xc, yc, length)
            xs.append(x)
            ys.append(y)
    figure.multi_line(xs=xs, ys=ys, line_color=lc[level])

    # Fake x/y perimeter
    xc, yc, dx, dy = 1.5, 0.9, 3, 1.5
    x, y = rectangle(xc, yc, dx, dy)
    figure.multi_line(xs=[x], ys=[y], line_color="black")

    using_mercator = False
    if using_mercator:
        circumference = EARTH_CIRCUMFERENCE
    else:
        circumference = 5

    tile_size = 256
    dp = resolution(global_resolution(circumference, tile_size), level)
    si, sj = tile_index(*pixel_index(xc, yc, dp))
    ei, ej = tile_index(*pixel_index(xc + dx, yc + dy, dp))
    xs, ys = [], []
    for i, j in tile_indices((si, sj), (ei, ej)):
        xc, yc, length = tile(i, j, level)
        x, y = square(xc, yc, length)
        xs.append(x)
        ys.append(y)
    figure.patches(xs=xs, ys=ys,
                   line_alpha=0,
                   fill_alpha=0.5,
                   fill_color=lc[level])

    document = bokeh.plotting.curdoc()
    document.add_root(figure)


def tile_indices(start, end):
    si, sj = start
    ei, ej = end
    for i in range(si, ei + 1):
        for j in range(sj, ej + 1):
            yield i, j


if __name__ == '__main__' or __name__.startswith("bk"):
    main()
