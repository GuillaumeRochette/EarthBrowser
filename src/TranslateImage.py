import numpy as np
from osgeo import gdal


def translate_output_bounds(file_path, pix_translation):
    ds = gdal.Open(file_path)
    xpix_translation, ypix_translation = pix_translation

    cols = ds.RasterXSize
    rows = ds.RasterYSize
    ulx, xres, xskew, uly, yskew, yres = ds.GetGeoTransform()

    lrx = ulx + cols * xres
    lry = uly + rows * yres

    print "Old output bounds : {:f} {:f} {:f} {:f}".format(ulx, uly, lrx, lry)

    ulx += xpix_translation * xres
    uly += ypix_translation * yres

    lrx = ulx + cols * xres
    lry = uly + rows * yres

    print "New output bounds : {:f} {:f} {:f} {:f}".format(ulx, uly, lrx, lry)
    output_file = file_path.replace(".tif", ".dec.tif")
    print output_file
    # gdal.Translate(output_file, ds, outputBounds=[ulx, uly, lrx, lry])

if __name__ == '__main__':
    xpix_translation = 29.52
    ypix_translation = 61.06
    print xpix_translation, ypix_translation

    file_path = "/home/guillaume/Documents/SegNet/data/Oakland.tif"
    translate_output_bounds(file_path, [xpix_translation, ypix_translation])
