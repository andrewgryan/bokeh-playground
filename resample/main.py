import bokeh.plotting
import numpy as np
import os
from functools import partial
import data
import view
import geo


NEXT = "NEXT"
PREVIOUS = "PREVIOUS"


def main():
    lon_range = (0, 30)
    lat_range = (0, 30)
    x_range, y_range = geo.web_mercator(
        lon_range,
        lat_range)
    figure = bokeh.plotting.figure(
        x_range=x_range,
        y_range=y_range,
        x_axis_type="mercator",
        y_axis_type="mercator",
        active_scroll="wheel_zoom")
    tile = bokeh.models.WMTSTileSource(
        url="https://maps.wikimedia.org/osm-intl/{Z}/{X}/{Y}.png",
        attribution=""
    )
    figures = [figure]
    for _ in range(2):
        f = bokeh.plotting.figure(
            x_range=figure.x_range,
            y_range=figure.y_range,
            x_axis_type="mercator",
            y_axis_type="mercator",
            active_scroll="wheel_zoom")
        figures.append(f)

    for f in figures:
        f.axis.visible = False
        f.toolbar.logo = None
        f.toolbar_location = None
        f.min_border = 0
        f.add_tile(tile)

    figure_row = bokeh.layouts.row(*figures,
            sizing_mode="stretch_both")
    figure_row.children = [figures[0]]  # Trick to keep correct sizing modes

    figure_drop = bokeh.models.Dropdown(
            label="Figure",
            menu=[(str(i), str(i)) for i in [1, 2, 3]])

    def on_click(value):
        if int(value) == 1:
            figure_row.children = [
                    figures[0]]
        elif int(value) == 2:
            figure_row.children = [
                    figures[0],
                    figures[1]]
        elif int(value) == 3:
            figure_row.children = [
                    figures[0],
                    figures[1],
                    figures[2]]

    figure_drop.on_click(on_click)

    color_mapper = bokeh.models.LinearColorMapper(
            low=0,
            high=1,
            palette=bokeh.palettes.Plasma[256])
    for figure in figures:
        colorbar = bokeh.models.ColorBar(
            color_mapper=color_mapper,
            orientation="horizontal",
            background_fill_alpha=0.,
            location="bottom_center",
            major_tick_line_color="black",
            bar_line_color="black")
        figure.add_layout(colorbar, 'center')

    paths = data.FILE_DB.files
    renderers = []
    image_sources = []
    image_viewers = []
    image_loaders = []
    for name in data.FILE_DB.names:
        loader = data.LOADERS[name]
        if isinstance(loader, data.RDT):
            viewer = RDT(loader)
        elif isinstance(loader, data.EarthNetworks):
            viewer = EarthNetworks(loader)
        elif isinstance(loader, data.GPM):
            viewer = view.GPMView(loader)
            image_loaders.append(loader)
            image_viewers.append(viewer)
            image_sources.append(viewer.source)
        else:
            viewer = view.UMView(loader)
            image_loaders.append(loader)
            image_viewers.append(viewer)
            image_sources.append(viewer.source)
        sub_renderers = []
        for figure in figures:
            if isinstance(viewer, (view.GPMView, view.UMView)):
                renderer = viewer.add_figure(
                        figure,
                        color_mapper)
            else:
                renderer = viewer.add_figure(figure)
            sub_renderers.append(renderer)
        renderers.append(sub_renderers)

    features = []
    for figure in figures:
        features += [
            add_feature(figure, data.COASTLINES),
            add_feature(figure, data.BORDERS)]
    toggle = bokeh.models.CheckboxButtonGroup(
            labels=["Coastlines"],
            active=[0],
            width=135)

    def on_change(attr, old, new):
        if len(new) == 1:
            for feature in features:
                feature.visible = True
        else:
            for feature in features:
                feature.visible = False

    toggle.on_change("active", on_change)

    dropdown = bokeh.models.Dropdown(
            label="Color",
            menu=[
                ("Black", "black"),
                ("White", "white")],
            width=50)
    dropdown.on_click(change_label(dropdown))

    def on_click(value):
        for feature in features:
            feature.glyph.line_color = value

    dropdown.on_click(on_click)

    slider = bokeh.models.Slider(
        start=0,
        end=1,
        step=0.1,
        value=1.0,
        show_value=False)
    custom_js = bokeh.models.CustomJS(
            args=dict(renderers=sum(renderers, [])),
            code="""
            renderers.forEach(function (r) {
                r.glyph.global_alpha = cb_obj.value
            })
            """)
    slider.js_on_change("value", custom_js)

    palettes = {
            "Viridis": bokeh.palettes.Viridis[256],
            "Magma": bokeh.palettes.Magma[256],
            "Inferno": bokeh.palettes.Inferno[256],
            "Plasma": bokeh.palettes.Plasma[256]
    }
    palette_controls = PaletteControls(
            color_mapper,
            palettes)

    mapper_limits = MapperLimits(image_sources, color_mapper)

    image_controls = ImageControls(data.FILE_DB.names, renderers)
    rows = []
    for drop, group in zip(
            image_controls.drops,
            image_controls.groups):
        row = bokeh.layouts.row(drop, group)
        rows.append(row)
    lcr_column = bokeh.layouts.column(*rows)

    def on_click(value):
        if int(value) == 1:
            for g in image_controls.groups:
                g.labels = ["Show"]
        elif int(value) == 2:
            for g in image_controls.groups:
                g.labels = ["L", "R"]
        elif int(value) == 3:
            for g in image_controls.groups:
                g.labels = ["L", "C", "R"]

    figure_drop.on_click(on_click)

    variables = image_loaders[0].variables
    pressures = image_loaders[0].pressures
    field_controls = FieldControls(
            variables,
            pressures)
    for viewer in image_viewers:
        field_controls.subscribe(viewer.render)

    div = bokeh.models.Div(text="", width=10)
    border_row = bokeh.layouts.row(
        bokeh.layouts.column(toggle),
        bokeh.layouts.column(div),
        bokeh.layouts.column(dropdown))

    time_controls = TimeControls()
    time_controls.subscribe(field_controls.on_time_control)

    document = bokeh.plotting.curdoc()
    document.add_root(
        bokeh.layouts.column(
            bokeh.layouts.row(figure_drop),
            time_controls.layout,
            border_row,
            lcr_column,
            bokeh.layouts.row(slider),
            bokeh.layouts.row(field_controls.drop),
            bokeh.layouts.row(field_controls.radio),
            bokeh.layouts.row(palette_controls.drop),
            bokeh.layouts.row(mapper_limits.low_input),
            bokeh.layouts.row(mapper_limits.high_input),
            bokeh.layouts.row(mapper_limits.checkbox),
            name="controls"))
    document.add_root(figure_row)


