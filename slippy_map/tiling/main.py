import bokeh.plotting
import bokeh.layouts
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

    min_level = 0
    max_level = 6
    level = 4
    lc = {
        0: "blue",
        1: "gray",
        2: "green",
        3: "red",
        4: "orange",
        5: "SteelBlue",
        6: "Teal"
    }
    grid_visible = True
    grid_source = bokeh.models.ColumnDataSource({
        "xs": [],
        "ys": [],
        "line_color": []
    })
    figure.multi_line(
        xs="xs",
        ys="ys",
        line_color="line_color",
        source=grid_source)

    def draw_grid(level):
        xs, ys = [], []
        for i in range(2**level):
            for j in range(2**level):
                xc, yc, length = tile(i, j, level)
                x, y = square(xc, yc, length)
                xs.append(x)
                ys.append(y)
        grid_source.data = {
            "xs": xs,
            "ys": ys,
            "line_color": len(xs) * [lc[level]]
        }

    if grid_visible:
        draw_grid(level)

    # Fake x/y perimeter
    xc, yc, dx, dy = 1.5, 0.9, 3, 1.5
    x, y = rectangle(xc, yc, dx, dy)
    rectangle_source = bokeh.models.ColumnDataSource({
        "xs": [x],
        "ys": [y]
    })
    figure.multi_line(xs="xs", ys="ys",
                      line_color="black",
                      source=rectangle_source)

    tile_size = 256
    using_mercator = False
    if using_mercator:
        circumference = EARTH_CIRCUMFERENCE
    else:
        circumference = 5
    dp = resolution(global_resolution(circumference, tile_size), level)

    def shade(xc, yc, dx, dy, dp, level):
        si, sj = tile_index(*pixel_index(xc, yc, dp))
        ei, ej = tile_index(*pixel_index(xc + dx, yc + dy, dp))
        xs, ys = [], []
        for i, j in tile_indices((si, sj), (ei, ej)):
            xc, yc, length = tile(i, j, level)
            x, y = square(xc, yc, length)
            xs.append(x)
            ys.append(y)
        print("{} tiles covering rectangle".format(len(xs)))
        return {
            "xs": xs,
            "ys": ys,
            "fill_color": len(xs) * [lc[level]],
            "line_color": len(xs) * [lc[level]]
        }

    shade_source = bokeh.models.ColumnDataSource(
        shade(xc, yc, dx, dy, dp, level))
    figure.patches(xs="xs",
                   ys="ys",
                   source=shade_source,
                   fill_alpha=0.5,
                   fill_color="fill_color",
                   line_color="line_color")

    def random_rectangle():
        nonlocal xc, yc, dx, dy
        max_width = 5
        max_height = 5
        dx = max_width * np.random.random()
        dy = max_height * np.random.random()
        xc = (max_width - dx) * np.random.random()
        yc = (max_height - dy) * np.random.random()

        dp = resolution(global_resolution(circumference, tile_size), level)
        shade_source.data = shade(xc, yc, dx, dy, dp, level)

        x, y = rectangle(xc, yc, dx, dy)
        rectangle_source.data = {
            "xs": [x],
            "ys": [y]
        }

    def draw():
        if grid_visible:
            draw_grid(level)
        else:
            grid_source.data = {
                "xs": [],
                "ys": [],
                "line_color": []
            }
        dp = resolution(global_resolution(circumference, tile_size), level)
        shade_source.data = shade(xc, yc, dx, dy, dp, level)


    def increment_level():
        nonlocal level
        if level < max_level:
            level += 1
            draw()

    def decrement_level():
        nonlocal level
        if level > min_level:
            level -= 1
            draw()

    def toggle_grid():
        nonlocal grid_visible
        grid_visible = not grid_visible
        draw()

    btns = []
    for label, on_click in [
                ("Random rectangle", random_rectangle),
                ("+", increment_level),
                ("-", decrement_level),
                ("Toggle grid", toggle_grid)
            ]:
        btn = bokeh.models.Button(label=label)
        btn.on_click(on_click)
        btns.append(btn)
    document = bokeh.plotting.curdoc()
    document.add_root(bokeh.layouts.column(
        bokeh.layouts.row(*btns),
        figure))


def tile_indices(start, end):
    si, sj = start
    ei, ej = end
    for i in range(si, ei + 1):
        for j in range(sj, ej + 1):
            yield i, j


if __name__ == '__main__' or __name__.startswith("bk"):
    main()
