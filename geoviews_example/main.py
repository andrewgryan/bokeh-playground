import xarray
import geoviews as gv
import geoviews.feature as gf
import tornado.ioloop
import bokeh.layouts
from bokeh.server.server import Server
import numpy as np
import template

renderer = gv.renderer('bokeh').instance(mode='server')


def index(document):
    # Load some data
    path = "~/cache/highway_ga6_20190315T0000Z.nc"
    air_temperature = xarray.open_dataset(path).air_temperature
    dataset = gv.Dataset(air_temperature[0])
    contours = dataset.to(gv.LineContours, ['longitude_0', 'latitude_0'])

    # Create map
    feature = (gf.land * gf.ocean * gf.lakes * gf.rivers * gf.coastline * gf.borders * contours).opts(
            global_extent=True,
            xaxis=None,
            yaxis=None,
            border=0,
            active_tools=["pan", "wheel_zoom"])
    figure = renderer.get_plot(feature).state
    figure.sizing_mode = "stretch_both"
    figure.aspect_ratio = 1
    figure.axis.visible = False
    figure.toolbar.logo = None
    figure.toolbar_location = None
    figure.title.text = ""

    contours.data = air_temperature[-1]

    document.add_root(bokeh.layouts.row(figure, name="map", sizing_mode="stretch_both"))
    document.template = template.INDEX


port = 8080
server = Server({"/": index}, port=port, io_loop=tornado.ioloop.IOLoop.current())
print("serving: localhost:{}".format(str(port)))
server.io_loop.start()
