from collections import OrderedDict
import data


def on_server_loaded(server_context):
    patterns = OrderedDict({
        "GA6": "/Users/andrewryan/cache/highway_ga6*.nc",
        "Tropical Africa 4.4km": "/Users/andrewryan/cache/highway_takm4p4*.nc",
        "East Africa 4.4km": "/Users/andrewryan/cache/highway_eakm4p4*.nc",
        "RDT": "/Users/andrewryan/cache/*.json",
        "EarthNetworks": "/Users/andrewryan/buckets/highway-external-collab/2019/20190407/englnrt_20190407*",
        "GPM IMERG early": "/Users/andrewryan/buckets/stephen-sea-public-london/gpm_imerg/gpm_imerg_NRTearly_V05B_20190406_highway_only.nc",
        "GPM IMERG late": "/Users/andrewryan/buckets/stephen-sea-public-london/gpm_imerg/gpm_imerg_NRTlate_V05B_20190406_highway_only.nc",
    })
    data.on_server_loaded(patterns)
