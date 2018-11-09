from bokeh.models import Marker, Patches
from bokeh.core.properties import Seq, Float


class DoubleBarbs(Patches):
    __implementation__ = "custom.ts"
    x = Seq(Float())
    y = Seq(Float())


class Barbs(Marker):
    __implementation__ = "custom.ts"
    xb = Seq(Float())
    yb = Seq(Float())
