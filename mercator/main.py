import bokeh.plotting
import bokeh.models
import bokeh.palettes
import numpy as np
import cartopy
import scipy.interpolate
import stretch


def main():
    bokeh_figure = bokeh.plotting.figure(
            x_axis_type="mercator",
            y_axis_type="mercator",
            sizing_mode="stretch_both")
    tile = bokeh.models.WMTSTileSource(
        url='http://c.tile.openstreetmap.org/{Z}/{X}/{Y}.png',
        attribution="&copy; <a href='http://www.openstreetmap.org/copyright'>OpenStreetMap</a> contributors"
    )
    bokeh_figure.add_tile(tile)

    # Define grid
    nx, ny = 40, 50
    x = np.linspace(90, 150, nx)
    y = np.linspace(-70, 70, ny)
    x2d, y2d = np.meshgrid(x, y)

    # Map to Google Mercator projection
    gl = cartopy.crs.Mercator.GOOGLE
    pc = cartopy.crs.PlateCarree()
    xt1d, yt1d, _ = gl.transform_points(pc, x2d.flatten(), y2d.flatten()).T

    zt1d = yt1d

    xt2d = xt1d.reshape(ny, nx)
    yt2d = yt1d.reshape(ny, nx)
    zt2d = zt1d.reshape(ny, nx)

    use_stretch = True
    if use_stretch:
        xm = xt2d[0, :]
        ym = stretch.web_mercator_y(y)
        transform = stretch.stretch_transform(ym, axis=0)
        xe, ye = np.meshgrid(xm, stretch.equal_spaced(ym))
        ze = transform(zt2d)
    else:
        xe, ye, ze = regular_grid(xt2d, yt2d, zt2d)

    # Plot filled color circles
    v = zt2d - ze
    palette = bokeh.palettes.Viridis256
    x = xe.flatten()
    y = ye.flatten()
    z = v.flatten()
    low = z.min()
    high = z.max()
    color_mapper = bokeh.models.LinearColorMapper(
        palette=palette,
        low=low,
        high=high
    )
    source = bokeh.models.ColumnDataSource({
        "x": x,
        "y": y,
        "z": z
        })
    # bokeh_figure.circle(
    #         x="x",
    #         y="y",
    #         fill_color={"field": "z", "transform": color_mapper},
    #         line_color={"field": "z", "transform": color_mapper},
    #         source=source)
    image_source = bokeh.models.ColumnDataSource({
        "x": [x.min()],
        "y": [y.min()],
        "dw": [x.max() - x.min()],
        "dh": [y.max() - y.min()],
        "image": [v]
        })
    bokeh_figure.image(
        x="x",
        y="y",
        dw="dw",
        dh="dh",
        image="image",
        source=image_source,
        color_mapper=color_mapper
    )
    color_bar = bokeh.models.ColorBar(
        color_mapper=color_mapper,
        orientation='horizontal',
        background_fill_alpha=0,
        location='bottom_center')
    bokeh_figure.add_layout(color_bar, 'center')

    button = bokeh.models.Button()
    button.on_click(changer(bokeh_figure, color_mapper, source))

    document = bokeh.plotting.curdoc()
    document.add_root(button)
    document.add_root(bokeh_figure)


def changer(
        bokeh_figure,
        color_mapper,
        source):

    def wrapped():
        x_start = bokeh_figure.x_range.start
        x_end = bokeh_figure.x_range.end
        y_start = bokeh_figure.y_range.start
        y_end = bokeh_figure.y_range.end

        x = source.data["x"]
        y = source.data["y"]
        z = source.data["z"]

        pts = np.where((x < x_end) & (x > x_start) &
                       (y < y_end) & (y > y_start))
        values = z[pts]
        if len(values) == 0:
            return

        low = values.min()
        high = values.max()
        if low == high:
            low += 0.1
            high -= 0.1

        color_mapper.low = low
        color_mapper.high = high

    return wrapped


def regular_grid(x, y, z):
    """Map unstructured to regular grid

    Assumptions are made on the shape of the input and desired
    output arrays

    :param x: 2D array shaped (ny, nx)
    :param y: 2D array shaped (ny, nx)
    :param z: 2D array shaped (ny, nx)
    :returns: x, y, z mapped to regular grid with
              same shape as input arrays
    """
    if isinstance(z, list):
        z = np.asarray(z)
    ny, nx = x.shape
    xe, ye = np.meshgrid(
        np.linspace(x.min(), x.max(), nx),
        np.linspace(y.min(), y.max(), ny))
    ze = scipy.interpolate.griddata(
            (x.flatten(), y.flatten()), z.flatten(),
            (xe, ye))
    return xe, ye, ze


if __name__.startswith("bk"):
    main()
