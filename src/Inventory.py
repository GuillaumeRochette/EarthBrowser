import os
from osgeo import gdal
import numpy as np
import caffe

gdal.UseExceptions()

root_dir = "/home/grochette/Documents/SegNet/data/"
label_dir = os.path.join(root_dir, "CleanData/Labels")

label_names = sorted(os.listdir(label_dir))
print "{} labels.".format(len(label_names))
global_counts = [0, 0, 0]
for label_name in label_names:
    label_path = os.path.join(label_dir, label_name)
    label_ds = gdal.Open(label_path)
    # label_ds = gdal.Open(label_path, gdal.GA_Update)
    print label_path
    band = label_ds.GetRasterBand(1)
    label = band.ReadAsArray()
    values, counts = np.unique(label, return_counts=True)
    for i in range(len(counts)):
        global_counts[i] += counts[i]

print global_counts
global_counts = np.array(global_counts, dtype=np.float32)
frequencies = global_counts[:-1] / np.sum(global_counts[:-1])

print frequencies
L = len(frequencies)
H = np.eye(L) - np.diag(frequencies)
print H
blob = caffe.io.array_to_blobproto(H.reshape((1, 1, L, L)))
with open('infogainH.binaryproto', 'wb') as f:
    f.write(blob.SerializeToString())
