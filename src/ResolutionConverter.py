from osgeo import gdal
import os
import glob
import matplotlib.pyplot as plt

root_dir = "/home/guillaume/Documents/SegNet/data"
tiles_dir = os.path.join(root_dir, "Tiles_1024x1024")
print tiles_dir
tile_pattern = os.path.join(tiles_dir, "*.tif")
print tile_pattern
tile_paths = glob.glob(tile_pattern)
# tile_paths.sort()
print tile_paths

for tile_path in tile_paths:
    print tile_path
    ds = gdal.Open(tile_path)
    img = ds.ReadAsArray()
    transform = ds.GetGeoTransform()
    print (transform[3], transform[0])
    plt.figure(figsize=(8, 8))
    plt.imshow(img)
    plt.show()
