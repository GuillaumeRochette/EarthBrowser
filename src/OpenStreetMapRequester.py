from osgeo import gdal
import overpass
import json
# import gzip
import numpy as np


def get_corner_coordinates(ds):
    geoinformation = ds.GetGeoTransform()
    cols = ds.RasterXSize
    rows = ds.RasterYSize

    west, xres, xskew, north, yskew, yres = geoinformation
    xres = 0.5
    yres = -0.5

    east = west + cols * xres
    south = north + rows * yres

    return north, east, south, west


def get_geojson_map(img_path):
    ds = gdal.Open(img_path)
    north, east, south, west = get_corner_coordinates(ds)

    api = overpass.API(timeout=600)
    map_query = overpass.MapQuery(south, west, north, east)
    response = api.Get(map_query)
    return response


if __name__ == '__main__':
    root_dir = "../data/"
    img_path = root_dir + "Tiles/Tile_10528_3584.tif"
    geojson_obj = get_geojson_map(img_path)

    with open(root_dir + "Tile_10528_3584.geojson", "w") as output_file:
        json.dump(geojson_obj, output_file)
