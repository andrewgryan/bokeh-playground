import bokeh.plotting
import bokeh.models
import bokeh.palettes
import numpy as np
import cartopy.crs
import json


def main():
    tile = bokeh.models.WMTSTileSource(
        url='http://c.tile.openstreetmap.org/{Z}/{X}/{Y}.png',
        attribution="Attribution text goes here"
    )

    figure = bokeh.plotting.figure(
        x_axis_type="mercator",
        y_axis_type="mercator",
        active_scroll="wheel_zoom",
    sizing_mode="stretch_both")
    figure.add_tile(tile)

    path = "/data/local/frrn/buckets/stephen-sea-public-london/rdt_json/RDT_features_eastafrica_201810190000.json"
    with open(path) as stream:
        geojson = stream.read()

    # Map to Web-Mercator
    with open(path) as stream:
        rdt = json.load(stream)
    copy = dict(rdt)
    for i, feature in enumerate(rdt["features"]):
        coordinates = feature['geometry']['coordinates'][0]
        lons, lats = np.asarray(coordinates).T
        x, y = google_mercator(lons, lats)
        c = np.array([x, y]).T.tolist()
        copy["features"][i]['geometry']['coordinates'][0] = c

    geojson = json.dumps(copy)

    # Make pretty polygons
    color_mapper = bokeh.models.LinearColorMapper(palette=bokeh.palettes.Viridis6)
    source = bokeh.models.GeoJSONDataSource(geojson=geojson)
    figure.multi_line(xs='xs', ys='ys',
                      line_width=2,
        line_color={'field': 'NumIdCell', 'transform': color_mapper},
        source=source)

    document = bokeh.plotting.curdoc()
    document.add_root(figure)


def google_mercator(lons, lats):
    gl = cartopy.crs.Mercator.GOOGLE
    pc = cartopy.crs.PlateCarree()
    x, y, _ = gl.transform_points(pc, flatten(lons), flatten(lats)).T
    return x, y


def flatten(a):
    if isinstance(a, list):
        a = np.array(a, dtype=np.float)
    return a.flatten()


if __name__.startswith("bk"):
    main()
