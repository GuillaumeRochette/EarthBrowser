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
        if j + y_patch > y_size:
            j = y_size - y_patch

        for i in range(0, x_size, x_stride):
            if i + x_patch > x_size:
                i = x_size - x_patch

            tile_name = tile_prefix + "_{:03d}_{:03d}.tif".format(i, j)
            tile_path = os.path.join(dst_dir, tile_name)
            print tile_path
            gdal.Translate(tile_path, ds, format='GTiff', srcWin=[i, j, x_patch, y_patch], noData=0,
                           options=['COMPRESS=DEFLATE'])


def split_SpaceNet(src_dir, dst_dir, patch_shape, strides=None):
    src_names = sorted(os.listdir(src_dir))
    for src_name in src_names:
        src_path = os.path.join(src_dir, src_name)
        split(src_path, dst_dir, patch_shape, strides, src_name.replace(".tif", ""))


if __name__ == '__main__':
    root_dir = "/home/grochette/Documents/SegNet/data"
    cities = ["Rio", "Vegas", "Paris", "Shanghai", "Khartoum"]
    for city in cities:
        data_dir = os.path.join(root_dir, "RawData/{}/Data".format(city))
        label_dir = os.path.join(root_dir, "RawData/{}/Labels".format(city))
        print data_dir
        print label_dir

        tile_shape = (224, 224)
        strides = (224, 224)

        output_dir = os.path.join(root_dir, "CleanData")
        out_data_dir = os.path.join(output_dir, "Data")
        if not os.path.isdir(out_data_dir):
            os.makedirs(out_data_dir)
        out_label_dir = os.path.join(output_dir, "Labels")
        if not os.path.isdir(out_label_dir):
            os.makedirs(out_label_dir)
        split_SpaceNet(data_dir, out_data_dir, tile_shape, strides)
        split_SpaceNet(label_dir, out_label_dir, tile_shape, strides)
