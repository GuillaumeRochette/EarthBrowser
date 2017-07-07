import os
from osgeo import gdal, ogr
import numpy as np


def outline_rasterization(vector_fp, raster_fp, output_fp):
    no_data_value = 0

    vector_ds = ogr.Open(vector_fp)
    vector_layer = vector_ds.GetLayer()

    raster_ds = gdal.Open(raster_fp)

    geotiff_driver = gdal.GetDriverByName("GTiff")
    output_ds = geotiff_driver.Create(output_fp, raster_ds.RasterXSize, raster_ds.RasterYSize, 1, gdal.GDT_Byte)
    output_ds.SetGeoTransform(raster_ds.GetGeoTransform())
    output_ds.SetProjection(raster_ds.GetProjection())
    gdal.RasterizeLayer(output_ds, [1], vector_layer, options=["ALL_TOUCHED=TRUE"])

if __name__ == '__main__':
    root_dir = "/home/guillaume/Documents/SegNet/data/Oakland_224x224"

    vectors_dir = os.path.join(root_dir, "GeoJSONVectors")
    vector_fp = os.path.join(vectors_dir, "Tile_16128_18144.geojson")

    raster_dir = os.path.join(root_dir, "InputTiles")
    raster_fp = os.path.join(raster_dir, "Tile_16128_18144.tif")

    output_dir = os.path.join(root_dir, "OutlineTiles")
    output_fp = os.path.join(output_dir, "Outline_16128_18144.tif")

    outline_rasterization(vector_fp, raster_fp, output_fp)
