from osgeo import gdal
import numpy as np
import matplotlib.pyplot as plt


# source = gdal.Open("/home/guillaume/Documents/SegNet/data/Oakland_224x224/OutlineTiles/Outline_16128_18144.tif")
source = gdal.Open("/home/guillaume/Documents/SegNet/data/Oakland_224x224/MaskTiles/Mask_16128_18144.tif")
print gdal.Info(source)

mask = np.array(source.ReadAsArray())

print mask.shape
print mask.dtype
print mask.max()
print mask.min()
plt.figure()
plt.imshow(mask)
plt.show()