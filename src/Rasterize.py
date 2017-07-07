import os
from osgeo import gdal, ogr, gdalnumeric
import numpy as np


def outline_rasterization(vector_fp, raster_fp, output_fp):
    no_data_value = 0

    vector_ds = ogr.Open(vector_fp)
    vector_layer = vector_ds.GetLayer()

    raster_ds = gdal.Open(raster_fp)

    geotiff_driver = gdal.GetDriverByName("GTiff")

    output_ds = geotiff_driver.Create(output_fp, raster_ds.RasterXSize, raster_ds.RasterYSize, 1, gdal.GDT_Byte,
                                      options=['COMPRESS=LZW'])
    output_ds.SetGeoTransform(raster_ds.GetGeoTransform())
    output_ds.SetProjection(raster_ds.GetProjection())

    band = output_ds.GetRasterBand(1)
    band.SetNoDataValue(no_data_value)
    gdal.RasterizeLayer(output_ds, [1], vector_layer, options=["ALL_TOUCHED=TRUE"])


def mask_rasterization(vector_fp, raster_fp, output_fp):
    no_data_value = 0

    vector_ds = ogr.Open(vector_fp)
    vector_layer = vector_ds.GetLayer()

    raster_ds = gdal.Open(raster_fp)

    mem_driver = gdal.GetDriverByName("MEM")
    outline_ds = mem_driver.Create("", raster_ds.RasterXSize, raster_ds.RasterYSize, 1, gdal.GDT_Float32)
    outline_ds.SetGeoTransform(raster_ds.GetGeoTransform())
    outline_ds.SetProjection(raster_ds.GetProjection())

    outline_band = outline_ds.GetRasterBand(1)
    outline_band.SetNoDataValue(no_data_value)

    gdal.RasterizeLayer(outline_ds, [1], vector_layer, burn_values=[255], options=["ALL_TOUCHED=TRUE"])

    mem_driver_2 = gdal.GetDriverByName("MEM")
    outside_ds = mem_driver_2.Create("", raster_ds.RasterXSize, raster_ds.RasterYSize, 1, gdal.GDT_Float32)
    outside_ds.SetGeoTransform(raster_ds.GetGeoTransform())
    outside_ds.SetProjection(raster_ds.GetProjection())

    outside_band = outside_ds.GetRasterBand(1)
    outside_band.SetNoDataValue(no_data_value)

    gdal.ComputeProximity(outline_band, outside_band, options=["NODATA=0"])

    mem_driver_3 = gdal.GetDriverByName("MEM")
    inside_ds = mem_driver_3.Create("", raster_ds.RasterXSize, raster_ds.RasterYSize, 1, gdal.GDT_Float32)
    inside_ds.SetGeoTransform(raster_ds.GetGeoTransform())
    inside_ds.SetProjection(raster_ds.GetProjection())

    inside_band = inside_ds.GetRasterBand(1)
    inside_band.SetNoDataValue(no_data_value)

    gdal.ComputeProximity(outline_band, inside_band, options=["NODATA=0", "VALUES=0"])

    geotiff_driver = gdal.GetDriverByName("GTiff")
    output_ds = geotiff_driver.Create(output_fp, raster_ds.RasterXSize, raster_ds.RasterYSize, 1, gdal.GDT_Float32,
                                      options=['COMPRESS=LZW'])
    output_ds.SetGeoTransform(raster_ds.GetGeoTransform())
    output_ds.SetProjection(raster_ds.GetProjection())

    # proximity = gdalnumeric.BandReadAsArray(inside_band)**p - gdalnumeric.BandReadAsArray(outside_band)**p
    proximity = gdalnumeric.BandReadAsArray(inside_band) - gdalnumeric.BandReadAsArray(outside_band)
    proximity_band = output_ds.GetRasterBand(1).WriteArray(proximity)


if __name__ == '__main__':
    root_dir = "/home/guillaume/Documents/SegNet/data/Oakland_224x224"

    vectors_dir = os.path.join(root_dir, "GeoJSONVectors")
    vector_fp = os.path.join(vectors_dir, "Tile_16128_18144.geojson")

    raster_dir = os.path.join(root_dir, "InputTiles")
    raster_fp = os.path.join(raster_dir, "Tile_16128_18144.tif")

    # output_dir = os.path.join(root_dir, "OutlineTiles")
    # output_fp = os.path.join(output_dir, "Outline_16128_18144.tif")
    # outline_rasterization(vector_fp, raster_fp, output_fp)

    output_dir = os.path.join(root_dir, "MaskTiles")
    output_fp = os.path.join(output_dir, "Mask_16128_18144.tif")

    mask_rasterization(vector_fp, raster_fp, output_fp)
