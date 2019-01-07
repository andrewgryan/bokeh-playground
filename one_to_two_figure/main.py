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

    zs = []
    nx, ny = 10, 10
    x, y = np.meshgrid(
            np.linspace(0, 10, nx),
            np.linspace(0, 10, ny))
    z = np.ma.asarray(y)
    z[:, ::2] = np.ma.masked
    source_1 = image_source(x, y, z)
    zs.append(z)

    z = np.ma.asarray(y)
    z[:, 1::2] = np.ma.masked
    source_2 = image_source(x, y, z)
    zs.append(z)

    low = min([z.min() for z in zs])
    high = max([z.max() for z in zs])
    color_mapper = bokeh.models.LinearColorMapper(
        palette=bokeh.palettes.Plasma[256],
        low=low,
        high=high,
        nan_color=bokeh.colors.RGB(0, 0, 0, a=0),
    )
    for f in figures:
        colorbar(f, color_mapper)

    first_glyph = plot_image(first, source_1, color_mapper)
    second_glyph = plot_image(first, source_2, color_mapper)
    third_glyph = plot_image(second, source_2, color_mapper)

    layout = bokeh.layouts.row(*figures, sizing_mode="stretch_both")
    layout.children = [figures[0]]  # Trick to keep correct sizing modes

    button = bokeh.models.Button()
    button.on_click(toggle(figures, layout, [second_glyph]))
    document.add_root(layout)
    document.add_root(button)


def image_source(x, y, z):
    # Map to Google Mercator projection
    gl = cartopy.crs.Mercator.GOOGLE
    pc = cartopy.crs.PlateCarree()
    x, y, _ = gl.transform_points(pc, x.flatten(), y.flatten()).T
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


def colorbar(figure, color_mapper):
    color_bar = bokeh.models.ColorBar(
        color_mapper=color_mapper,
        orientation='horizontal',
        background_fill_alpha=0,
        location='bottom_center')
    figure.add_layout(color_bar, 'center')
    return color_bar


def toggle(figures, layout, glyphs):
    def render():
        if len(layout.children) == 1:
            layout.children = figures
            for glyph in glyphs:
                glyph.visible = False
        else:
            layout.children = [figures[0]]
            for glyph in glyphs:
                glyph.visible = True
    return render


if __name__.startswith('bk'):
    main()
