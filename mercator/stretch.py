import cartopy
import scipy.interpolate
import scipy.ndimage
import numpy as np


def web_mercator_y(latitudes):
    """Find y values in Mercator Web projection related to latitudes"""
    longitudes = np.zeros(len(latitudes), dtype=np.float)
    gl = cartopy.crs.Mercator.GOOGLE
    pc = cartopy.crs.PlateCarree()
    _, y, _ = gl.transform_points(pc, longitudes, latitudes).T
    return y


def resample_transform(y):
    """Generate latitude/y stretching transform"""
    index = np.arange(len(y), dtype=np.float)
    index_map = scipy.interpolate.interp1d(y, index)
    j = index_map(equal_spaced(y))

    def transform(values):
        if isinstance(values, list):
            values = np.asarray(values)
        assert values.ndim == 2, 'Only able to stretch 2D arrays'
        i = np.arange(values.shape[0], dtype=np.float)
        return scipy.ndimage.map_coordinates(values,
                                             np.meshgrid(i, j, indexing='ij'))

    return transform


def equal_spaced(v):
    return np.linspace(v.min(), v.max(), len(v), dtype=np.float)
