import numpy as np
import bokeh.plotting
import bokeh.models
import bokeh.tile_providers
import numpy as np
import cartopy


def web_mercator(lons, lats):
    lons, lats = np.asarray(lons), np.asarray(lats)
    google_mercator = cartopy.crs.Mercator.GOOGLE
    plate_carree = cartopy.crs.PlateCarree()
    values = google_mercator.transform_points(
            plate_carree,
            lons,
            lats)
    x, y, _ = values.T
    return x, y


from_model = True
if from_model:
    tile = bokeh.models.WMTSTileSource(
        url='http://c.tile.openstreetmap.org/{Z}/{X}/{Y}.png',
        attribution="Attribution text goes here"
    )
else:
    tile = bokeh.tile_porviders.STAMEN_TONER

figure = bokeh.plotting.figure(
        x_range=(-2000000, 6000000),
        y_range=(-1000000, 7000000),
        x_axis_type="mercator",
        y_axis_type="mercator",
        sizing_mode='stretch_both',
        match_aspect=True,
        )
figure.add_tile(tile)

# Plot big square line
lons = [-80, 80, 80, -80, -80]
lats = [-70, -70, 70, 70, -70]
x, y = web_mercator(lons, lats)
figure.line(x=x, y=y)

# Add a random ImageRGBA plot to illustrate concept
N = 100
rgba = np.zeros((N, N, 4), dtype=np.uint8)
x = np.linspace(0, 255, N)
y = np.linspace(0, 255, N)
X, Y = np.meshgrid(x, y)
rgba[:, :, 0] = X.astype(np.uint8)
rgba[:, :, 1] = Y.astype(np.uint8)
rgba[:, :, 2] = 0
rgba[:, :, 3] = 255
source = bokeh.models.ColumnDataSource({
    "x": [0],
    "y": [0],
    "dw": [500000],
    "dh": [500000],
    "image": [rgba]
})
figure.image_rgba(
    x="x",
    y="y",
    dw="dw",
    dh="dh",
    image="image",
    source=source
)

document = bokeh.plotting.curdoc()
document.add_root(figure)
