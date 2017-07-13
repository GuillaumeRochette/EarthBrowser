import os
import lmdb
import numpy as np
from osgeo import gdal
from caffe.io import array_to_datum

gdal.UseExceptions()


def write_tile_lmdb(tile_dir, db_dir, step=1000):
    tile_names = sorted(os.listdir(tile_dir))
    with lmdb.Environment(db_dir, map_size=1e12) as env:
        for i in range(0, len(tile_names), step):
            with lmdb.Transaction(env, write=True, buffers=True) as txn:
                for tile_name in tile_names[i:i + step]:
                    print tile_name
                    tile_path = os.path.join(tile_dir, tile_name)
                    tile_ds = gdal.Open(tile_path)
                    tile = np.array(tile_ds.ReadAsArray())
                    tile = tile[:-1, ...]
                    print tile.shape
                    datum = array_to_datum(tile)
                    key = tile_name.replace("Tile_", "").replace(".tif", "")
                    print key
                    txn.put(key.encode("ASCII"), datum.SerializeToString())


def write_heatmap_lmdb(heatmap_dir, db_dir, step=1000):
    heatmap_names = sorted(os.listdir(heatmap_dir))
    with lmdb.Environment(db_dir, map_size=1e12) as env:
        for i in range(0, len(heatmap_names), step):
            with lmdb.Transaction(env, write=True, buffers=True) as txn:
                for heatmap_name in heatmap_names[i:i + step]:
                    print heatmap_name

                    heatmap_path = os.path.join(heatmap_dir, heatmap_name)
                    heatmap_ds = gdal.Open(heatmap_path)
                    heatmap = np.array(heatmap_ds.ReadAsArray())
                    heatmap = np.expand_dims(heatmap, axis=0)
                    print heatmap.shape

                    datum = array_to_datum(heatmap)
                    key = heatmap_name.replace("Heatmap_", "").replace(".tif", "")
                    print key
                    txn.put(key.encode("ASCII"), datum.SerializeToString())


root_dir = "/home/guillaume/Documents/SegNet/data/Oakland_224x224"
heatmap_dir = os.path.join(root_dir, "Heatmaps")
tile_dir = os.path.join(root_dir, "Tiles")

heatmap_db_dir = os.path.join(root_dir, "OaklandLMDB/Heatmaps")
if not os.path.isdir(heatmap_db_dir):
    os.makedirs(heatmap_db_dir)
write_heatmap_lmdb(heatmap_dir, heatmap_db_dir)

tile_db_dir = os.path.join(root_dir, "OaklandLMDB/Tiles")
if not os.path.isdir(tile_db_dir):
    os.makedirs(tile_db_dir)
write_tile_lmdb(tile_dir, tile_db_dir)
