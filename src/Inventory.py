import argparse
import glob
import numpy as np
import os
from osgeo import gdal

import caffe

gdal.UseExceptions()


def compute_distribution(label_paths):
    """
    Compute the distribution of the labels contained in the dataset.
    :param label_paths: Array of label_path.
    :return: Dict(label_value, count)
    """
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
    parser = argparse.ArgumentParser(
        description="Compute the occurences of the various classes in the dataset, then generate the infogain matrix H, which should be used (in Caffe) when class are very imbalanced.")
    parser.add_argument("--input_dir", required=True,
                        help="Directory containing the city directories, themselves containing the labels.")
    parser.add_argument("--output_dir", required=True, help="Output directory for the infogain matrix file.")
    args = parser.parse_args()

    input_dir = args.input_dir
    output_dir = args.output_dir
    cities = os.listdir(input_dir)
    # Lists labels.
    label_paths = []
    for city in cities:
        city_dir = os.path.join(input_dir, city)
        label_dir = os.path.join(city_dir, "Labels")
        label_paths += sorted(glob.glob(os.path.join(label_dir, "*")))

    dist = compute_distribution(label_paths)
    print dist
    occurences = np.array(dist.values(), dtype=np.float32)
    # Ignores the labels corresponding to the edge of the rasterized polygons,
    # which will be ignored during training.
    occurences = occurences[:-1]
    L = len(occurences)
    # Computes the weights according to the inverse frequency.
    weights = occurences.sum() / (occurences * L)
    # Creates the (diagonal) matrix containing the weights.
    H = np.diag(weights)
    print H
    # Blob it then store it as a binaryproto for Caffe ingestion.
    blob = caffe.io.array_to_blobproto(H.reshape((1, 1, L, L)))
    with open(os.path.join(output_dir, "infogainH.binaryproto"), 'wb') as f:
        f.write(blob.SerializeToString())
