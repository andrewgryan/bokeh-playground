import bokeh.plotting
import bokeh.models
import bokeh.tile_providers

from_model = True
if from_model:
    tile = bokeh.models.WMTSTileSource(
        url='http://c.tile.openstreetmap.org/{Z}/{X}/{Y}.png',
        attribution="Attribution text goes here"
    )
else:
    tile = bokeh.tile_porviders.STAMEN_TONER

figure = bokeh.plotting.figure(
        x_range=(-200000, 600000),
        y_range=(-100000, 700000),
        x_axis_type="mercator",
        y_axis_type="mercator",
        sizing_mode='stretch_both',
        match_aspect=True,
        )
figure.add_tile(tile)

document = bokeh.plotting.curdoc()
document.add_root(figure)
