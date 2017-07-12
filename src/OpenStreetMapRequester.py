from osgeo import gdal
import glob
import os
import overpass
import json
import numpy as np


def get_coordinates(ds):
    geoinformation = ds.GetGeoTransform()
    cols = ds.RasterXSize
    rows = ds.RasterYSize

    west, xres, xskew, north, yskew, yres = geoinformation

    east = west + cols * xres
    south = north + rows * yres

    return north, east, south, west


def get_geospatial_data(img_path):
    ds = gdal.Open(img_path)
    north, east, south, west = get_coordinates(ds)
    # print north, east, south, west

    api = overpass.API(timeout=600)
    map_query = overpass.MapQuery(south, west, north, east)
    geospatial_data = api.Get(map_query)
    return geospatial_data


if __name__ == '__main__':
    root_dir = "/home/guillaume/Documents/SegNet/data/Oakland_3200x3200"

    tiles_dir = os.path.join(root_dir, "Tiles")
    tile_names = os.listdir(tiles_dir)

    json_dir = os.path.join(root_dir, "GeoJSONs")
    if not os.path.isdir(json_dir):
        os.makedirs(json_dir)

    for index, tile_name in enumerate(sorted(tile_names)):
        print index
        tile_path = os.path.join(tiles_dir, tile_name)
        print tile_path
        geojson_obj = get_geospatial_data(tile_path)

        json_name = tile_name.replace(".tif", ".geojson")
        json_path = os.path.join(json_dir, json_name)
        print json_path

        with open(json_path, "w") as output_file:
            json.dump(geojson_obj, output_file)
