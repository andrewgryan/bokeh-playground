import bokeh.plotting
import bokeh.models
import numpy as np
import cartopy


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
    nx, ny = 10, 10
    x = np.linspace(90, 150, nx)
    y = np.linspace(-10, 30, ny)
    X, Y = np.meshgrid(x, y)

    # Map to Google Mercator projection
    values = cartopy.crs.Mercator.GOOGLE.transform_points(
            cartopy.crs.PlateCarree(),
            X.flatten(), Y.flatten())
    xt, yt, _ = values.T

    bokeh_figure.circle(x=xt, y=yt)

    # Linear space in Google Mercator projection
    x = np.linspace(xt.min(), xt.max(), nx)
    y = np.linspace(yt.min(), yt.max(), ny)
    x, y = np.meshgrid(x, y)
    bokeh_figure.circle(x=x.flatten(), y=y.flatten(),
            fill_color="red",
            line_color="red")

    document = bokeh.plotting.curdoc()
    document.add_root(bokeh_figure)


if __name__.startswith("bk"):
    main()

