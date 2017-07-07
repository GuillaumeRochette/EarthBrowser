import os
import numpy as np
from osgeo import gdal
from spaceNetUtilities import labelTools
import matplotlib.pyplot as plt

root_dir = "/home/guillaume/Documents/SegNet/data"
raster_src = os.path.join(root_dir, "Oakland_224x224/InputTiles/Tile_16128_18144.tif")
vector_src = os.path.join(root_dir, "Oakland.geojson")
# vector_src = os.path.join(root_dir, "Oakland_224x224/GeoJSONVectors/Tile_16128_18144.geojson")

# labelTools.createRasterFromGeoJson(root_dir + "Oakland.geojson", root_dir + "Oakland.tif", root_dir + "OaklandMap.tif")
distance_map = labelTools.createDistanceTransform(rasterSrc=raster_src, vectorSrc=vector_src)
img = gdal.Open(raster_src).ReadAsArray()
img = np.array(img, dtype=np.float32)
img = np.transpose(img, axes=(1, 2, 0))

print img.shape
print distance_map.shape
max_pixel = np.max(img, (0, 1))
print max_pixel
min_pixel = np.min(img, (0, 1))
print min_pixel
img = (img - min_pixel) / (max_pixel - min_pixel)
img = img[..., :-1][..., ::-1]

plt.figure()
plt.subplot(1, 2, 1)
plt.imshow(img)
plt.subplot(1, 2, 2)
plt.imshow(distance_map)
plt.show()
