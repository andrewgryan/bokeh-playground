import cartopy
import numpy as np


def web_mercator(lons, lats):
    return transform(
            lons,
            lats,
            cartopy.crs.PlateCarree(),
            cartopy.crs.Mercator.GOOGLE)


def transform(x, y, src_crs, dst_crs):
    x, y = np.asarray(x), np.asarray(y)
    xt, yt, _ = dst_crs.transform_points(src_crs, x.flatten(), y.flatten()).T
    return xt, yt
