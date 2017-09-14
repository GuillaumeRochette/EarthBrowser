import numpy as np
import os
from osgeo import gdal

import matplotlib.pyplot as plt

data_dir = "/home/guillaume/Documents/SegNet/data/CleanData"
i = 555
s1 = gdal.Open(os.path.join(data_dir, "Data/RGB_PAN_Rio_06917_000_183.tif"))
s2 = gdal.Open(os.path.join(data_dir, "Labels/CLASS_SEG_Rio_06917_000_183.tif"))
print gdal.Info(s1)
print gdal.Info(s2)

datum = np.array(s1.ReadAsArray())
label = np.array(s2.ReadAsArray())

print datum.shape
print datum.dtype

print label.shape
print label.dtype

d_u, d_counts = np.unique(datum, return_counts=True)
l_u, l_counts = np.unique(label, return_counts=True)
print d_u, d_counts
print l_u, l_counts

datum = np.transpose(datum, axes=[1, 2, 0])
plt.figure()
plt.subplot(1, 2, 1)
plt.imshow(datum)
plt.subplot(1, 2, 2)
plt.imshow(label)
plt.show()
