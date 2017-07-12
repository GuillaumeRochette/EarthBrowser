import os
from osgeo import gdal

gdal.UseExceptions()


def split(src_path, dst_dir, patch_shape, strides=None, tile_prefix="Tile"):
    ds = gdal.Open(src_path)
    x_size = ds.RasterXSize
    y_size = ds.RasterYSize
    x_patch, y_patch = patch_shape
    if strides is None:
        x_stride, y_stride = patch_shape
    else:
        x_stride, y_stride = strides
    for j in range(0, y_size, y_stride):
        for i in range(0, x_size, x_stride):
            tile_name = tile_prefix + "_{:05d}_{:05d}.tif".format(i, j)
            tile_path = os.path.join(dst_dir, tile_name)
            print tile_path
            gdal.Translate(tile_path, ds, format='GTiff', srcWin=[i, j, x_patch, y_patch], noData=0)


if __name__ == '__main__':
    root_dir = "/home/guillaume/Documents/SegNet/data"
    img_names = ["Oakland.dec.tif"]
    # img_names = ["Oakland.dec.tif", "Fremont.dec.tif", "Concord.dec.tif"]

    tile_shape = (3200, 3200)
    # strides = (64, 64)

    for img_name in img_names:
        img_path = os.path.join(root_dir, img_name)
        dir_name = img_name.replace(".dec.tif", "") + "_{:d}x{:d}/Tiles".format(tile_shape[0], tile_shape[1])
        dst_dir = os.path.join(root_dir, dir_name)

        print dst_dir
        if not os.path.isdir(dst_dir):
            os.makedirs(dst_dir)
        # split(img_path, dst_dir, tile_shape, strides)
        split(img_path, dst_dir, tile_shape)
