from bokeh.models import Triangle
from bokeh.core.properties import List, Float


class Barbs(Triangle):
    __implementation__ = "custom.ts"
    xb = List(Float(), help="Wind barb x vertices")
    yb = List(Float(), help="Wind barb y vertices")
