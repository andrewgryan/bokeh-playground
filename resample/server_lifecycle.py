from collections import OrderedDict
import os
import data


def on_server_loaded(server_context):
    directory = "/Users/andrewryan/buckets/stephen-sea-public-london"
    patterns = OrderedDict({
        "GA6": os.path.join(directory, "model_data/highway_ga6*.nc"),
        "Tropical Africa 4.4km": os.path.join(directory, "model_data/highway_takm4p4*.nc"),
        "East Africa 4.4km": os.path.join(directory, "model_data/highway_eakm4p4*.nc"),
        "RDT": "/Users/andrewryan/cache/*.json",
        "EarthNetworks": "/Users/andrewryan/buckets/highway-external-collab/2019/20190407/englnrt_20190407*",
        "GPM IMERG early": os.path.join(directory, "gpm_imerg/gpm_imerg_NRTearly_V05B_*_highway_only.nc"),
        "GPM IMERG late": os.path.join(directory, "gpm_imerg/gpm_imerg_NRTlate_V05B_*_highway_only.nc"),
    })
    data.on_server_loaded(patterns)
