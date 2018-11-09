from bokeh.models import Marker, Patches
from bokeh.core.properties import (
        Seq,
        Float,
        NumberSpec,
        DistanceSpec)


class DoubleBarbs(Patches):
    __implementation__ = "custom.ts"
    x = NumberSpec()
    y = NumberSpec()


class Barbs(Marker):
    __implementation__ = "custom.ts"
    xb = Seq(Float())
    yb = Seq(Float())