class EarthNetworks(object):
    def __init__(self, loader):
        frame = loader.frame
        if frame is not None:
            x, y = geo.web_mercator(
                    frame.longitude,
                    frame.latitude)
            date = frame.date
            longitude = frame.longitude
            latitude = frame.latitude
            flash_type = frame.flash_type
        else:
            x, y = [], []
            date = []
            longitude = []
            latitude = []
            flash_type = []
        self.source = bokeh.models.ColumnDataSource({
            "x": x,
            "y": y,
            "date": date,
            "longitude": longitude,
            "latitude": latitude,
            "flash_type": flash_type,
        })

    def add_figure(self, figure):
        renderer = figure.circle(
                x="x",
                y="y",
                size=10,
                source=self.source)
        tool = bokeh.models.HoverTool(
                tooltips=[
                    ('Time', '@date{%F}'),
                    ('Lon', '@longitude'),
                    ('Lat', '@latitude'),
                    ('Flash type', '@flash_type')],
                formatters={
                    'date': 'datetime'
                },
                renderers=[renderer])
        figure.add_tools(tool)
        return renderer


class RDT(object):
    def __init__(self, loader):
        self.color_mapper = bokeh.models.CategoricalColorMapper(
                palette=bokeh.palettes.Spectral6,
                factors=["0", "1", "2", "3", "4"])
        self.source = bokeh.models.GeoJSONDataSource(
                geojson=loader.geojson)

    def add_figure(self, figure):
        renderer = figure.patches(
            xs="xs",
            ys="ys",
            fill_alpha=0,
            line_width=2,
            line_color={
                'field': 'PhaseLife',
                'transform': self.color_mapper},
            source=self.source)
        tool = bokeh.models.HoverTool(
                tooltips=[
                    ('CType', '@CType'),
                    ('CRainRate', '@CRainRate'),
                    ('ConvTypeMethod', '@ConvTypeMethod'),
                    ('ConvType', '@ConvType'),
                    ('ConvTypeQuality', '@ConvTypeQuality'),
                    ('SeverityIntensity', '@SeverityIntensity'),
                    ('MvtSpeed', '@MvtSpeed'),
                    ('MvtDirection', '@MvtDirection'),
                    ('NumIdCell', '@NumIdCell'),
                    ('CTPressure', '@CTPressure'),
                    ('CTPhase', '@CTPhase'),
                    ('CTReff', '@CTReff'),
                    ('LonG', '@LonG'),
                    ('LatG', '@LatG'),
                    ('ExpansionRate', '@ExpansionRate'),
                    ('BTmin', '@BTmin'),
                    ('BTmoy', '@BTmoy'),
                    ('CTCot', '@CTCot'),
                    ('CTCwp', '@CTCwp'),
                    ('NbPosLightning', '@NbPosLightning'),
                    ('SeverityType', '@SeverityType'),
                    ('Surface', '@Surface'),
                    ('Duration', '@Duration'),
                    ('CoolingRate', '@CoolingRate'),
                    ('Phase life', '@PhaseLife')],
                renderers=[renderer])
        figure.add_tools(tool)
        return renderer


