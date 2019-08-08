"""
Any geospatial application can benefit from a simple
layer implementation. Allowing users to craft, add, remove and even
save layers is vital to enable data exploration.

The decomposition of responsibilities between the :class:`Editor`,
:class:`Setting` and :class:`Layer` should be straight forward. The editor is
a controller/view on a settings object, that manipulates the settings object state. The
settings object(s) are :class:`Observable` that the Layer(s) respond to
by mirroring themselves.

"""
import bokeh.plotting
import numpy as np
from cbar import ColorbarLayout


class Observable(object):
    """Simple implementation of observer design pattern"""
    def __init__(self):
        self.subscribers = []

    def subscribe(self, callback):
        """On event trigger callback

        :param callback: function called when change occurs
        """
        self.subscribers.append(callback)

    def announce(self, value):
        """Notify subscribers of event

        :param value: passed to subscribed callbacks
        """
        for callback in self.subscribers:
            callback(value)


class Application(object):
    """Object to encapsulate various menus, data structures and views"""
    def __init__(self):
        self.figure = bokeh.plotting.figure(
            toolbar_location=None,
            min_border=0,
            x_range=(1e7, 1.5e7),
            y_range=(-2.5e6, 2.5e6),
            x_axis_type="mercator",
            y_axis_type="mercator",
            active_scroll="wheel_zoom",
            sizing_mode="stretch_both")
        self.figure.axis.visible = False
        tile = bokeh.models.WMTSTileSource(
            url="https://maps.wikimedia.org/osm-intl/{Z}/{X}/{Y}.png",
            attribution=""
        )
        self.figure.add_tile(tile)
        self.layers = []
        self.settings = []
        self.collection = Collection()
        self.buttons = {
            "add": bokeh.models.Button(label="Add layer", name="btn"),
        }
        self.buttons["add"].on_click(self.add_layer)
        self.dropdowns = {
            "layer": bokeh.models.Dropdown(label="Layers")
        }
        autolabel(self.dropdowns["layer"])
        self.dropdowns["layer"].on_change("value", self.on_layer)
        self.colorbar_layout = ColorbarLayout()
        self.buttons["colorbar_layout"] = bokeh.models.Button()
        self.buttons["colorbar_layout"].on_click(self.colorbar_layout.render)

        self.buttons["colorbar_toggle"] = bokeh.models.Button(label="Toggle")
        custom_js = bokeh.models.CustomJS(code="""
            let el = document.getElementById('cbar');
            if (el.style.display === "none") {
                el.style.display = "block";
            } else {
                el.style.display = "none";
            }
        """)
        self.buttons["colorbar_toggle"].js_on_click(custom_js)
        self.editor = Editor()

        tabs = bokeh.models.Tabs(tabs=[
            bokeh.models.Panel(
                child=bokeh.layouts.column(
                    self.editor.root,
                    self.buttons["add"],
                    self.collection.checkbox_group,
                ),
                title="Navigate"
            ),
            bokeh.models.Panel(
                child=bokeh.layouts.column(
                    self.dropdowns["layer"],
                    self.buttons["colorbar_layout"],
                    self.buttons["colorbar_toggle"],
                ),
                title="Edit layers"
            )
        ])

        controls = bokeh.layouts.column(
            bokeh.layouts.row(tabs),
            name="control"
        )

        self.roots = [
            bokeh.layouts.column(self.figure, sizing_mode="stretch_both"),
            controls,
            self.colorbar_layout.root
        ]
        self._i = 0

    def add_layer(self):
        name = "Layer: {}".format(self._i)
        xs = np.array([[0, 1, 1, 0, 0]]) + self._i
        ys = np.array([[0, 0, 1, 1, 0]]) + self._i
        source = bokeh.models.ColumnDataSource({
            "xs": xs,
            "ys": ys,
            "line_color": [self.editor.line_color]
        })

        layer = Layer(source)
        layer.attach(self.figure)
        self.layers.append(layer)

        setting = Setting()
        setting.subscribe(layer.on_setting)
        setting.line_color = self.editor.line_color
        self.settings.append(setting)

        self.collection.add_layer(layer, name, self._i)

        self.dropdowns["layer"].menu.append((name, name))
        self._i += 1

    def on_layer(self, attr, old, new):
        for i, (key, value) in enumerate(self.dropdowns["layer"].menu):
            if value != new:
                continue
            self.editor.setting = self.settings[i]
            return


