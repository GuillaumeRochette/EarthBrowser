import os
from osgeo import gdal


def split(img_path, tiles_dir, tile_shape, tile_prefix="Tile"):
    ds = gdal.Open(img_path)
    x_size = ds.RasterXSize
    y_size = ds.RasterYSize
    x_step, y_step = tile_shape
    for j in range(0, y_size, y_step):
        for i in range(0, x_size, x_step):
            tile_name = tile_prefix + "_" + str(i) + "_" + str(j) + ".tif"
            tile_path = os.path.join(tiles_dir, tile_name)
            print tile_path
            gdal.Translate(tile_path, ds, format='GTiff', srcWin=[i, j, x_step, y_step], noData=0)


if __name__ == '__main__':
    root_dir = "../data/"
    img_name = "Oakland.tif"

    img_path = os.path.join(root_dir, img_name)

    tiles_dir = os.path.join(root_dir, "Tiles/")
    if not os.path.isdir(tiles_dir):
        os.mkdir(tiles_dir)
    split(img_path, tiles_dir, (224, 224))
