import os
from osgeo import gdal
import numpy as np
import matplotlib.pyplot as plt

data_dir = "/home/guillaume/Documents/SegNet/data/Data_224x224/Data"
i = 555
s1 = gdal.Open("/home/guillaume/Documents/SegNet/data/Data_224x224/Data/Paris_RGB_PAN_00000_112_448.tif")
print gdal.Info(s1)

img_1 = np.array(s1.ReadAsArray())
img_2 = img_1[..., ::-1, ::-1]
img_1 = np.transpose(img_1, axes=[1, 2, 0])
img_2 = np.transpose(img_2, axes=[1, 2, 0])

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
