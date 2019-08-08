"""

Dynamic colorbar arrangements can be achieved through
a set operation on tuples ``(name, level, min, max, ...)`` that
describe a colorbar.

"""
import bokeh.plotting
import bokeh.layouts
import bokeh.models


class Setting(object):
    def __init__(self, palette, levels, low, high):
        self.palette = palette
        self.levels = int(levels)
        self.low = low
        self.high = high

    def __repr__(self):
        if self.__class__.__module__ is None:
            name = self.__class__.__name__
        else:
            name = ".".join([
                self.__class__.__module__,
                self.__class__.__name__
            ])

        def _str(s):
            if isinstance(s, str):
                return "'{}'".format(s)
            return str(s)
        args = [_str(a) for a in [
            self.palette,
            self.levels,
            self.low,
            self.high]]
        return "{}({})".format(name, ", ".join(args))

    def __eq__(self, other):
        return (
            (self.palette == other.palette) and
            (self.levels == other.levels) and
            (self.low == other.low) and
            (self.high == other.high))

    @classmethod
    def default(cls, low=0):
        """Construct colorbar settings"""
        return cls("viridis", 256, low, 1)


class ColorbarLayout(object):
    """Responsible for stacking colorbar objects"""
    def __init__(self):
        self.height = 60
        self.width = 500
        self.padding = 5
        self.palettes = [
            "Greys256",
            "Viridis256"
        ]
        self.figures = {}
        self.color_mappers = {}
        self.root = bokeh.layouts.column(*[], name="cbar")

    def render(self):
        for palette in self.palettes:
            if palette in self.figures:
                self.color_mappers[palette].high = 2
                continue

            figure = bokeh.plotting.figure(
                plot_height=self.height,
                plot_width=self.width,
                toolbar_location=None,
                min_border=0,
                background_fill_alpha=0,
                border_fill_alpha=0,
                outline_line_color=None)
            figure.axis.visible = False
            color_mapper = bokeh.models.LinearColorMapper(
                palette=palette, low=0, high=1)
            colorbar = bokeh.models.ColorBar(
                color_mapper=color_mapper,
                location=(0, 0),
                height=10,
                width=int(self.width - (20 + self.padding)),
                padding=self.padding,
                orientation="horizontal",
                major_tick_line_color="black",
                bar_line_color="black",
                background_fill_alpha=0.,
            )
            colorbar.title = ""
            figure.add_layout(colorbar, 'center')
            self.root.children.append(figure)
            self.figures[palette] = figure
            self.color_mappers[palette] = color_mapper
