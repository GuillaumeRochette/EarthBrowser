import os
import glob
import rasterio
import json
import shapely.geometry as sg

root_dir = "/home/guillaume/Documents/SegNet/data/RawData"
cities = ["Vegas", "Paris", "Shanghai", "Khartoum"]
for city in cities:
    types = {}
    city_dir = os.path.join(root_dir, city)
    osm_dir = os.path.join(city_dir, "OpenStreetMap_Labels")
    sn_dir = os.path.join(city_dir, "SpaceNet_Labels")

    sn_paths = sorted(glob.glob(os.path.join(sn_dir, "*")))
    osm_paths = sorted(glob.glob(os.path.join(osm_dir, "*")))
    geojson_paths = sn_paths + osm_paths

    for geojson_path in geojson_paths:
        with open(geojson_path, "r") as geojson_file:
            geojson = json.load(geojson_file)
        for feature in geojson["features"]:
            type = sg.shape(feature["geometry"]).type
            if type not in types:
                types[type] = 1
            else:
                types[type] += 1
    print city, types
