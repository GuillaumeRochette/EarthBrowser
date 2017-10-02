import glob
import numpy as np
import os
from osgeo import gdal
import argparse

import matplotlib.pyplot as plt

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Use it to display data and labels side by side.")
    parser.add_argument("--input_dir", required=True,
                        help="Directory containing the city directories, themselves containing data and labels.")
    parser.add_argument("--channels", nargs="+", type=int,
                        help="Channels to keep for multispectral images, WV3 -> PHR = [1,2,4,6].")
    args = parser.parse_args()
    input_dir = args.input_dir
    channels = args.channels

    cities = os.listdir(input_dir)
    mul_pan_paths = []
    label_paths = []
    for city in cities:
        city_dir = os.path.join(input_dir, city)
        mul_pan_dir = os.path.join(city_dir, "MUL_PAN")
        label_dir = os.path.join(city_dir, "Labels")
        mul_pan_paths += glob.glob(os.path.join(mul_pan_dir, "*"))
        label_paths += glob.glob(os.path.join(label_dir, "*"))

    mul_pan_paths = sorted(mul_pan_paths)
    label_paths = sorted(label_paths)
    print "There are currently {} listed data and labels.".format(len(mul_pan_paths))
    while True:
        i = int(input())
        mul_pan_path = mul_pan_paths[i]
        label_path = label_paths[i]
        print mul_pan_path
        print label_path

        mul_pan = np.array(gdal.Open(mul_pan_path).ReadAsArray())
        label = np.array(gdal.Open(label_path).ReadAsArray())

        print mul_pan.shape, mul_pan.dtype
        print label.shape, label.dtype
        # Select the channels that were chosen for training.
        if channels:
            mul_pan = mul_pan[channels, ...]
        img = np.transpose(mul_pan[::-1, ...], axes=[1, 2, 0])

        min_pixel = np.min(img, axis=(0, 1))
        max_pixel = np.max(img, axis=(0, 1))
        img = np.array(img, dtype=np.float32)
        img = (img - min_pixel) / (max_pixel - min_pixel)
        img *= 2 ** 8
        img = np.array(img, dtype=np.uint8)

        # Plot.
        plt.figure()
        plt.subplot(1, 2, 1)
        plt.imshow(img)
        plt.subplot(1, 2, 2)
        plt.imshow(label)
        plt.show()
