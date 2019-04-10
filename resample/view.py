import bokeh.models


class UMView(object):
    def __init__(self, loader):
        self.loader = loader
        self.source = bokeh.models.ColumnDataSource({
                "x": [],
                "y": [],
                "dw": [],
                "dh": [],
                "image": []})

    def render(self, variable, ipressure, itime):
        if variable is None:
            return
        self.source.data = self.loader.image(
                variable,
                ipressure,
                itime)

    def add_figure(self, figure, color_mapper):
        return figure.image(
                x="x",
                y="y",
                dw="dw",
                dh="dh",
                image="image",
                source=self.source,
                color_mapper=color_mapper)


class GPMView(object):
    def __init__(self, loader):
        self.loader = loader
        self.empty = {
                "x": [],
                "y": [],
                "dw": [],
                "dh": [],
                "image": []}
        self.source = bokeh.models.ColumnDataSource(self.empty)

    def render(self, variable, ipressure, itime):
        if variable != "precipitation_flux":
            self.source.data = self.empty
        else:
            self.source.data = self.loader.image(itime)

    def add_figure(self, figure, color_mapper):
        return figure.image(
                x="x",
                y="y",
                dw="dw",
                dh="dh",
                image="image",
                source=self.source,
                color_mapper=color_mapper)
