import json
import logging
import numpy as np
import os
import shapely.geometry as sg
import sys
import argparse

import rasterio
import rasterio.features as rf

logging.basicConfig(stream=sys.stderr, level=logging.INFO)
logger = logging.getLogger('rasterize_geometry')


def count_geometries(geojson_paths):
    """
    Compute the distribution of the geometries contained in the GeoJSONs.
    :param geojson_paths: Array containing the GeoJSON paths.
    :return: Dict(geometry_type, count)
    """
    types = {}
    for geojson_path in geojson_paths:
        with open(geojson_path, "r") as geojson_file:
            geojson = json.load(geojson_file)
        for feature in geojson["features"]:
            type = sg.shape(feature["geometry"]).type
            if type not in types:
                types[type] = 1
            else:
                types[type] += 1
    return types


def open_linestring_to_polygon(open_linestring, mean_res):
    """
    Buffers a linestring to 10 times the mean_resolution of the image.
    :param open_linestring: LineString object.
    :param mean_res: Mean resolution of the raster.
    :return: Polygon object.
    """
    polygon = open_linestring.buffer(10 * mean_res)
    return polygon


def closed_linestring_to_polygon(closed_linestring):
    """
    Creates the Polygon of the given LineString.
    :param closed_linestring: LineString object.
    :return: Polygon object.
    """
    polygon = sg.Polygon(closed_linestring)
    return polygon


def process_with_contour(polygon, mean_res):
    """
    Creates the contour of a Polygon.
    :param polygon: Polygon object.
    :param mean_res: Mean resolution of the raster.
    :return: Tuple containing the inner Polygon and its contour (also a Polygon).
    """
    inner_polygon = polygon.buffer(-5 * mean_res)
    contour = polygon.difference(inner_polygon)
    return inner_polygon, contour


def rasterize(data, features):
    """
    Creates a raster of the given features contained within the bounds of the given data.
    :param data: Rasterio raster.
    :param features: Array of GeoJSON features.
    :return: Rasterized features contained within the data bounds.
    """
    x_res = data.affine.a
    y_res = data.affine.e
    # Compute the mean pixel resolution, in case they differ.
    mean_res = (np.abs(x_res) + np.abs(y_res)) / 2.0

    # Can intervert road and building value, doesn't matter.
    road_value = 1
    building_value = 2
    # Contour has usually the highest index.
    contour_value = 3

    geometries_and_values = []

    for feature in features:
        geometry = sg.shape(feature["geometry"])
        if geometry.type == "LineString":
            # If the LineString isn't closed, it's probably a road.
            if not geometry.is_closed:
                road = open_linestring_to_polygon(geometry, mean_res)
                inner_polygon, contour = process_with_contour(road, mean_res)
                if inner_polygon.area != 0:
                    geometries_and_values.append([inner_polygon, road_value])
                if contour.area != 0:
                    geometries_and_values.append([contour, contour_value])
            # If not, I don't know what that is.
            else:
                pass
                # building = closed_linestring_to_polygon(geometry)
                # inner_polygon, contour = process_with_contour(building, mean_res)
                # if inner_polygon.area != 0:
                #     geometries_and_values.append([inner_polygon, building_value])
                # if contour.area != 0:
                #     geometries_and_values.append([contour, contour_value])
        elif geometry.type in ["Polygon", "MultiPolygon"]:
            # Polygons should be buildings.
            inner_polygon, contour = process_with_contour(geometry, mean_res)
            if inner_polygon.area != 0:
                geometries_and_values.append([inner_polygon, building_value])
            if contour.area != 0:
                geometries_and_values.append([contour, contour_value])
    # Rasterize if there are any geometries.
    if geometries_and_values:
        label = rf.rasterize(geometries_and_values, out_shape=data.shape, transform=data.affine, all_touched=True,
                             dtype=rasterio.uint8)
    # Or return an array of zeroes.
    else:
        label = np.zeros(data.shape, dtype=np.uint8)
    return label


def aggregate_features(sp_path, osm_path):
    """
    Aggregate SpaceNet GeoJSON and OpenStreetMap GeoJSON data.
    :param sp_path: SpaceNet GeoJSON path.
    :param osm_path: OpenStreetMap GeoJSON path.
    :return: GeoJSON features.
    """
    features = []
    with open(sp_path, "r") as sp_file:
        geojson = json.load(sp_file)
    features += geojson["features"]
    with open(osm_path, "r") as osm_file:
        geojson = json.load(osm_file)
    features += geojson["features"]
    return features


def burn_raster(label_path, label, data):
    """
    Burn the label raster to a file, given the data properties.
    :param label_path: Label raster path.
    :param label: Label raster.
    :param data: Data raster
    :return:
    """
    with rasterio.open(label_path, mode="w", driver="GTiff", width=data.width, height=data.height, count=1,
                       crs=data.crs, transform=data.affine, dtype=rasterio.uint8, nodata=0,
                       compress="DEFLATE") as label_file:
        label_file.write(label, indexes=1)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Rasterize GeoJSON Files in order to create labels for the images.")
    parser.add_argument("--input_dir", required=True,
                        help="Directory containing the city directories, themselves containing data and labels.")
    args = parser.parse_args()

    input_dir = args.input_dir
    cities = os.listdir(input_dir)
    for city in cities:
        city_dir = os.path.join(input_dir, city)

        mul_pan_dir = os.path.join(city_dir, "MUL_PAN")
        osm_dir = os.path.join(city_dir, "OpenStreetMap_Labels")
        sp_dir = os.path.join(city_dir, "SpaceNet_Labels")

        label_dir = os.path.join(city_dir, "Labels")
        if not os.path.isdir(label_dir):
            os.makedirs(label_dir)

        data_names = sorted(os.listdir(mul_pan_dir))
        sp_names = sorted(os.listdir(sp_dir))
        osm_names = sorted(os.listdir(osm_dir))

        for data_name, sp_name, osm_name in zip(data_names, sp_names, osm_names):
            print data_name, sp_name, osm_name
            data_path = os.path.join(mul_pan_dir, data_name)
            sp_path = os.path.join(sp_dir, sp_name)
            osm_path = os.path.join(osm_dir, osm_name)

            data = rasterio.open(data_path)
            features = aggregate_features(sp_path, osm_path)
            label = rasterize(data, features)
            label_name = data_name
            label_path = os.path.join(label_dir, label_name)
            burn_raster(label_path, label, data)
