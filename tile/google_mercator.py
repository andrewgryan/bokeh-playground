import numpy as np
import matplotlib.pyplot as plt
import cartopy
x = np.array([-80, 80, 80, -80, -80])
y = np.array([-70, -70, 70, 70, -70])
ax = plt.axes(projection=cartopy.crs.Mercator.GOOGLE)
ax.coastlines()
ax.plot(x, y, transform=cartopy.crs.PlateCarree())
plt.savefig("google.png")
