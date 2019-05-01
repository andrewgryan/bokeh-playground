"""Server data shared amongst documents"""
import datetime as dt
import re
import os
import glob
import netCDF4


FILE_DB = {}
PATHS = {}
RUN_TIMES = {}
VALID_TIMES = {}
MODEL_NAMES = []
VARIABLES = {}


def load():
    global PATHS
    global MODEL_NAMES
    global FILE_DB
    global VARIABLES
    global RUN_TIMES
    global VALID_TIMES

    offline = False
    if offline:
        model_dir = os.path.expanduser("~/cache")
        patterns = [
            ("GA6", "highway_ga6*"),
            ("TAkm4p4", "highway_takm4p4*"),
            ("OS42", "*os42*")]
    else:
        model_dir = os.path.expanduser("~/buckets/stephen-sea-public-london/model_data")
        patterns = [("GA6", "highway_ga6*")]

    for name, pattern in patterns:
        MODEL_NAMES.append(name)
        full_pattern = os.path.join(model_dir, pattern)
        print("listing: {}".format(full_pattern))
        paths = glob.glob(full_pattern)
        FILE_DB[name] = paths
        for path in paths:
            run_time = parse_time(path)
            key = (name, run_time)
            PATHS[key] = path

        RUN_TIMES[name] = [
            parse_time(path) for path in paths]

    for name, paths in FILE_DB.items():
        with netCDF4.Dataset(paths[-1]) as dataset:
            variables = [name for name in dataset.variables]
        VARIABLES[name] = variables

    print("ready")


def valid_times(path):
    if path in VALID_TIMES:
        print("already seen: {}".format(path))
    else:
        print("loading: {}".format(path))
        with netCDF4.Dataset(path) as dataset:
            var = dataset.variables["time"]
            times = netCDF4.num2date(
                    var[:],
                    units=var.units)
        VALID_TIMES[path] = times
    return VALID_TIMES[path]


def parse_time(path):
    name = os.path.basename(path)
    groups = re.search(r"[0-9]{8}T[0-9]{4}Z", path)
    if groups:
        return dt.datetime.strptime(groups[0], "%Y%m%dT%H%MZ")
