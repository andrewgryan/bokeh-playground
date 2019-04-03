import bokeh.plotting
import cartopy
import numpy as np
import netCDF4
import scipy.interpolate
import scipy.ndimage
import glob
import os


def main():
    lon_range = (0, 30)
    lat_range = (0, 30)
    x_range, y_range = transform(
        lon_range,
        lat_range,
        cartopy.crs.PlateCarree(),
        cartopy.crs.Mercator.GOOGLE)
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

    pattern = "/Users/andrewryan/cache/highway_*.nc"
    renderers = []
    sources = []
    paths = glob.glob(pattern)
    for path in paths:
        source = bokeh.models.ColumnDataSource({
            "x": [],
            "y": [],
            "dw": [],
            "dh": [],
            "image": []})
        sources.append(source)
        sub_renderers = []
        for figure in figures:
            renderer = figure.image(
                    x="x",
                    y="y",
                    dw="dw",
                    dh="dh",
                    image="image",
                    source=source,
                    color_mapper=color_mapper)
            sub_renderers.append(renderer)
        renderers.append(sub_renderers)
        source.data = load_image(path, "relative_humidity")

    def get_name(path):
        if "ga6" in os.path.basename(path):
            return "GA6"
        elif "takm4p4" in os.path.basename(path):
            return "Tropical Africa 4.4km"
        elif "eakm4p4" in os.path.basename(path):
            return "East Africa 4.4km"

    labels = [get_name(path) for path in paths]
    checkboxes = bokeh.models.CheckboxGroup(
            labels=labels,
            active=[0, 1, 2])

    def on_change(attr, old, new):
        for i in old:
            if i not in new:
                for r in renderers[i]:
                    r.visible = False
        for i in new:
            if i not in old:
                for r in renderers[i]:
                    r.visible = True

    checkboxes.on_change("active", on_change)

    features = []
    for figure in figures:
        features += [
            add_feature(figure, cartopy.feature.BORDERS),
            add_feature(figure, cartopy.feature.COASTLINE)]
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

    variables = load_variables(paths[0])
    variables_drop = bokeh.models.Dropdown(
            label="Variables",
            menu=[(v, v) for v in variables],
            width=50)
    variables_drop.on_click(change_label(variables_drop))

    def on_click(value):
        for path, source in zip(paths, sources):
            source.data = load_image(path, value)

    variables_drop.on_click(on_click)

    palettes = {
            "Viridis": bokeh.palettes.Viridis[256],
            "Magma": bokeh.palettes.Magma[256],
            "Inferno": bokeh.palettes.Inferno[256],
            "Plasma": bokeh.palettes.Plasma[256]
    }
    palettes_drop = bokeh.models.Dropdown(
            label="Palettes",
            menu=[(k, k) for k in palettes.keys()])

    palettes_drop.on_click(change_label(palettes_drop))

    def on_click(value):
        color_mapper.palette = palettes[value]

    palettes_drop.on_click(on_click)

    def on_change(attr, old, new):
        images = [source.data["image"][0]
            for source in sources]
        low = np.min([np.min(x) for x in images])
        high = np.max([np.max(x) for x in images])
        color_mapper.low = low
        color_mapper.high = high

    input_width = 65
    low_input = bokeh.models.TextInput(
            title="Low:",
            width=input_width)
    low_input.on_change(
            "value",
            change(color_mapper, "low", float))
    color_mapper.on_change(
            "low",
            change(low_input, "value", str))
    high_input = bokeh.models.TextInput(
            title="High:",
            width=input_width)
    high_input.on_change(
            "value",
            change(color_mapper, "high", float))
    color_mapper.on_change(
            "high",
            change(high_input, "value", str))

    for source in sources:
        source.on_change("data", on_change)

    # LCR rows
    def on_change(i):
        def wrapper(attr, old, new):
            rs = renderers[i]
            for j in old:
                if j not in new:
                    rs[j].visible = False
            for j in new:
                if j not in old:
                    rs[j].visible = True
        return wrapper

    rows = []
    groups = []
    for i in range(3):
        group = bokeh.models.CheckboxButtonGroup(
                labels=["L", "C", "R"])
        group.on_change("active", on_change(i))
        groups.append(group)
        row = bokeh.layouts.row(group)
        rows.append(row)
    lcr_column = bokeh.layouts.column(*rows)

    def on_click(value):
        if int(value) == 1:
            for g in groups:
                g.labels = ["Select"]
        elif int(value) == 2:
            for g in groups:
                g.labels = ["L", "R"]
        elif int(value) == 3:
            for g in groups:
                g.labels = ["L", "C", "R"]

    figure_drop.on_click(on_click)

    div = bokeh.models.Div(text="", width=10)
    border_row = bokeh.layouts.row(
        bokeh.layouts.column(toggle),
        bokeh.layouts.column(div),
        bokeh.layouts.column(dropdown))

    div = bokeh.models.Div(text="", width=10)
    input_row = bokeh.layouts.row(
        bokeh.layouts.column(low_input),
        bokeh.layouts.column(div),
        bokeh.layouts.column(high_input))

    document = bokeh.plotting.curdoc()
    document.add_root(
        bokeh.layouts.column(
            bokeh.layouts.row(figure_drop),
            border_row,
            bokeh.layouts.row(checkboxes),
            bokeh.layouts.row(lcr_column),
            bokeh.layouts.row(slider),
            bokeh.layouts.row(variables_drop),
            bokeh.layouts.row(palettes_drop),
            input_row,
            name="controls"))
    document.add_root(figure_row)


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


