import matplotlib.pyplot as plt
import cartopy
ax = plt.axes(projection=cartopy.crs.Mercator.GOOGLE)
ax.coastlines()
plt.savefig("google.png")
