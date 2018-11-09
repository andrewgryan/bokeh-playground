from bokeh.models import Triangle
from bokeh.core.properties import List, Float


class Barbs(Triangle):
    __implementation__ = "custom.ts"
    barb_x = List(Float())
    barb_y = List(Float())