class Collection(object):
    def __init__(self):
        self.layers = []
        self.checkbox_group = bokeh.models.CheckboxGroup(
            labels=[],
            active=[]
        )
        self.checkbox_group.on_change("active", self.on_checkbox)

    def add_layer(self, layer, name, i):
        self.layers.append(layer)
        self.checkbox_group.labels.append(name)
        self.checkbox_group.active.append(i)

    def on_checkbox(self, attr, old, new):
        for i, layer in enumerate(self.layers):
            for renderer in layer.renderers:
                renderer.visible = i in new


class Setting(Observable):
    """Observable controlled by an Editor used to sync Layer(s)"""
    def __init__(self, line_color=None):
        self._line_color = line_color
        super().__init__()

    @property
    def line_color(self):
        return getattr(self, "_line_color", None)

    @line_color.setter
    def line_color(self, value):
        self._line_color = value
        self.announce(self)


class Editor(object):
    """Responsible for editing layer settings"""
    def __init__(self, line_color="black"):
        self.active = False
        self._setting = None
        self.line_color = line_color
        self.buttons = {
            "edit": bokeh.models.CheckboxButtonGroup(labels=["Edit layer"])
        }
        self.buttons["edit"].on_change("active", self.on_active)
        self.dropdowns = {
            "model": bokeh.models.Dropdown(label="Model", menu=[
                ("Operational GA6", "Operational GA6"),
                ("Operational Tropical Africa", "Operational Tropical Africa"),
            ]),
            "variable": bokeh.models.Dropdown(label="Variable", menu=[
                ("air_temperature", "air_temperature"),
                ("cloud_fraction", "cloud_fraction"),
            ]),
            "line_color": bokeh.models.Dropdown(label="Color", menu=[
                ("red", "red"),
                ("orange", "orange"),
                ("yellow", "yellow"),
                ("green", "green"),
                ("blue", "blue"),
                ("black", "black"),
            ])
        }
        self.dropdowns["line_color"].on_change(
            "value", self.on_change("line_color"))
        for dropdown in self.dropdowns.values():
            autolabel(dropdown)
        self.root = bokeh.layouts.column(
            self.dropdowns["model"],
            self.dropdowns["variable"],
            self.dropdowns["line_color"],
            self.buttons["edit"]
        )

    @property
    def setting(self):
        return self._setting

    @setting.setter
    def setting(self, value):
        self._setting = value
        self.render(value)

    def render(self, setting):
        dropdown = self.dropdowns["line_color"]
        if dropdown.value != setting.line_color:
            dropdown.value = setting.line_color

    def on_active(self, attr, old, new):
        self.active = 0 in new

    def on_change(self, prop):
        """Pass user interaction on to underlying setting object"""
        def callback(attr, old, new):
            setattr(self, prop, new)
            if (self.active) and (self.setting is not None):
                setattr(self.setting, prop, new)
        return callback


class Layer(object):
    """Thin wrapper to reference objects related to a layer"""
    def __init__(self, source):
        self.renderers = []
        self.source = source
        self.glyph = bokeh.models.MultiLine(
            xs="xs", ys="ys", line_color="line_color")

    def on_setting(self, setting):
        self.source.data["line_color"] = [setting.line_color]

    def attach(self, figure):
        renderer = figure.add_glyph(self.source, self.glyph)
        self.renderers.append(renderer)


def autolabel(dropdown):
    """Helper to update dropdown label when choice is made"""
    def on_change(attr, old, new):
        for key, value in dropdown.menu:
            if value == new:
                dropdown.label = key
    dropdown.on_change("value", on_change)


def main():
    app = Application()
    document = bokeh.plotting.curdoc()
    for root in app.roots:
        document.add_root(root)


if __name__.startswith("bk"):
    main()
