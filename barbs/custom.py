from bokeh.models import Triangle
from bokeh.core.properties import Seq, Float


class Barbs(Triangle):
    __implementation__ = "custom.ts"
    xb = Seq(Float())
    yb = Seq(Float())
