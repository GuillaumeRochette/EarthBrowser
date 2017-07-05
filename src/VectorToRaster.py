from osgeo import gdal
from spaceNetUtilities import labelTools
import matplotlib.pyplot as plt

root_dir = "../data/"

# labelTools.createRasterFromGeoJson(root_dir + "Oakland.geojson", root_dir + "Oakland.tif", root_dir + "OaklandMap.tif")
distance_map = labelTools.createDistanceTransform(root_dir + "Tiles_224x224/Tile_22176_10080.tif",
                                                  root_dir + "Tile_22176_10080.geojson",
                                                  root_dir + "OaklandDistanceMap.npy")
img = gdal.Open(root_dir + "Tiles_224x224/Tile_22176_10080.tif").ReadAsArray()
print distance_map.shape
plt.figure()
plt.subplot(1, 2, 1)
plt.imshow(img)
plt.subplot(1, 2, 2)
plt.imshow(distance_map)
plt.show()
