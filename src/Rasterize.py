import json
import logging
import numpy as np
import os
import shapely.geometry as sg
import sys

import rasterio
import rasterio.features as rf

logging.basicConfig(stream=sys.stderr, level=logging.INFO)
logger = logging.getLogger('rasterize_geometry')


def count_geometries(geojson_paths):
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
    polygon = open_linestring.buffer(10 * mean_res)
    return polygon


def closed_linestring_to_polygon(closed_linestring):
    polygon = sg.Polygon(closed_linestring)
    return polygon


def process_with_contour(polygon, mean_res):
    inner_polygon = polygon.buffer(-5 * mean_res)
    contour = polygon.difference(inner_polygon)
    return inner_polygon, contour


def rasterize(data, features):
    x_res = data.affine.a
    y_res = data.affine.e
    mean_res = (np.abs(x_res) + np.abs(y_res)) / 2.0

    road_value = 1
    building_value = 2
    contour_value = 3

    geometries_and_values = []

    for feature in features:
        geometry = sg.shape(feature["geometry"])
        if geometry.type == "LineString":
            if not geometry.is_closed:
                road = open_linestring_to_polygon(geometry, mean_res)
                inner_polygon, contour = process_with_contour(road, mean_res)
                if inner_polygon.area != 0:
                    geometries_and_values.append([inner_polygon, road_value])
                if contour.area != 0:
                    geometries_and_values.append([contour, contour_value])
                # else:
                #     building = closed_linestring_to_polygon(geometry)
                #     inner_polygon, contour = process_with_contour(building, mean_res)
                #     if inner_polygon.area != 0:
                #         geometries_and_values.append([inner_polygon, building_value])
                #     if contour.area != 0:
                #         geometries_and_values.append([contour, contour_value])
        elif geometry.type in ["Polygon", "MultiPolygon"]:
            inner_polygon, contour = process_with_contour(geometry, mean_res)
            if inner_polygon.area != 0:
                geometries_and_values.append([inner_polygon, building_value])
            if contour.area != 0:
                geometries_and_values.append([contour, contour_value])
    if geometries_and_values:
        label = rf.rasterize(geometries_and_values, out_shape=data.shape, transform=data.affine, all_touched=True,
                             dtype=rasterio.uint8)
    else:
        label = np.zeros(data.shape, dtype=np.uint8)
    return label


def aggregate_features(sp_path, osm_path):
    features = []
    with open(osm_path, "r") as osm_file:
        geojson = json.load(osm_file)
    features += geojson["features"]
    with open(sp_path, "r") as sp_file:
        geojson = json.load(sp_file)
    features += geojson["features"]
    return features


def burn_raster(label_path, label, data):
    with rasterio.open(label_path, mode="w", driver="GTiff", width=data.width, height=data.height, count=1,
                       crs=data.crs, transform=data.affine, dtype=rasterio.uint8, nodata=0,
                       compress="DEFLATE") as label_file:
        label_file.write(label, indexes=1)


if __name__ == '__main__':
    root_dir = "/home/guillaume/Documents/SegNet/data/RawData"
    cities = ["Vegas", "Paris", "Shanghai", "Khartoum"]
    for city in cities:
        city_dir = os.path.join(root_dir, city)

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
