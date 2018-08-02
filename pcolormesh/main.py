import bokeh.plotting
import numpy as np
import matplotlib.pyplot as plt

x = np.array([1, 3, 4])
y = np.array([1, 3, 4])
x, y = np.meshgrid(x, y)
z = x**2 + y**2
ni, nj = z.shape
mappable = plt.pcolormesh(x, y, z)
plt.savefig("plot")
rgba = mappable.to_rgba(mappable.get_array(),
                        bytes=True).reshape(ni - 1, nj - 1, 4)
figure = bokeh.plotting.figure()
figure.image_rgba(x=1, y=1, dw=3, dh=3, image=[rgba])
bokeh.plotting.show(figure)
