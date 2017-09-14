import os
from osgeo import gdal


def translate_output_bounds(src_path, dst_path, pix_translation):
    """Create a translated copy of the input image along the x, y axes (pixel unit) to a specified location.
    It was used to realign Pleiades images with OpenStreetMap data.
    It uses gdal.Translate() in a similar way as gdal_translate binary.

    :param src_path: Path of the source image.
    :param dst_path: Path for the output.
    :param pix_translation: Couple of int or float, containing the translation vector.
    :return:
    """
    src_ds = gdal.Open(src_path)
    xpix_translation, ypix_translation = pix_translation

    cols = src_ds.RasterXSize
    rows = src_ds.RasterYSize
    ulx, xres, xskew, uly, yskew, yres = src_ds.GetGeoTransform()

    lrx = ulx + cols * xres
    lry = uly + rows * yres

    print "Old output bounds : {:f} {:f} {:f} {:f}".format(ulx, uly, lrx, lry)

    new_ulx = ulx + xpix_translation * xres
    new_uly = uly + ypix_translation * yres

    new_lrx = new_ulx + cols * xres
    new_lry = new_uly + rows * yres

    print "New output bounds : {:f} {:f} {:f} {:f}".format(new_ulx, new_uly, new_lrx, new_lry)
    print dst_path
    gdal.Translate(dst_path, src_ds, outputBounds=[new_ulx, new_uly, new_lrx, new_lry])


if __name__ == '__main__':
    xpix_translation = 29.52
    ypix_translation = 61.06
    print xpix_translation, ypix_translation

    root_dir = "/home/guillaume/Documents/SegNet/data"
    src_names = ["Oakland.tif", "Fremont.tif", "Concord.tif"]
    src_paths = [os.path.join(root_dir, src_name) for src_name in src_names]
    dst_paths = [src_path.replace(".tif", ".dec.tif") for src_path in src_paths]
    for src_path, dst_path in zip(src_paths, dst_paths):
        print src_path, dst_path
        translate_output_bounds(src_path, dst_path, [xpix_translation, ypix_translation])
