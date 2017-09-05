import os
from osgeo import gdal
import numpy as np
import caffe

gdal.UseExceptions()


def infogain_matrix(frequencies):
    L = len(frequencies)
    H = np.eye(L) - np.diag(frequencies)
    return H


def get_frequencies(label_dir):
    label_names = sorted(os.listdir(label_dir))
    print "{} labels.".format(len(label_names))
    occurrences = {}
    for i, label_name in enumerate(label_names):
        label_path = os.path.join(label_dir, label_name)
        print i, label_path
        label_ds = gdal.Open(label_path)
        band = label_ds.GetRasterBand(1)
        label = band.ReadAsArray()
        values, counts = np.unique(label, return_counts=True)
        for value, count in zip(values, counts):
            if value not in occurrences:
                occurrences[value] = count
            else:
                occurrences[value] += count
    print occurrences


root_dir = "/home/grochette/Documents/SegNet/data/"
label_dir = os.path.join(root_dir, "CleanData/Labels")
get_frequencies(label_dir)

# print frequencies
# H = infogain_matrix(frequencies)
# print H
# blob = caffe.io.array_to_blobproto(H.reshape((1, 1, L, L)))
# with open('infogainH.binaryproto', 'wb') as f:
#     f.write(blob.SerializeToString())