class Observable(object):
    def __init__(self):
        self.uid = 0
        self.listeners = []

    def subscribe(self, listener):
        self.uid += 1
        self.listeners.append(listener)
        return partial(self.unsubscribe, int(self.uid))

    def unsubscribe(self, uid):
        del self.listeners[uid]

    def announce(self, *args):
        for listener in self.listeners:
            listener(*args)


class FieldControls(Observable):
    def __init__(self, variables, pressures):
        self.itime = 0
        self.ipressure = 0
        self.variables = variables
        self.pressures = pressures
        self.drop = bokeh.models.Dropdown(
                label="Variables",
                menu=[(v, v) for v in self.variables],
                width=50)
        self.drop.on_click(change_label(self.drop))
        self.drop.on_click(self.on_click)
        self.radio = bokeh.models.RadioGroup(
                labels=[str(int(p)) for p in self.pressures],
                active=self.ipressure,
                inline=True)
        self.radio.on_change("active", self.on_radio)
        super().__init__()

    def on_click(self, value):
        self.variable = value
        self.render()

    def on_radio(self, attr, old, new):
        if new is not None:
            self.ipressure = new
            self.render()

    def render(self):
        if self.variable is None:
            return
        self.announce(self.variable, self.ipressure, self.itime)

    def on_time_control(self, action):
        if action == NEXT:
            self.next_time()
        elif action == PREVIOUS:
            self.previous_time()

    def next_time(self):
        self.itime += +1
        self.render()

    def previous_time(self):
        self.itime += -1
        self.render()


class TimeControls(Observable):
    def __init__(self):
        self.plus = bokeh.models.Button(label="+", width=140)
        self.plus.on_click(self.on_plus)
        self.minus = bokeh.models.Button(label="-", width=140)
        self.minus.on_click(self.on_minus)
        self.layout = bokeh.layouts.row(
                bokeh.layouts.widgetbox(self.minus, width=140),
                bokeh.layouts.widgetbox(self.plus, width=140),
                width=300)
        super().__init__()

    def on_plus(self):
        self.announce(NEXT)

    def on_minus(self):
        self.announce(PREVIOUS)


