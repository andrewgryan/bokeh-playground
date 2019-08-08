import bokeh.models


class Layer(object):
    """Maintains data sources related to a single layer"""
    def __init__(self):
        self.sources = {}

    def get_source(self, file_name):
        return self.select(self.key(file_name))

    @staticmethod
    def key(file_name):
        if file_name.endswith(".json"):
            return "geojson"
        else:
            return "column_data_source"

    def select(self, key):
        if key not in self.sources:
            self.sources[key] =  bokeh.models.ColumnDataSource({
                "x": [],
                "y": [],
            })
        return self.sources[key]
