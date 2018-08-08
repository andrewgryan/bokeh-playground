import matplotlib.pyplot as plt
import cartopy
import cartopy.io.shapereader as shpreader

def main():
    # Cartopy API
    borders = cartopy.feature.BORDERS
    borders.scale = "10m"
    for geom in borders.geometries():
        for g in geom:
            x, y = g.xy
            plt.plot(x, y, color="black", lw=1)
    plt.savefig("cartopy-border")


def plot_borders_manually():
    path = shpreader.natural_earth(resolution="10m",
                                   category="cultural",
                                   name="admin_0_boundary_lines_land")
    print(path)
    reader = shpreader.Reader(path)
    for geom in reader.geometries():
        for g in geom:
            x, y = g.xy
            plt.plot(x, y, color="black", lw=1)


def plot_south_east_asia_borders():
    chosen_names = [
        "indonesia",
        "malaysia",
        "philippines"
    ]
    colors = {
            "indonesia": "orange",
            "malaysia": "red",
            "philippines": "purple"
    }
    path = shpreader.natural_earth(resolution="10m",
                                   category="cultural",
                                   name="admin_0_countries")
    reader = shpreader.Reader(path)
    countries = reader.records()
    for country in countries:
        name = country.attributes['NAME_EN']
        if name.lower() not in chosen_names:
            continue
        boundary = country.geometry.boundary
        c = colors[name.lower()]
        for g in boundary.geoms:
            x, y = g.xy
            plt.plot(x, y, color=c, lw=1)


if __name__ == '__main__':
    main()
