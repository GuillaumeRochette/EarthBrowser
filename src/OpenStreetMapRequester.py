import json
import os
import time
from osgeo import gdal

import overpass


def get_coordinates(src_ds):
    geoinformation = src_ds.GetGeoTransform()
    cols = src_ds.RasterXSize
    rows = src_ds.RasterYSize

    west, xres, xskew, north, yskew, yres = geoinformation

    east = west + cols * xres
    south = north + rows * yres

    return north, east, south, west


def get_geojson(data_path):
    src_ds = gdal.Open(data_path)
    north, east, south, west = get_coordinates(src_ds)
    collected = False
    api = overpass.API(timeout=300)
    map_query = overpass.MapQuery(south, west, north, east)
    while not collected:
        try:
            geojson = api.Get(map_query)
            collected = True
        except Exception as e:
            print "Error !"
            collected = False
            time.sleep(1)
    return geojson


def request_data(data_dir, geojson_dir, file_extension="tif"):
    data_names = sorted(os.listdir(data_dir))
    for i, data_name in enumerate(data_names):
        data_path = os.path.join(data_dir, data_name)
        geojson_name = data_name.replace(file_extension, "geojson")
        geojson_path = os.path.join(geojson_dir, geojson_name)
        print i, data_path, geojson_path

        geojson = get_geojson(data_path)

        with open(geojson_path, "w") as geojson_file:
            json.dump(geojson, geojson_file)


if __name__ == '__main__':
    root_dir = "/home/guillaume/Documents/SegNet/"
    raw_data_dir = os.path.join(root_dir, "data/RawData")
    cities = ["Vegas", "Paris", "Shanghai", "Khartoum"]

    for city in cities:
        city_dir = os.path.join(raw_data_dir, "{}".format(city))
        data_dir = os.path.join(city_dir, "MUL_PAN")
        geojson_dir = os.path.join(city_dir, "OpenStreetMap_Labels")
        if not os.path.isdir(geojson_dir):
            os.makedirs(geojson_dir)
        request_data(data_dir, geojson_dir)
