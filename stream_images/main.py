import bokeh.plotting
import numpy as np


def main():
    """main program"""
    app = Application()
    document = bokeh.plotting.curdoc()
    for root in app.roots:
        document.add_root(root)


class Application:
    def __init__(self):
        self.figure = bokeh.plotting.figure()
        self.figure.x_range = bokeh.models.Range1d(0, 1)
        self.sources = {}
        self.sources["still"] = bokeh.models.ColumnDataSource({
            "x": [],
            "y": [],
            "dw": [],
            "dh": [],
            "image": [],
        })
        self.sources["stream"] = bokeh.models.ColumnDataSource({
            "x": [],
            "y": [],
            "dw": [],
            "dh": [],
            "image": [],
        })
        self.renderers = {}
        for key, source in self.sources.items():
            self.renderers[key] = self.figure.image(x="x",
                                                    y="y",
                                                    dw="dw",
                                                    dh="dh",
                                                    image="image",
                                                    source=source)

        button = bokeh.models.Button()
        button.on_click(ImageStream(self.sources["stream"]))
        button.on_click(self.show_stream)

        self.layout = bokeh.layouts.column(
            button,
            self.figure
        )

        self.buttons = {}
        self.buttons["random"] = bokeh.models.Button(label="Random")
        self.buttons["random"].on_click(self.random)

        self.roots = [
            self.layout,
            bokeh.layouts.row(self.buttons["random"])
        ]

    def random(self):
        image = np.random.randn(100).reshape(10, 10)
        self.sources["still"].data = {
            "x": [0],
            "y": [0],
            "dw": [1],
            "dh": [1],
            "image": [image],
        }
        self.show_random()

    def show_random(self):
        self.renderers["stream"].visible = False
        self.renderers["still"].visible = True
        self.figure.x_range.start = 0
        self.figure.x_range.end = 1

    def show_stream(self):
        self.renderers["stream"].visible = True
        self.renderers["still"].visible = False
        data = self.sources["stream"].data
        n = len(data["image"])
        if n > 0:
            start = min(data["x"][i] for i in range(n))
            end = max(data["x"][i] + data["dw"][i] for i in range(n))
        else:
            start = 0
            end = 1
        self.figure.x_range.start = start
        self.figure.x_range.end = end


class ImageStream:
    def __init__(self, source):
        self.source = source
        self.i = 0

    def __call__(self, event):
        nx = (self.i + 1) * 10
        ny = (self.i + 1) * 10
        image = np.random.randn(nx * ny).reshape(nx, ny)
        data = {
            "x": [self.i],
            "y": [0],
            "dw": [1],
            "dh": [1],
            "image": [image],
        }
        self.source.stream(data, rollover=3)
        self.i += 1


if __name__.startswith("bokeh"):
    main()