class MapperLimits(object):
    def __init__(self, sources, color_mapper, fixed=False):
        self.fixed = fixed
        self.sources = sources
        for source in self.sources:
            source.on_change("data", self.on_source_change)
        self.color_mapper = color_mapper
        self.low_input = bokeh.models.TextInput(title="Low:")
        self.low_input.on_change("value",
                self.change(color_mapper, "low", float))
        self.color_mapper.on_change("low",
                self.change(self.low_input, "value", str))
        self.high_input = bokeh.models.TextInput(title="High:")
        self.high_input.on_change("value",
                self.change(color_mapper, "high", float))
        self.color_mapper.on_change("high",
                self.change(self.high_input, "value", str))
        self.checkbox = bokeh.models.CheckboxGroup(
                labels=["Fixed"],
                active=[])
        self.checkbox.on_change("active", self.on_checkbox_change)

    def on_checkbox_change(self, attr, old, new):
        if len(new) == 1:
            self.fixed = True
        else:
            self.fixed = False

    def on_source_change(self, attr, old, new):
        if self.fixed:
            return
        images = []
        for source in self.sources:
            if len(source.data["image"]) == 0:
                continue
            images.append(source.data["image"][0])
        if len(images) > 0:
            low = np.min([np.min(x) for x in images])
            high = np.max([np.max(x) for x in images])
            self.color_mapper.low = low
            self.color_mapper.high = high

    @staticmethod
    def change(widget, prop, dtype):
        def wrapper(attr, old, new):
            if old == new:
                return
            if getattr(widget, prop) == dtype(new):
                return
            setattr(widget, prop, dtype(new))
        return wrapper


class PaletteControls(object):
    def __init__(self, color_mapper, palettes):
        self.color_mapper = color_mapper
        self.palettes = palettes
        self.drop = bokeh.models.Dropdown(
                label="Palettes",
                menu=[(k, k) for k in self.palettes.keys()])
        self.drop.on_click(change_label(self.drop))
        self.drop.on_click(self.on_click)

    def on_click(self, value):
        self.color_mapper.palette = self.palettes[value]


class ImageControls(object):
    def __init__(self, names, renderers):
        self.names = names
        self.renderers = renderers
        self.state = [
                (0, [True, False, False]),
                (1, [True, False, False]),
                (2, [True, False, False]),
                (3, [False, False, False])]
        self.previous_state = None
        self.drops = []
        self.groups = []
        for i in range(3):
            drop = bokeh.models.Dropdown(
                    menu=[(n, n) for n in names],
                    label=names[i],
                    width=150)
            drop.on_click(select(drop))
            drop.on_change('value', self.on_dropdown(i))
            self.drops.append(drop)

            group = bokeh.models.CheckboxButtonGroup(
                    labels=["Show"],
                    active=[0])
            group.on_change("active", self.on_radio(i))
            self.groups.append(group)

        self.render()

    def on_dropdown(self, i):
        def wrapper(attr, old, new):
            if old != new:
                _, flags = self.state[i]
                self.state[i] = (self.names.index(new), flags)
                self.render()
        return wrapper

    def on_radio(self, i):
        def wrapper(attr, old, new):
            _, flags = self.state[i]
            for j in old:
                if j not in new:
                    flags[j] = False
            for j in new:
                if j not in old:
                    flags[j] = True
            self.render()
        return wrapper

    def render(self):
        if self.previous_state is not None:
            # Hide deselected states
            lost_items = (
                    set(self.flatten(self.previous_state)) -
                    set(self.flatten(self.state)))
            for i, j, _ in lost_items:
                self.renderers[i][j].visible = False

        # Sync visible states with menu choices
        states = set(self.flatten(self.state))
        hidden = [(i, j) for i, j, v in states if not v]
        visible = [(i, j) for i, j, v in states if v]
        for i, j in hidden:
            self.renderers[i][j].visible = False
        for i, j in visible:
            self.renderers[i][j].visible = True

        # Copy old state
        self.previous_state = list(self.state)

    @staticmethod
    def flatten(state):
        items = []
        for index, flags in state:
            items += [(index, i, f) for i, f in enumerate(flags)]
        return items


def select(dropdown):
    def wrapped(new):
        for label, value in dropdown.menu:
            if value == new:
                dropdown.label = label
    return wrapped


def change_label(widget):
    def wrapped(value):
        widget.label = str(value)
    return wrapped


def change(widget, prop, dtype):
    def wrapper(attr, old, new):
        if old == new:
            return
        if getattr(widget, prop) == dtype(new):
            return
        setattr(widget, prop, dtype(new))
    return wrapper


def add_feature(figure, data):
    source = bokeh.models.ColumnDataSource(data)
    return figure.multi_line(
        xs="xs",
        ys="ys",
        source=source,
        color="white")


if __name__.startswith("bk"):
    main()
