import bokeh.plotting
import bokeh.models
import bokeh.palettes
import numpy as np
import cartopy
import scipy.interpolate


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
    nx, ny = 20, 30
    x = np.linspace(90, 150, nx)
    y = np.linspace(-10, 30, ny)
    grid_x, grid_y = np.meshgrid(x, y)

    # Map to Google Mercator projection
    values = cartopy.crs.Mercator.GOOGLE.transform_points(
            cartopy.crs.PlateCarree(),
            grid_x.flatten(), grid_y.flatten())
    xt, yt, _ = values.T

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

    xe, ye, ze = evenly_space(xt, yt, zt, (nx, ny))

    # Plot filled color circles
    colored_circle(bokeh_figure,
            xe.flatten(),
            ye.flatten(),
            ze.flatten(),
            color_mapper)

    document = bokeh.plotting.curdoc()
    document.add_root(bokeh_figure)


def evenly_space(x, y, z, shape):
    """Map unstructured to regular grid"""
    nx, ny = shape
    src_x, src_y, src_z = x, y, z
    dst_x = np.linspace(x.min(), x.max(), nx)
    dst_y = np.linspace(y.min(), y.max(), ny)
    dst_x, dst_y = np.meshgrid(dst_x, dst_y)
    dst_z = scipy.interpolate.griddata(
            (src_x, src_y), src_z,
            (dst_x, dst_y))
    return dst_x, dst_y, dst_z


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

