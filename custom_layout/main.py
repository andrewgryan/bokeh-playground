import bokeh.plotting
from bokeh.core.properties import String, Instance
from bokeh.models import Slider, LayoutDOM


class Custom(LayoutDOM):
    __implementation__ = "custom.ts"
    text = String()
    slider = Instance(Slider)


class Application(object):
    def __init__(self):
        self.roots = []
        button = bokeh.models.Button()
        figure = bokeh.plotting.figure()
        source = bokeh.models.ColumnDataSource({
            "x": [1, 2, 3],
            "y": [1, 2, 3],
            "size": [2, 2, 2]
            })
        renderer = figure.circle(
                x="x",
                y="y",
                size="size",
                source=source)
        slider = bokeh.models.Slider(
                start=0,
                end=10,
                step=0.1,
                value=2,
                show_value=False,
                tooltips=False)
        custom_js = bokeh.models.CustomJS(
            args=dict(source=source),
            code="""
            source.data["size"] = source.data["size"]
                .map(x => Math.pow(cb_obj.value, 2))
            source.change.emit()
            """)
        slider.js_on_change("value", custom_js)
        custom = Custom(
                text="Label",
                slider=slider)
        column = bokeh.layouts.column(
                bokeh.layouts.row(
                    button),
                bokeh.layouts.row(
                    slider,
                    custom),
                bokeh.layouts.row(
                    figure))
        self.roots.append(column)


def main():
    app = Application()
    document = bokeh.plotting.curdoc()
    for root in app.roots:
        document.add_root(root)


if __name__.startswith("bk"):
    main()
