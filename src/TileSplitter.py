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
            tile_name = tile_prefix + "_{:03d}_{:03d}.tif".format(i, j)
            tile_path = os.path.join(dst_dir, tile_name)
            print tile_path
            gdal.Translate(tile_path, ds, format='GTiff', srcWin=[i, j, x_patch, y_patch], noData=0,
                           options=['COMPRESS=LZW'])


def split_SpaceNet(src_dir, dst_dir, patch_shape, strides=None, tile_prefix="Tile"):
    src_names = sorted(os.listdir(src_dir))
    for i, src_name in enumerate(src_names):
        src_path = os.path.join(src_dir, src_name)
        current_tile_prefix = tile_prefix + "_{:05d}".format(i)
        split(src_path, dst_dir, patch_shape, strides, current_tile_prefix)


if __name__ == '__main__':
    root_dir = "/home/guillaume/Documents/SegNet/data"
    cities = ["Rio", "Paris"]
    for city in cities:
        data_dir = os.path.join(root_dir, "RawData/{}/Data".format(city))
        label_dir = os.path.join(root_dir, "RawData/{}/Labels".format(city))
        print data_dir
        print label_dir

        tile_shape = (224, 224)
        strides = (224, 224)

        output_dir = os.path.join(root_dir, "Data_{:d}x{:d}").format(tile_shape[0], tile_shape[1])
        out_data_dir = os.path.join(output_dir, "Data")
        if not os.path.isdir(out_data_dir):
            os.makedirs(out_data_dir)
        out_label_dir = os.path.join(output_dir, "Labels")
        if not os.path.isdir(out_label_dir):
            os.makedirs(out_label_dir)
        split_SpaceNet(data_dir, out_data_dir, tile_shape, strides, "RGB_PAN_{}".format(city))
        split_SpaceNet(label_dir, out_label_dir, tile_shape, strides, "CLASS_SEG_{}".format(city))
