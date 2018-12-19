import bokeh.plotting
import bokeh.models
import bokeh.layouts
import cartopy
import numpy as np


def main():
    document = bokeh.plotting.curdoc()
    tile = bokeh.models.WMTSTileSource(
        url='http://c.tile.openstreetmap.org/{Z}/{X}/{Y}.png',
        attribution="Attribution text goes here"
    )
    first = bokeh.plotting.figure(
        x_range=(-2000000, 6000000),
        y_range=(-1000000, 7000000),
        x_axis_type="mercator",
        y_axis_type="mercator",
        active_scroll="wheel_zoom")
    second = bokeh.plotting.figure(
        active_scroll="wheel_zoom",
        x_axis_type="mercator",
        y_axis_type="mercator",
        x_range=first.x_range,
        y_range=first.y_range)
    figures = [
     first,
     second
    ]
    for f in figures:
        f.toolbar.logo = None
        f.toolbar_location = None
        f.add_tile(tile)

    first_glyph = plot_image(first)
    second_glyph = plot_image(first)
    third_glyph = plot_image(second)

    figures[0].circle([1, 2, 3], [1, 2, 3])
    figures[1].circle([1, 2, 3], [1, 2, 3], fill_color="red", line_color=None)

    layout = bokeh.layouts.row(*figures, sizing_mode="stretch_both")
    layout.children = [figures[0]]  # Trick to keep correct sizing modes

    button = bokeh.models.Button()
    button.on_click(toggle(figures, layout))
    document.add_root(layout)
    document.add_root(button)


def image_source():
    # Define grid
    nx, ny = 40, 50
    x = np.linspace(0, 10, nx)
    y = np.linspace(0, 10, ny)
    x2d, y2d = np.meshgrid(x, y)

    # Map to Google Mercator projection
    gl = cartopy.crs.Mercator.GOOGLE
    pc = cartopy.crs.PlateCarree()
    x, y, _ = gl.transform_points(pc, x2d.flatten(), y2d.flatten()).T

    z = x2d + y2d
    low = z.min()
    high = z.max()
    return bokeh.models.ColumnDataSource({
        "x": [x.min()],
        "y": [y.min()],
        "dw": [x.max() - x.min()],
        "dh": [y.max() - y.min()],
        "image": [z]
        })


def plot_image(figure, source, color_mapper):
    return figure.image(
        x="x",
        y="y",
        dw="dw",
        dh="dh",
        image="image",
        source=source,
        color_mapper=color_mapper
    )


def color_mapper(low, high):
    return bokeh.models.LinearColorMapper(
        palette=bokeh.palettes.Viridis256,
        low=low,
        high=high
    )


def colorbar(figure, color_mapper):
    color_bar = bokeh.models.ColorBar(
        color_mapper=color_mapper,
        orientation='horizontal',
        background_fill_alpha=0,
        location='bottom_center')
    figure.add_layout(color_bar, 'center')
    return color_bar


def toggle(figures, layout):
    def render():
        if len(layout.children) == 1:
            layout.children = figures
        else:
            layout.children = [figures[0]]
    return render


if __name__.startswith('bk'):
    main()
