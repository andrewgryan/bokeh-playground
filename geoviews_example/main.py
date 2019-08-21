import geoviews as gv
import geoviews.feature as gf
import tornado.ioloop
import bokeh.layouts
from bokeh.server.server import Server
import numpy as np
import template

renderer = gv.renderer('bokeh').instance(mode='server')


def index(document):
    feature = (gf.land * gf.ocean * gf.lakes * gf.rivers * gf.coastline * gf.borders).opts(
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
    document.add_root(bokeh.layouts.row(figure, name="map", sizing_mode="stretch_both"))
    document.template = template.INDEX


port = 8080
server = Server({"/": index}, port=port, io_loop=tornado.ioloop.IOLoop.current())
print("serving: localhost:{}".format(str(port)))
server.io_loop.start()
