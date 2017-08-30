import os
from osgeo import gdal

gdal.UseExceptions()


def split(src_path, dst_dir, patch_shape, strides, tile_prefix="Tile"):
    ds = gdal.Open(src_path)
    x_size = ds.RasterXSize
    y_size = ds.RasterYSize
    x_patch, y_patch = patch_shape
    x_stride, y_stride = strides
    for j in range(0, y_size, y_stride):
        if j + y_patch > y_size:
            j = y_size - y_patch

        for i in range(0, x_size, x_stride):
            if i + x_patch > x_size:
                i = x_size - x_patch

            tile_name = "{}_{:05d}_{:05d}.tif".format(tile_prefix, i, j)
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
    # cities = ["Rio", "Vegas", "Paris", "Shanghai", "Khartoum"]
    cities = ["Vegas", "Paris", "Shanghai", "Khartoum"]  # Rio doesn't have MUL_PAN (50cm), only MUL (2m).
    for city in cities:
        mul_pan_dir = os.path.join(root_dir, "RawData/{}/MUL_PAN".format(city))
        rgb_pan_dir = os.path.join(root_dir, "RawData/{}/RGB_PAN".format(city))
        label_dir = os.path.join(root_dir, "RawData/{}/Labels".format(city))
        print mul_pan_dir
        print rgb_pan_dir
        print label_dir

        tile_shape = (224, 224)
        strides = (224, 224)

        out_rgb_pan_dir = os.path.join(root_dir, "CleanData/RGB_PAN")
        if not os.path.isdir(out_rgb_pan_dir):
            os.makedirs(out_rgb_pan_dir)
        out_mul_pan_dir = os.path.join(root_dir, "CleanData/MUL_PAN")
        if not os.path.isdir(out_mul_pan_dir):
            os.makedirs(out_mul_pan_dir)
        out_label_dir = os.path.join(root_dir, "CleanData/Labels")
        if not os.path.isdir(out_label_dir):
            os.makedirs(out_label_dir)

        split_SpaceNet(mul_pan_dir, out_mul_pan_dir, tile_shape, strides)
        split_SpaceNet(rgb_pan_dir, out_rgb_pan_dir, tile_shape, strides)
        split_SpaceNet(label_dir, out_label_dir, tile_shape, strides)
        # src_path = "/home/grochette/Images/SanFrancisco/Oakland.tif"
        # dst_dir = "/home/grochette/Images/SanFrancisco/Tiles"
        # if not os.path.isdir(dst_dir):
        #     os.makedirs(dst_dir)
        # patch_shape = (224, 224)
        # strides = (224, 224)
        # tile_prefix = "Oakland"
        # split(src_path, dst_dir, patch_shape, strides, tile_prefix)
