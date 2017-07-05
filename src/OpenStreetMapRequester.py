from osgeo import gdal
import os
import overpass
import json
# import gzip
import numpy as np


def get_corner_coordinates(ds):
    geoinformation = ds.GetGeoTransform()
    cols = ds.RasterXSize
    rows = ds.RasterYSize

    west, xres, xskew, north, yskew, yres = geoinformation

    east = west + cols * xres
    south = north + rows * yres

    return north, east, south, west


def get_geojson_map(img_path):
    ds = gdal.Open(img_path)
    north, east, south, west = get_corner_coordinates(ds)

    api = overpass.API(timeout=600)
    map_query = overpass.MapQuery(south, west, north, east)
    print map_query
    response = api.Get(map_query)
    return response


if __name__ == '__main__':
    root_dir = "/home/guillaume/Documents/SegNet/data"
    img_path = os.path.join(root_dir, "Tiles_1024x1024/Tile_9216_15360.tif")
    print img_path
    geojson_obj = get_geojson_map(img_path)
    json_path = os.path.join(root_dir, "Tile_9216_15360.geojson")
    print json_path
    with open(json_path, "w") as output_file:
        json.dump(geojson_obj, output_file)
