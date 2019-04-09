import bokeh.plotting
import cartopy
import numpy as np
import os
import data
import geo


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
            viewer = GPMViewer(loader)
            image_loaders.append(loader)
            image_viewers.append(viewer)
            image_sources.append(viewer.source)
        else:
            viewer = UMViewer(loader)
            image_loaders.append(loader)
            image_viewers.append(viewer)
            image_sources.append(viewer.source)
        sub_renderers = []
        for figure in figures:
            if isinstance(viewer, (GPMViewer, UMViewer)):
                renderer = viewer.add_figure(
                        figure,
                        color_mapper)
            else:
                renderer = viewer.add_figure(figure)
            sub_renderers.append(renderer)
        renderers.append(sub_renderers)

    features = []
    for figure in figures:
        coastline = cartopy.feature.COASTLINE
        coastline.scale = "50m"
        features += [
            add_feature(figure, cartopy.feature.BORDERS),
            add_feature(figure, coastline)]
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

    field_controls = FieldControls(
            image_viewers,
            image_loaders)

    div = bokeh.models.Div(text="", width=10)
    border_row = bokeh.layouts.row(
        bokeh.layouts.column(toggle),
        bokeh.layouts.column(div),
        bokeh.layouts.column(dropdown))


    document = bokeh.plotting.curdoc()
    document.add_root(
        bokeh.layouts.column(
            bokeh.layouts.row(figure_drop),
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


class GPMViewer(object):
    def __init__(self, loader):
        self.loader = loader
        self.empty = {
                "x": [],
                "y": [],
                "dw": [],
                "dh": [],
                "image": []}
        self.source = bokeh.models.ColumnDataSource(self.empty)

    def render(self, variable, ipressure):
        if variable != "precipitation_flux":
            self.source.data = self.empty
        else:
            self.source.data = self.loader.image()

    def add_figure(self, figure, color_mapper):
        return figure.image(
                x="x",
                y="y",
                dw="dw",
                dh="dh",
                image="image",
                source=self.source,
                color_mapper=color_mapper)


class UMViewer(object):
    def __init__(self, loader):
        self.loader = loader
        self.source = bokeh.models.ColumnDataSource({
                "x": [],
                "y": [],
                "dw": [],
                "dh": [],
                "image": []})

    def render(self, variable, ipressure):
        if variable is None:
            return
        self.source.data = self.loader.image(
                variable,
                ipressure)

    def add_figure(self, figure, color_mapper):
        return figure.image(
                x="x",
                y="y",
                dw="dw",
                dh="dh",
                image="image",
                source=self.source,
                color_mapper=color_mapper)


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


class FieldControls(object):
    def __init__(self, viewers, loaders):
        self.viewers = viewers
        self.ipressure = 0
        self.variables = loaders[0].variables
        self.pressures = loaders[0].pressures
        self.pressure_variables = loaders[0].pressure_variables
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
        for viewer in self.viewers:
            viewer.render(self.variable, self.ipressure)


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


def add_feature(figure, feature):
    source = bokeh.models.ColumnDataSource({
        "xs": [],
        "ys": []
    })
    renderer = figure.multi_line(
        xs="xs",
        ys="ys",
        source=source,
        color="white")
    xs, ys = [], []
    for geometry in feature.geometries():
        for g in geometry:
            lons, lats = g.xy
            x, y = geo.web_mercator(lons, lats)
            xs.append(x)
            ys.append(y)
    source.data = {
        "xs": xs,
        "ys": ys
    }
    return renderer


if __name__.startswith("bk"):
    main()
