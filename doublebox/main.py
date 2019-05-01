#!/usr/bin/env python
import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl


def main():
    facecolor = "SteelBlue"
    values = np.random.randn(100)
    tenth = np.percentile(values, 10)
    ninetieth = np.percentile(values, 90)
    print(tenth, ninetieth)
    width = 0.05
    height = ninetieth - tenth
    x = 1 - (width / 2)
    y = tenth
    patch = mpl.patches.Rectangle((x, y), width, height, edgecolor='black', facecolor=facecolor)
    ax = plt.gca()
    ax.add_patch(patch)
    boxes = plt.boxplot(values, patch_artist=True)
    for box in boxes['boxes']:
        box.set(facecolor=facecolor)
    # plt.show()
    plt.savefig("double-box")

if __name__ == '__main__':
    main()
