import json
import os
import time
from osgeo import gdal
import argparse
import overpass


def get_coordinates(src_ds):
    """
    Get the coordinates of the Geospatial data.
    :param src_ds: Data source.
    :return: Tuple containing the coordinates of the area.
    """
    geoinformation = src_ds.GetGeoTransform()
    cols = src_ds.RasterXSize
    rows = src_ds.RasterYSize

    west, xres, xskew, north, yskew, yres = geoinformation

    east = west + cols * xres
    south = north + rows * yres

    return north, east, south, west


def get_geojson(data_path):
    """
    Requests the OpenStreetMap Extended API for a GeoJSON-like object about the specified data.
    :param data_path: Path of the geospatial data.
    :return: GeoJSON object of features contained in the data bounds.
    """
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
    """
    Requests GeoJSONs for all data contained in the directory.
    :param data_dir: Path to the data directory.
    :param geojson_dir: Path to the output GeoJSON directory.
    :param file_extension: File extension of the data.
    :return:
    """
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
    parser = argparse.ArgumentParser(
        description="Requests the Extended OpenStreetMap API to retrieve vector data related to our raster data.")
    parser.add_argument("-i", "--input_dir", required=True,
                        help="Directory containing the city directories, themselves containing the raster data.")
    args = parser.parse_args()
    input_dir = args.input_dir
    # Requests data for every city contained in the directory.
    cities = os.listdir(input_dir)
    for city in cities:
        city_dir = os.path.join(input_dir, city)
        data_dir = os.path.join(city_dir, "MUL_PAN")
        geojson_dir = os.path.join(city_dir, "OpenStreetMap_Labels")
        if not os.path.isdir(geojson_dir):
            os.makedirs(geojson_dir)
        request_data(data_dir, geojson_dir)
