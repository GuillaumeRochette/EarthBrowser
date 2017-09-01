import os
import random
import h5py
import numpy as np
from osgeo import gdal


def list_filepaths(src_dir):
    """
    Lists all files inside a directory, returns an array containing their full paths.
    :param src_dir: Source directory.
    :return: Array containing the full path of every files contained in the directory.
    """
    filenames = sorted(os.listdir(src_dir))
    filepaths = [os.path.join(src_dir, filename) for filename in filenames]
    return filepaths


def split_train_val_sets(data_paths, labels_paths, split_ratio=0.9):
    """
    Randomly splits a dataset into a training set and a validation set according to the split ratio.
    :param data_paths: Paths to the data to be splitted.
    :param labels_paths: Paths to the labels to be splitted.
    :param split_ratio: Float bound in ]0,1[, to determine the proportion of data and labels in the training set.
    :return: Two arrays containing pairs of data/labels.
    """
    zipped_list = list(zip(data_paths, labels_paths))
    random.shuffle(zipped_list)
    train_val_index = int(len(zipped_list) * split_ratio)
    train_set = zipped_list[:train_val_index]
    val_set = zipped_list[train_val_index:]
    return train_set, val_set


def create_hdf5(set_paths, hdf5_dir, max_data_per_file=2500, symmetry=False, channels=None):
    """
    Creates a HDF5 database, that will serve as input for the segmentation model.
    :param set_paths: Array containing pairs of data/labels.
    :param hdf5_dir: Directory where the HDF5 files will be stored.
    :param max_data_per_file: Max number of data/labels pairs to be written in a single HDF5 file.
    Big files will take significantly more time to take to load in memory, thus slowing down training.
    :param symmetry: Creates "synthetic" data, as it flips data and labels up-side-down.
    :param channels: Channels to be retained for the task.
    To imitate Pleiades sensor, we retain channels [1,2,4,6] from WorldView-3 sensor.
    :return:
    """
    print "Output directory : {}".format(hdf5_dir)
    hdf5_paths = []
    hfd5_file_number = 0
    data = []
    labels = []
    for i, set_path in enumerate(set_paths):
        datum_path, label_path = set_path
        datum = np.array(gdal.Open(datum_path).ReadAsArray(), dtype=np.float32)
        if channels:
            datum = datum[channels, ...]
        label = np.array(gdal.Open(label_path).ReadAsArray(), dtype=np.uint8)
        label[label == 255] = 2
        if label.ndim < 4:
            label = np.expand_dims(label, 0)
        data.append(datum)
        labels.append(label)

        if symmetry:
            v_sym_datum, v_sym_label = datum[..., ::-1, :], label[..., ::-1, :]  # vertical symmetry
            h_sym_datum, h_sym_label = datum[..., ::-1], label[..., ::-1]  # horizontal symmetry
            a_sym_datum, a_sym_label = datum[..., ::-1, ::-1], label[..., ::-1, ::-1]  # linear axial symmetry
            data.append(v_sym_datum), data.append(h_sym_datum), data.append(a_sym_datum)
            labels.append(v_sym_label), labels.append(h_sym_label), labels.append(a_sym_label)

        if len(data) >= max_data_per_file or i + 1 == len(set_paths):
            data = np.array(data)
            labels = np.array(labels)
            print data.shape, labels.shape
            print data.mean(axis=(0, 2, 3)), labels.mean(axis=(0, 2, 3))
            print "{:d} data and labels processed.".format(len(data))
            hdf5_name = "File_{:d}.h5".format(hfd5_file_number)
            hdf5_path = os.path.join(hdf5_dir, hdf5_name)
            hdf5_paths.append(hdf5_path)
            print hdf5_name
            print "Writing in {}.".format(hdf5_name)
            with h5py.File(hdf5_path, "w") as hdf5_file:
                hdf5_file.create_dataset("data", data=data)
                hdf5_file.create_dataset("labels", data=labels)
            print "Done."
            data = []
            labels = []
            hfd5_file_number += 1
    hdf5_list_path = os.path.join(hdf5_dir, "hdf5_list.txt")
    print "HDF5 Files indexed in {}.".format(hdf5_list_path)
    with open(hdf5_list_path, "w") as list_of_files:
        for hdf5_path in hdf5_paths:
            list_of_files.write(hdf5_path + "\n")


if __name__ == '__main__':
    root_dir = "/home/grochette/Documents/SegNet/data"
    data_dir = os.path.join(root_dir, "CleanData/MUL_PAN")
    labels_dir = os.path.join(root_dir, "CleanData/Labels")

    h5_dir = os.path.join(root_dir, "HDF5")
    train_dir = os.path.join(h5_dir, "Train")
    val_dir = os.path.join(h5_dir, "Validation")
    if not os.path.isdir(train_dir):
        os.makedirs(train_dir)
    if not os.path.isdir(val_dir):
        os.makedirs(val_dir)

    data_paths = list_filepaths(data_dir)
    labels_paths = list_filepaths(labels_dir)

    train_set, val_set = split_train_val_sets(data_paths, labels_paths, 0.90)
    print "Whole set contains {} files".format(len(data_paths))
    print "Train set contains {} files.".format(len(train_set))
    print "Validation set contains {} files.".format(len(val_set))
    create_hdf5(train_set, train_dir, max_data_per_file=1000, symmetry=False, channels=[1, 2, 4, 6])
    create_hdf5(val_set, val_dir, max_data_per_file=1000, symmetry=False, channels=[1, 2, 4, 6])
