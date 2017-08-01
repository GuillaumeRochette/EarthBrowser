import os
from osgeo import gdal
import numpy as np
import matplotlib.pyplot as plt

data_dir = "/home/guillaume/Documents/SegNet/data/Data_224x224/Data"
i = 555
s1 = gdal.Open("/home/guillaume/Documents/SegNet/data/RawData/Rio/Data/3band_AOI_1_RIO_img8.tif")
s2 = gdal.Open("/home/guillaume/Documents/SegNet/data/RawData/Rio/Labels/3band_AOI_1_RIO_img8segcls.tif")
print gdal.Info(s1)

img_1 = np.array(s1.ReadAsArray())
img_1 = np.transpose(img_1, axes=[1, 2, 0])

img_2 = np.array(s2.ReadAsArray())

print img_1.shape
print img_1.dtype

print img_2.shape
print img_2.dtype

plt.figure()
plt.subplot(1, 2, 1)
plt.imshow(img_1)
plt.subplot(1, 2, 2)
plt.imshow(img_2)
plt.show()
