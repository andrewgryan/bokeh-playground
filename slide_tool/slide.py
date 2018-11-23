from bokeh.core.properties import Instance
from bokeh.models import Tool, Span

class SlideTool(Tool):
    __implementation__ = "slide.ts"
    span = Instance(Span)
