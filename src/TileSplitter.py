import os
from osgeo import gdal

gdal.UseExceptions()


def split(img_path, tiles_dir, tile_shape, tile_name="Tile"):
    ds = gdal.Open(img_path)
    x_size = ds.RasterXSize
    y_size = ds.RasterYSize
    x_step, y_step = tile_shape
    for j in range(0, y_size, y_step):
        for i in range(0, x_size, x_step):
            tile_name = tile_name + "_" + str(i) + "_" + str(j) + ".tif"
            tile_path = os.path.join(tiles_dir, tile_name)
            print tile_path
            gdal.Translate(tile_path, ds, format='GTiff', srcWin=[i, j, x_step, y_step], noData=0)


if __name__ == '__main__':
    root_dir = "/home/guillaume/Documents/SegNet/data"
    img_name = "Oakland.dec.tif"
    img_path = os.path.join(root_dir, img_name)

    tile_shape = (224, 224)

    dir_name = "Oakland_{:d}x{:d}/InputTiles".format(tile_shape[0], tile_shape[1])
    tiles_dir = os.path.join(root_dir, dir_name)
    print tiles_dir
    if not os.path.isdir(tiles_dir):
        os.makedirs(tiles_dir)
    split(img_path, tiles_dir, tile_shape)
