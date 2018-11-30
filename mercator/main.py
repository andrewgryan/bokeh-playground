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
    nx, ny = 10, 5
    x = np.linspace(90, 150, nx)
    y = np.linspace(-10, 30, ny)
    grid_x, grid_y = np.meshgrid(x, y)

    # Map to Google Mercator projection
    gl = cartopy.crs.Mercator.GOOGLE
    pc = cartopy.crs.PlateCarree()
    xt, yt, _ = gl.transform_points(pc, grid_x.flatten(), grid_y.flatten()).T

    zt = yt

    palette = bokeh.palettes.Viridis256
    color_mapper = bokeh.transform.linear_cmap(
            field_name="z",
            palette=palette,
            low=zt.min(),
            high=zt.max())

    colored_circle(bokeh_figure,
            xt,
            yt,
            zt,
            color_mapper)

    use_stretch = True
    if use_stretch:
        ym = stretch.web_mercator_y(y)
        transform = stretch.stretch_transform(ym, axis=0)
        xm = xt.reshape(ny, nx)[0, :]
        xe, ye = np.meshgrid(xm, stretch.equal_spaced(ym))
        ze = transform(ye)
    else:
        xe, ye, ze = regular_grid(xt.reshape(ny, nx),
                                  yt.reshape(ny, nx),
                                  zt.reshape(ny, nx))

    # Plot filled color circles
    colored_circle(bokeh_figure,
            xe.flatten(),
            ye.flatten(),
            ze.flatten(),
            color_mapper)

    document = bokeh.plotting.curdoc()
    document.add_root(bokeh_figure)


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


def colored_circle(bokeh_figure, x, y, z, color_mapper):
    source = bokeh.models.ColumnDataSource({
        "x": x,
        "y": y,
        "z": z
        })
    bokeh_figure.circle(
            x="x",
            y="y",
            fill_color=color_mapper,
            line_color=color_mapper,
            source=source)


if __name__.startswith("bk"):
    main()
