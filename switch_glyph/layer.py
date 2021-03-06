"""
Layer architecture

"""
import bokeh.models
import bokeh.layouts
import numpy as np


UI_ADD = "UI_ADD"
UI_REMOVE = "UI_REMOVE"


def ui_add(dropdown, group):
    return {
        "kind": UI_ADD,
        "payload": {
            "dropdown": dropdown,
            "group": group
        }
    }


def ui_remove():
    return {
        "kind": UI_REMOVE
    }


class UI(object):
    """User interface to layers"""
    def __init__(self):
        self.buttons = {
            "add": bokeh.models.Button(label="Add"),
            "remove": bokeh.models.Button(label="Remove"),
        }
        self.buttons["add"].on_click(self.on_add)
        self.buttons["remove"].on_click(self.on_remove)
        self.layout = bokeh.layouts.column(
                bokeh.layouts.row(
                    self.buttons["remove"],
                    self.buttons["add"]))

    def on_add(self):
        dropdown = bokeh.models.Dropdown()
        group = bokeh.models.CheckboxButtonGroup()
        row = bokeh.layouts.row(dropdown, group)
        self.layout.children.insert(-1, row)
        # self.notify(ui_add(dropdown, group))

    def on_remove(self):
        self.layout.children.pop(-2)
        # self.notify(ui_remove())


class Controls(object):
    def __init__(self, figures, menu):
        self.loader_factory = LoaderFactory()
        self.figures = figures
        self.menu = menu

    def add_control(self, color):
        source_factory = SourceFactory()
        views = []
        for figure in self.figures:
            glyph_factory = GlyphFactory(source_factory, figure, color)
            view = VisibleGlyphs(glyph_factory)
            views.append(view)

        dropdown = bokeh.models.Dropdown(menu=self.menu)
        dropdown.on_change("value", self.on_change(source_factory))
        for view in views:
            dropdown.on_change("value", view.on_change)
        return dropdown, views

    def on_change(self, source_factory):
        """Connect sources to file system"""
        def callback(attr, old, file_name):
            source = source_factory.get_source(file_name)
            source.data = self.loader_factory.load(file_name)
        return callback


class LeftRight(object):
    """Control left/right visibility"""
    def __init__(self, views):
        self.views = views
        self.group = bokeh.models.CheckboxButtonGroup(
                labels=["L", "R"])
        self.group.on_change("active", self.on_change)

    def on_change(self, attr, old, new):
        for i, view in enumerate(self.views):
            view.visible = i in new


class LoaderFactory(object):
    """I/O layer data from disk"""
    def __init__(self):
        self.cache = {}

    def load(self, file_name):
        if file_name not in self.cache:
            # Random data per file
            self.cache[file_name] = {
                "x": np.random.randn(10),
                "y": np.random.randn(10)
            }
        return self.cache[file_name]


class VisibleGlyphs(object):
    """Manages glyphs related to a single layer on a single figure"""
    def __init__(self, glyph_factory):
        self.glyph_factory = glyph_factory
        self.glyphs = {}
        self.key = None  # Needed to set visibility state
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
        self.key = self.glyph_factory.glyph_key(new)
        if self.key not in self.glyphs:
            self.glyphs[self.key] = self.glyph_factory(new, visible=self.visible)

        if self.visible:
            # Mute unselected glyphs
            for key, glyph in self.glyphs.items():
                glyph.visible = key == self.key
        else:
            # Mute all glyphs
            for glyph in self.glyphs.values():
                glyph.visible = False


class GlyphFactory(object):
    """Delegates construction of GlyphRenderers to other objects"""
    def __init__(self, source_factory, figure, color):
        self.source_factory = source_factory
        self.figure = figure
        self.color = color

    def __call__(self, file_name, visible=True):
        source = self.source_factory.get_source(file_name)
        key = self.glyph_key(file_name)
        if key == "circle":
            return self.figure.circle(x="x", y="y", source=source,
                    fill_color=self.color,
                    visible=visible)
        elif key == "line":
            return self.figure.line(x="x", y="y", source=source,
                    line_color=self.color,
                    visible=visible)
        elif key == "square":
            return self.figure.square(x="x", y="y", source=source,
                    fill_color=self.color,
                    visible=visible)

    @staticmethod
    def glyph_key(file_name):
        if file_name.endswith(".nc"):
            return "line"
        elif file_name.endswith(".json"):
            return "circle"
        else:
            return "square"


class SourceFactory(object):
    """Maintains sources related to a single layer

    Allows sources to be swapped out as and when the data underlying
    the layer changes, e.g. ColumnDataSource to GeoJSONSource,
    or more subtle changes in source.data dict structures
    """
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
