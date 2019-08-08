import bokeh.models


class View(object):
    """Manages glyphs related to a single layer on a figure"""
    def __init__(self, layer, figure, color):
        self.layer = layer
        self.figure = figure
        self.color = color
        self.glyphs = {}
        self.key = None
        self._visible = True

    @property
    def visible(self):
        return self._visible

    @visible.setter
    def visible(self, flag):
        try:
            self.glyphs[self.key].visible = flag
        except KeyError:
            pass
        self._visible = flag

    def on_change(self, attr, old, new):
        # Select/construct glyph_renderer on demand
        self.key = self.glyph_key(new)
        if self.key not in self.glyphs:
            source = self.layer.get_source(new)
            self.glyphs[self.key] = self.glyph_factory(self.key, source)

        if self.visible:
            # Mute unselected glyphs
            for key, glyph in self.glyphs.items():
                glyph.visible = key == self.key
        else:
            # Mute all glyphs
            for glyph in self.glyphs.values():
                glyph.visible = False

    def glyph_factory(self, key, source):
        if key == "circle":
            return self.figure.circle(x="x", y="y", source=source,
                    fill_color=self.color,
                    visible=self.visible)
        elif key == "line":
            return self.figure.line(x="x", y="y", source=source,
                    line_color=self.color,
                    visible=self.visible)
        elif key == "square":
            return self.figure.square(x="x", y="y", source=source,
                    fill_color=self.color,
                    visible=self.visible)

    @staticmethod
    def glyph_key(file_name):
        if file_name.endswith(".nc"):
            return "line"
        elif file_name.endswith(".json"):
            return "circle"
        else:
            return "square"


class Layer(object):
    """Maintains data sources related to a single layer"""
    def __init__(self):
        self.sources = {}

    @staticmethod
    def key(file_name):
        if file_name.endswith(".json"):
            return "geojson"
        else:
            return "column_data_source"

    def get_source(self, file_name):
        key = self.key(file_name)
        if key not in self.sources:
            self.sources[key] =  bokeh.models.ColumnDataSource({
                "x": [],
                "y": [],
            })
        return self.sources[key]
