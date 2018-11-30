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


def stretch_transform(y, axis=1, dtype=np.float):
    """Generate latitude/y stretching transform"""
    index = np.arange(len(y), dtype=dtype)
    index_map = scipy.interpolate.interp1d(y, index)
    mapped_index = index_map(equal_spaced(y))

    def transform(values):
        if isinstance(values, list):
            values = np.asarray(values)
        assert values.ndim == 2, 'Only able to stretch 2D arrays'
        if axis == 1:
            i = np.arange(values.shape[0], dtype=dtype)
            j = mapped_index
        else:
            i = mapped_index
            j = np.arange(values.shape[1], dtype=dtype)
        return scipy.ndimage.map_coordinates(values,
                                             np.meshgrid(i, j, indexing='ij'),
                                             order=1)

    return transform


def equal_spaced(v):
    return np.linspace(v.min(), v.max(), len(v), dtype=np.float)
