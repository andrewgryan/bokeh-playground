"""

Demonstration of combining client-side animation with streamed
column data sources

"""
import bokeh.plotting
import numpy as np


class Animation:
    def __init__(self, figure, dataset):
        self._i = 0  # To be replaced by auto-stream/animate functionality
        self.dataset = dataset
        self.sources = {}
        self.sources['mode'] = bokeh.models.ColumnDataSource({
            "playing": [False]
        })
        self.sources['index'] = bokeh.models.ColumnDataSource({
            "i": [0],
        })
        custom_js_filter = bokeh.models.CustomJSFilter(args=dict(index_source=self.sources['index']), code="""
            let indices = new Array(source.get_length()).fill(true);
            return indices.map((x, i) => i == index_source.data['i'][0])
        """)
        self.sources['image'] = bokeh.models.ColumnDataSource({
            "x": [],
            "y": [],
            "dw": [],
            "dh": [],
            "image": [],
        })
        view = bokeh.models.CDSView(source=self.sources['image'], filters=[custom_js_filter])
        figure.image(
                x="x",
                y="y",
                dw="dw",
                dh="dh",
                image="image",
                source=self.sources['image'],
                view=view)
        buttons = {
            "play": bokeh.models.Button(label="Play"),
            "pause": bokeh.models.Button(label="Pause")
        }

        # Animation recursive JS
        custom_js = bokeh.models.CustomJS(args=dict(
            image_source=self.sources['image'],
            index_source=self.sources['index'],
            mode_source=self.sources['mode']), code="""
                let next_frame = function() {
                    if (mode_source.data['playing'][0]) {
                        let index = index_source.data['i'][0];
                        index_source.data['i'] = [(index + 1) % image_source.get_length()]
                        image_source.change.emit() // Trigger CustomJSFilter
                        setTimeout(next_frame, 100)
                    }
                }
                if (mode_source.data['playing'][0]) {
                    setTimeout(next_frame, 100)
                }
        """)
        self.sources["mode"].js_on_change("data", custom_js)

        # Play button
        custom_js = bokeh.models.CustomJS(args=dict(mode_source=self.sources['mode']), code="""
            mode_source.data['playing'] = [true];
            mode_source.change.emit();
        """)
        buttons["play"].js_on_click(custom_js)
        buttons["play"].on_click(self.play)

        # Pause button
        custom_js = bokeh.models.CustomJS(args=dict(mode_source=self.sources['mode']), code="""
            mode_source.data['playing'] = [false];
            mode_source.change.emit();
        """)
        buttons["pause"].js_on_click(custom_js)

        self.layout = bokeh.layouts.row(
                buttons["play"],
                buttons["pause"])

    def play(self):
        # Load frame(s) if needed
        if self._i < 20:
            for i in range(10):
                self.add_frame()

        # Trigger client-side animation
        self.sources['mode'].data['playing'] = [True]

    def add_frame(self):
        print(f"Add frame: {self._i}")
        self.sources['image'].stream(self.dataset.load_image(self._i))
        self._i += 1


class Dataset:
    """Fake entity to simulate I/O"""
    def __init__(self):
        self.X, self.Y = np.meshgrid(
                np.linspace(0, 2, 256),
                np.linspace(0, 2, 256))

    def load_image(self, index):
        """Simulates retrieving next image from server"""
        image = self.particle((self.X - 0.1 * index), self.Y)
        return {
            "x": [0],
            "y": [0],
            "dw": [2],
            "dh": [2],
            "image": [image]
        }

    @staticmethod
    def particle(X, Y):
        return np.exp(-1 * (X**2 + Y**2))


def main():
    figure = bokeh.plotting.figure()
    dataset = Dataset()
    animation = Animation(figure, dataset)
    document = bokeh.plotting.curdoc()
    document.add_root(
        bokeh.layouts.column(
            animation.layout,
            figure))


if __name__.startswith('bk'):
    main()
