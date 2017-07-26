import os
import random
import h5py
import numpy as np
from osgeo import gdal


def list_filepaths(a_dir):
    filenames = sorted(os.listdir(a_dir))
    filepaths = [os.path.join(a_dir, filename) for filename in filenames]
    return filepaths


def split_train_val_sets(data_paths, labels_paths, train_val_ratio):
    zipped_list = list(zip(data_paths, labels_paths))
    random.shuffle(zipped_list)
    train_val_index = int(len(zipped_list) * train_val_ratio)
    train_set = zipped_list[:train_val_index]
    val_set = zipped_list[train_val_index:]
    return train_set, val_set


def mean_centered_datum(datum):
    temp = np.transpose(datum, axes=[1, 2, 0])
    mean_pixel = np.array([103.939, 116.779, 123.68])
    temp -= mean_pixel
    datum = np.transpose(temp, axes=[2, 0, 1])
    return datum


def create_HDF5(data_set, hdf5_dir, max_data_per_file=2500, symmetry=False):
    print "Output directory : {}".format(hdf5_dir)
    hdf5_paths = []
    batches = [data_set[i:i + max_data_per_file] for i in range(0, len(data_set), max_data_per_file)]
    for i, batch in enumerate(batches):
        data = []
        labels = []
        hdf5_name = "File_{:d}.h5".format(i)
        hdf5_path = os.path.join(hdf5_dir, hdf5_name)
        hdf5_paths.append(hdf5_path)
        print hdf5_name
        print "Processing {:d} data and labels".format(len(batch))
        for j, set_paths in enumerate(batch):
            datum_path, label_path = set_paths

            datum = np.array(gdal.Open(datum_path).ReadAsArray(), dtype=np.float32)
            label = np.array(gdal.Open(label_path).ReadAsArray(), dtype=np.uint8)

            datum = datum[::-1, ...]  # switch from RGB to BGR
            datum = mean_centered_datum(datum)

            data.append(datum)
            labels.append(label)

            if symmetry:
                v_sym_datum, v_sym_label = datum[..., ::-1, :], label[..., ::-1, :]  # vertical symmetry
                h_sym_datum, h_sym_label = datum[..., ::-1], label[..., ::-1]  # horizontal symmetry
                a_sym_datum, a_sym_label = datum[..., ::-1, ::-1], label[..., ::-1, ::-1]  # linear axial symmetry
                data.append(v_sym_datum), data.append(h_sym_datum), data.append(a_sym_datum)
                labels.append(v_sym_label), labels.append(h_sym_label), labels.append(a_sym_label)
        data = np.array(data)
        labels = np.array(labels)
        print "Done."
        print "Writing in {}.".format(hdf5_name)
        with h5py.File(hdf5_path, "w") as hdf5_file:
            hdf5_file.create_dataset("data", data=data)
            hdf5_file.create_dataset("labels", data=labels)
        print "Done."
    hdf5_list_path = os.path.join(hdf5_dir, "hdf5_list.txt")
    print "HDF5 Files indexed in {}.".format(hdf5_list_path)
    with open(hdf5_list_path, "w") as list_of_files:
        for hdf5_path in hdf5_paths:
            list_of_files.write(hdf5_path + "\n")


if __name__ == '__main__':
    root_dir = "/home/guillaume/Documents/SegNet/data/Data_224x224"
    data_dir = os.path.join(root_dir, "Data")
    labels_dir = os.path.join(root_dir, "Labels")

    h5_dir = os.path.join(root_dir, "HDF5")
    train_dir = os.path.join(h5_dir, "Train")
    val_dir = os.path.join(h5_dir, "Validation")
    if not os.path.isdir(train_dir):
        os.makedirs(train_dir)
    if not os.path.isdir(val_dir):
        os.makedirs(val_dir)

    data_paths = list_filepaths(data_dir)
    labels_paths = list_filepaths(labels_dir)

    train_set, val_set = split_train_val_sets(data_paths, labels_paths, 0.80)
    create_HDF5(train_set, train_dir, max_data_per_file=500, symmetry=True)
    create_HDF5(val_set, val_dir, max_data_per_file=2000, symmetry=False)