def load_variables(path):
    variables = []
    with netCDF4.Dataset(path) as dataset:
        for v in dataset.variables:
            if "bnds" in v:
                continue
            if v in dataset.dimensions:
                continue
            if len(dataset.variables[v].dimensions) < 2:
                continue
            variables.append(v)
    return variables


def load_image(path, variable):
    print("loading: {} {}".format(path, variable))
    with netCDF4.Dataset(path) as dataset:
        var = dataset.variables[variable]
        for d in var.dimensions:
            if "longitude" in d:
                lons = dataset.variables[d][:]
            if "latitude" in d:
                lats = dataset.variables[d][:]
        if len(var.dimensions) == 4:
            values = var[0, 0, :]
        else:
            values = var[0, :]
    gx, _ = web_mercator(
        lons,
        np.zeros(len(lons), dtype="d"))
    _, gy = web_mercator(
        np.zeros(len(lats), dtype="d"),
        lats)
    image = stretch_y(gy)(values)
    x = gx.min()
    y = gy.min()
    dw = gx[-1] - gx[0]
    dh = gy[-1] - gy[0]
    return {
        "x": [x],
        "y": [y],
        "dw": [dw],
        "dh": [dh],
        "image": [image]
    }


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
            x, y = web_mercator(lons, lats)
            xs.append(x)
            ys.append(y)
    source.data = {
        "xs": xs,
        "ys": ys
    }
    return renderer

def web_mercator(lons, lats):
    return transform(
            lons,
            lats,
            cartopy.crs.PlateCarree(),
            cartopy.crs.Mercator.GOOGLE)


def transform(x, y, src_crs, dst_crs):
    x, y = np.asarray(x), np.asarray(y)
    xt, yt, _ = dst_crs.transform_points(src_crs, x.flatten(), y.flatten()).T
    return xt, yt


def stretch_y(uneven_y):
    """Mercator projection stretches longitude spacing

    To remedy this effect an even-spaced resampling is performed
    in the projected space to make the pixels and grid line up

    .. note:: This approach assumes the grid is evenly spaced
              in longitude/latitude space prior to projection
    """
    if isinstance(uneven_y, list):
        uneven_y = np.asarray(uneven_y, dtype=np.float)
    even_y = np.linspace(
        uneven_y.min(), uneven_y.max(), len(uneven_y),
        dtype=np.float)
    index = np.arange(len(uneven_y), dtype=np.float)
    index_function = scipy.interpolate.interp1d(uneven_y, index)
    index_fractions = index_function(even_y)

    def wrapped(values, axis=0):
        if isinstance(values, list):
            values = np.asarray(values, dtype=np.float)
        assert values.ndim == 2, "Can only stretch 2D arrays"
        msg = "{} != {} do not match".format(values.shape[axis], len(uneven_y))
        assert values.shape[axis] == len(uneven_y), msg
        if axis == 0:
            i = index_fractions
            j = np.arange(values.shape[1], dtype=np.float)
        elif axis == 1:
            i = np.arange(values.shape[0], dtype=np.float)
            j = index_fractions
        else:
            raise Exception("Can only handle axis 0 or 1")
        return scipy.ndimage.map_coordinates(
            values,
            np.meshgrid(i, j, indexing="ij"),
            order=1)
    return wrapped


if __name__.startswith("bk"):
    main()
