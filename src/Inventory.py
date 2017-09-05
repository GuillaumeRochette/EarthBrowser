import os
import glob
from osgeo import gdal
import numpy as np
import caffe

gdal.UseExceptions()


def compute_distribution(label_paths):
    print "{} labels.".format(len(label_paths))
    occurrences = {}
    for i, label_path in enumerate(label_paths):
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
    return occurrences


if __name__ == '__main__':
    root_dir = "/home/grochette/Documents/SegNet"
    clean_data_dir = os.path.join(root_dir, "data/CleanData")
    cities = ["Vegas", "Paris", "Shanghai", "Khartoum"]
    label_paths = []
    for city in cities:
        label_dir = os.path.join(clean_data_dir, "{}/Labels".format(city))
        label_paths += sorted(glob.glob(os.path.join(label_dir, "*")))

    dist = compute_distribution(label_paths)
    occurences = np.array(dist.values(), dtype=np.float32)
    occurences = occurences[:-1]
    L = len(occurences)
    weights = occurences.sum() / (occurences * L)
    H = np.diag(weights)
    print H
    blob = caffe.io.array_to_blobproto(H.reshape((1, 1, L, L)))
    with open(os.path.join(clean_data_dir, "infogainH.binaryproto"), 'wb') as f:
        f.write(blob.SerializeToString())
