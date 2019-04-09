import glob
import json
import pandas as pd
import numpy as np
import netCDF4
import scipy.interpolate
import scipy.ndimage
import geo
from collections import OrderedDict


FILE_DB = None
LOADERS = {}
IMAGES = OrderedDict()


def on_server_loaded(patterns):
    global FILE_DB
    FILE_DB = FileDB(patterns)
    FILE_DB.sync()
    for name, paths in FILE_DB.files.items():
        if name == "RDT":
            LOADERS[name] = RDT(paths)
        elif "GPM" in name:
            LOADERS[name] = GPM(paths)
        elif name == "EarthNetworks":
            LOADERS[name] = EarthNetworks(paths)
        else:
            LOADERS[name] = UMLoader(paths)

    # Example of server-side pre-caching
    for name in [
            "Tropical Africa 4.4km"]:
        path = FILE_DB.files[name][0]
        load_image(path, "relative_humidity", 0)


class FileDB(object):
    def __init__(self, patterns):
        self.patterns = patterns
        self.names = list(patterns.keys())
        self.files = {}

    def sync(self):
        for key, pattern in self.patterns.items():
            self.files[key] = glob.glob(pattern)


class EarthNetworks(object):
    def __init__(self, paths):
        self.paths = paths
        self.frame = self.read(paths)

    @staticmethod
    def read(csv_files):
        if isinstance(csv_files, str):
            csv_files = [csv_files]
        frames = []
        for csv_file in csv_files:
            frame = pd.read_csv(
                csv_file,
                parse_dates=[1],
                converters={0: EarthNetworks.flash_type},
                usecols=[0, 1, 2, 3],
                names=["flash_type", "date", "longitude", "latitude"],
                header=None)
            frames.append(frame)
        if len(frames) == 0:
            return None
        else:
            return pd.concat(frames, ignore_index=True)


    @staticmethod
    def flash_type(value):
        return {
            "0": "CG",
            "1": "IC",
            "9": "Keep alive"
        }.get(value, value)


class RDT(object):
    def __init__(self, paths):
        self.paths = paths
        self.geojson = self.load(self.paths[0])

    @staticmethod
    def load(path):
        print("loading: {}".format(path))
        with open(path) as stream:
            rdt = json.load(stream)

        copy = dict(rdt)
        for i, feature in enumerate(rdt["features"]):
            coordinates = feature['geometry']['coordinates'][0]
            lons, lats = np.asarray(coordinates).T
            x, y = geo.web_mercator(lons, lats)
            c = np.array([x, y]).T.tolist()
            copy["features"][i]['geometry']['coordinates'][0] = c

        # Hack to use Categorical mapper
        for i, feature in enumerate(rdt["features"]):
            p = feature['properties']['PhaseLife']
            copy["features"][i]['properties']['PhaseLife'] = str(p)

        return json.dumps(copy)


class GPM(object):
    def __init__(self, paths):
        self.paths = paths

    def image(self):
        return load_image(
                self.paths[0],
                "precipitation_flux",
                0)


class UMLoader(object):
    def __init__(self, paths):
        self.paths = paths
        self.variables = load_variables(self.paths[0])
        self.pressure_variables, self.pressures = self.load_heights(self.paths[0])

    @staticmethod
    def load_heights(path):
        variables = set()
        with netCDF4.Dataset(path) as dataset:
            pressures = dataset.variables["pressure"][:]
            for variable, var in dataset.variables.items():
                if variable == "pressure":
                    continue
                if "pressure" in var.dimensions:
                    variables.add(variable)
        return variables, pressures

    def image(self, variable, ipressure):
        return load_image(
                self.paths[0],
                variable,
                ipressure)


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


def load_image(path, variable, ipressure=None):
    key = (path, variable, ipressure)
    if key in IMAGES:
        print("already seen: {}".format(key))
        return IMAGES[key]
    else:
        print("loading: {}".format(key))
        with netCDF4.Dataset(path) as dataset:
            try:
                var = dataset.variables[variable]
            except KeyError as e:
                if variable == "precipitation_flux":
                    var = dataset.variables["stratiform_rainfall_rate"]
                else:
                    raise e
            for d in var.dimensions:
                if "longitude" in d:
                    lons = dataset.variables[d][:]
                if "latitude" in d:
                    lats = dataset.variables[d][:]
            if len(var.dimensions) == 4:
                values = var[0, ipressure, :]
            else:
                values = var[0, :]
        image = stretch_image(lons, lats, values)
        IMAGES[key] = image
        return image


def stretch_image(lons, lats, values):
    gx, _ = geo.web_mercator(
        lons,
        np.zeros(len(lons), dtype="d"))
    _, gy = geo.web_mercator(
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
