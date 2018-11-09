from bokeh.models import Marker
from bokeh.core.properties import Seq, Float


class Barbs(Marker):
    __implementation__ = "custom.ts"
    xb = Seq(Float())
    yb = Seq(Float())
