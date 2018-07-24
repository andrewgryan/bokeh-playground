import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import cartopy
import bokeh.plotting

figure = bokeh.plotting.figure(sizing_mode='stretch_both',
                               match_aspect=True)


# Struggling to find appropriate extent for cartopy feature
# Left, right, bottom, top
x0, x1, y0, y1 = (0, 21, 0, 11)
extent = x0, x1, y0, y1


def coastlines(figure, scale="110m", extent=None):
    """Add cartopy coastline to a figure

    Translates cartopy.feature.COASTLINE object
    into collection of bokeh lines

    .. note:: This method assumes the map projection
              is cartopy.crs.PlateCarreee

    :param figure: bokeh figure instance
    :param scale: cartopy coastline scale '110m', '50m' or '10m'
    :param extent: x_start, x_end, y_start, y_end
    """
    coastline = cartopy.feature.COASTLINE
    coastline.scale = scale
    for geometry in coastline.intersecting_geometries(extent):
        figure.line(*geometry[0].xy,
                    color='black',
                    level='overlay')

coastlines(figure,
           scale="10m",
           extent=extent)

# Custom normalisation
norm = mpl.colors.Normalize(vmin=0,
                            vmax=200)

# Imshow
ni, nj = 10, 10
values = np.arange(ni * nj).reshape(ni, nj)
mappable = plt.imshow(values, norm=norm)
rgba = mappable.to_rgba(mappable.get_array(),
                        bytes=True).reshape(ni, nj, 4)
figure.image_rgba(image=[rgba],
                  x=0,
                  y=0,
                  dh=ni,
                  dw=nj)

# Imshow
ni, nj = 10, 10
values = np.arange(ni * nj).reshape(ni, nj)
values += 100
mappable = plt.imshow(values, norm=norm)
rgba = mappable.to_rgba(mappable.get_array(),
                        bytes=True).reshape(ni, nj, 4)
figure.image_rgba(image=[rgba],
                  x=nj - 1,
                  y=1,
                  dh=ni,
                  dw=nj)

# Set bokeh x/y range extents
figure.x_range.start = x0
figure.x_range.end = x1
figure.y_range.start = y0
figure.y_range.end = y1

bokeh.plotting.show(figure)
