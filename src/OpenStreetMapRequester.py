from osgeo import gdal
import os
import overpass
import json
import numpy as np


def get_corner_coordinates(ds):
    geoinformation = ds.GetGeoTransform()
    cols = ds.RasterXSize
    rows = ds.RasterYSize

    west, xres, xskew, north, yskew, yres = geoinformation

    east = west + cols * xres
    south = north + rows * yres

    return north, east, south, west


def get_geojson_obj(img_path):
    ds = gdal.Open(img_path)
    north, east, south, west = get_corner_coordinates(ds)
    print north, east, south, west

    api = overpass.API(timeout=600)
    map_query = overpass.MapQuery(south, west, north, east)
    response = api.Get(map_query)
    return response


if __name__ == '__main__':
    root_dir = "/home/guillaume/Documents/SegNet/data"
    img_name = "Oakland_224x224/InputTiles/Tile_16128_18144.tif"
    img_path = os.path.join(root_dir, img_name)
    print img_path

    geojson_obj = get_geojson_obj(img_path)
    json_name = "Oakland_224x224/GeoJSONVectors/Tile_16128_18144.geojson"
    json_path = os.path.join(root_dir, json_name)
    print json_path

    with open(json_path, "w") as output_file:
        json.dump(geojson_obj, output_file)
