import os
from osgeo import gdal, ogr, gdalnumeric
import numpy as np
import spaceNetUtilities.labelTools

gdal.UseExceptions()


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


# def PASCALVOC2012_rasterization():
#     srcRaster = gdal.Open(rasterImageName)
#     outputRaster = rasterImageName
#     if segment:
#         NoData_value = -9999
#
#         source_ds = ogr.Open(geoJson)
#         source_layer = source_ds.GetLayer()
#         srs = source_layer.GetSpatialRef()
#         memDriver = ogr.GetDriverByName('MEMORY')
#         outerBuffer=memDriver.CreateDataSource('outer')
#         outerBufferLayer = outerBuffer.CreateLayer("test", srs, geom_type=ogr.wkbPolygon)
#         innerBuffer = memDriver.CreateDataSource('inner')
#         innerBufferLayer = innerBuffer.CreateLayer("test2", srs, geom_type=ogr.wkbPolygon)
#
#         idField = ogr.FieldDefn("objid", ogr.OFTInteger)
#         innerBufferLayer.CreateField(idField)
#
#         featureDefn = innerBufferLayer.GetLayerDefn()
#         bufferDist = srcRaster.GetGeoTransform()[1]*bufferSizePix
#         for idx, feature in enumerate(source_layer):
#             ingeom = feature.GetGeometryRef()
#             geomBufferOut = ingeom.Buffer(bufferDist)
#             geomBufferIn  = ingeom.Buffer(-bufferDist)
#             print(geomBufferIn.ExportToWkt())
#             print(geomBufferIn.IsEmpty())
#             print(geomBufferIn.IsSimple())
#
#             if geomBufferIn.GetArea()>0.0:
#                 outBufFeature = ogr.Feature(featureDefn)
#                 outBufFeature.SetGeometry(geomBufferOut)
#
#                 outerBufferLayer.CreateFeature(outBufFeature)
#
#                 inBufFeature = ogr.Feature(featureDefn)
#                 inBufFeature.SetGeometry(geomBufferIn)
#                 inBufFeature.SetField('objid', idx)
#                 innerBufferLayer.CreateFeature(inBufFeature)
#
#                 outBufFeature = None
#                 inBufFeature = None
#
#
#
#         print('writing GTIFF sgcls')
#         print('rasterToWrite = {}'.format(xmlFileName.replace('.xml', 'segcls.tif')))
#         target_ds = gdal.GetDriverByName('GTiff').Create(xmlFileName.replace('.xml', 'segcls.tif'), srcRaster.RasterXSize, srcRaster.RasterYSize, 1, gdal.GDT_Byte)
#         print('setTransform')
#         target_ds.SetGeoTransform(srcRaster.GetGeoTransform())
#         print('setProjection')
#         target_ds.SetProjection(srcRaster.GetProjection())
#         print('getBand')
#         band = target_ds.GetRasterBand(1)
#         print('setnodata')
#         band.SetNoDataValue(NoData_value)
#
#         # Rasterize
#         print('rasterize outer buffer')
#         gdal.RasterizeLayer(target_ds, [1], outerBufferLayer, burn_values=[255])
#         print('rasterize inner buffer')
#         gdal.RasterizeLayer(target_ds, [1], innerBufferLayer, burn_values=[1])


def heatmap_rasterization(vector_fp, raster_fp, output_fp):
    no_data_value = 0

    vector_ds = ogr.Open(vector_fp)
    vector_layer = vector_ds.GetLayer()

    raster_ds = gdal.Open(raster_fp)

    mem_driver = gdal.GetDriverByName("MEM")
    outline_ds = mem_driver.Create("", raster_ds.RasterXSize, raster_ds.RasterYSize, 1, gdal.GDT_Int16)
    outline_ds.SetGeoTransform(raster_ds.GetGeoTransform())
    outline_ds.SetProjection(raster_ds.GetProjection())

    outline_band = outline_ds.GetRasterBand(1)
    outline_band.SetNoDataValue(no_data_value)

    gdal.RasterizeLayer(outline_ds, [1], vector_layer, burn_values=[255], options=["ALL_TOUCHED=TRUE"])

    mem_driver_2 = gdal.GetDriverByName("MEM")
    outside_ds = mem_driver_2.Create("", raster_ds.RasterXSize, raster_ds.RasterYSize, 1, gdal.GDT_Int16)
    outside_ds.SetGeoTransform(raster_ds.GetGeoTransform())
    outside_ds.SetProjection(raster_ds.GetProjection())

    outside_band = outside_ds.GetRasterBand(1)
    outside_band.SetNoDataValue(no_data_value)

    gdal.ComputeProximity(outline_band, outside_band, options=["NODATA=0"])

    mem_driver_3 = gdal.GetDriverByName("MEM")
    inside_ds = mem_driver_3.Create("", raster_ds.RasterXSize, raster_ds.RasterYSize, 1, gdal.GDT_Int16)
    inside_ds.SetGeoTransform(raster_ds.GetGeoTransform())
    inside_ds.SetProjection(raster_ds.GetProjection())

    inside_band = inside_ds.GetRasterBand(1)
    inside_band.SetNoDataValue(no_data_value)

    gdal.ComputeProximity(outline_band, inside_band, options=["NODATA=0", "VALUES=0"])

    geotiff_driver = gdal.GetDriverByName("GTiff")
    output_ds = geotiff_driver.Create(output_fp, raster_ds.RasterXSize, raster_ds.RasterYSize, 1, gdal.GDT_Int16,
                                      options=['COMPRESS=LZW'])
    output_ds.SetGeoTransform(raster_ds.GetGeoTransform())
    output_ds.SetProjection(raster_ds.GetProjection())

    # proximity = gdalnumeric.BandReadAsArray(inside_band)**p - gdalnumeric.BandReadAsArray(outside_band)**p
    proximity = gdalnumeric.BandReadAsArray(inside_band) - gdalnumeric.BandReadAsArray(outside_band)
    proximity_band = output_ds.GetRasterBand(1).WriteArray(proximity)


if __name__ == '__main__':
    root_dir = "/home/guillaume/Documents/SegNet/data/Oakland_224x224"
    raster_dir = os.path.join(root_dir, "Tiles")
    heatmap_dir = os.path.join(root_dir, "Heatmaps")
    if not os.path.isdir(heatmap_dir):
        os.makedirs(heatmap_dir)

    vectors_dir = "/home/guillaume/Documents/SegNet/data/Oakland_2240x2240/GeoJSONs"

    raster_filenames = os.listdir(raster_dir)
    for raster_filename in sorted(raster_filenames):
        raster_fp = os.path.join(raster_dir, raster_filename)
        print raster_fp
        i, j = [int(e) for e in raster_filename.replace("Tile_", "").replace(".tif", "").split("_")]
        i -= i % 2240
        j -= j % 2240
        vector_filename = "Tile_{:05d}_{:05d}.geojson".format(i, j)
        vector_fp = os.path.join(vectors_dir, vector_filename)
        print vector_fp

        heatmap_filename = raster_filename.replace("Tile", "Heatmap")
        heatmap_fp = os.path.join(heatmap_dir, heatmap_filename)
        print heatmap_fp
        heatmap_rasterization(vector_fp, raster_fp, heatmap_fp)
