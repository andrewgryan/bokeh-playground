import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import cartopy
import bokeh.plotting

figure = bokeh.plotting.figure(sizing_mode='scale_width')

# Coastlines
for geometry in cartopy.feature.COASTLINE.geometries():
    figure.line(*geometry[0].xy,
                color='black',
                level='overlay')

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
                  x=nj + 1,
                  y=0,
                  dh=ni,
                  dw=nj)

bokeh.plotting.show(figure)
