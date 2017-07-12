from osgeo import gdal
import numpy as np
import matplotlib.pyplot as plt

s1 = gdal.Open("/home/guillaume/Documents/SegNet/data/Oakland_224x224/Tiles/Tile_09984_09088.tif")
s2 = gdal.Open("/home/guillaume/Documents/SegNet/data/Oakland_224x224/Outlines/Outline_09984_09088.tif")
s3 = gdal.Open("/home/guillaume/Documents/SegNet/data/Oakland_224x224/Heatmaps/Heatmap_09984_09088.tif")
print gdal.Info(s1)

img_1 = np.array(s1.ReadAsArray())
img_2 = np.array(s2.ReadAsArray())
img_3 = np.array(s3.ReadAsArray())

img_1 = np.transpose(img_1, axes=[1, 2, 0])

# channels = [0, 1, 2]

img_1 = img_1[..., :-1][..., ::-1]
img_1 = img_1.astype(np.float32) / 4095.

print img_1.shape
print img_2.shape
print img_3.shape

plt.figure()
plt.subplot(1, 3, 1)
plt.imshow(img_1)
plt.subplot(1, 3, 2)
plt.imshow(img_2)
plt.subplot(1, 3, 3)
plt.imshow(img_3)
plt.show()
