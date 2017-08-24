import os
from osgeo import gdal
import numpy as np

gdal.UseExceptions()

root_dir = "/home/grochette/Documents/SegNet/data/"
label_dir = os.path.join(root_dir, "CleanData/Labels")

label_names = sorted(os.listdir(label_dir))
all_values = []
for label_name in label_names:
    label_path = os.path.join(label_dir, label_name)
    label_ds = gdal.Open(label_path)
    # label_ds = gdal.Open(label_path, gdal.GA_Update)
    print label_path
    band = label_ds.GetRasterBand(1)
    label = band.ReadAsArray()
    values = np.unique(label)
    for value in values:
        if value not in all_values:
            all_values.append(value)
    # label[label == 255]=2
    # band.WriteArray(label)

print all_values