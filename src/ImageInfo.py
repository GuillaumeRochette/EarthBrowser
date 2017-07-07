from osgeo import gdal
import numpy as np
import matplotlib.pyplot as plt


source = gdal.Open("/home/guillaume/Documents/SegNet/data/Oakland_224x224/InputTiles/Tile_8512_8512.tif")
print gdal.Info(source)

img = source.ReadAsArray()
img = np.array(img)

print img.shape
print img.dtype

img = img.transpose([2, 1, 0])

print img.shape

img_vis = img[..., :-1]

print img_vis.shape

plt.figure()
plt.imshow(img_vis)
plt.show()
