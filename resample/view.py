import bokeh.models


class UMView(object):
    def __init__(self, loader, color_mapper):
        self.loader = loader
        self.color_mapper = color_mapper
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

    def add_figure(self, figure):
        return figure.image(
                x="x",
                y="y",
                dw="dw",
                dh="dh",
                image="image",
                source=self.source,
                color_mapper=self.color_mapper)


class GPMView(object):
    def __init__(self, loader, color_mapper):
        self.loader = loader
        self.color_mapper = color_mapper
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

    def add_figure(self, figure):
        return figure.image(
                x="x",
                y="y",
                dw="dw",
                dh="dh",
                image="image",
                source=self.source,
                color_mapper=self.color_mapper)
