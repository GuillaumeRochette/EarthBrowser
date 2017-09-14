import glob
import h5py
import numpy as np
import os
import random
from osgeo import gdal


def split_train_val_sets(data_paths, labels_paths, split_ratio=0.9, seed=None):
    """
    Randomly splits a dataset into a training set and a validation set according to the split ratio.
    :param data_paths: Paths to the data to be splitted.
    :param labels_paths: Paths to the labels to be splitted.
    :param split_ratio: Float bound in ]0,1[, to determine the proportion of data and labels in the training set.
    :return: Two arrays containing pairs of data/labels.
    """
    zipped_list = list(zip(data_paths, labels_paths))
    if seed:
        random.seed(seed)
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
    To imitate Pleiades sensor, we retain channels [1,2,4,6] from WorldView-3 sensor. (Blue, Green, Red, NIR1).
    :return:
    """
    print "Output directory : {}".format(hdf5_dir)
    hdf5_paths = []
    hfd5_file_number = 0
    data = []
    labels = []
    for i, set_path in enumerate(set_paths):
        datum_path, label_path = set_path
        # Convert data dtype into float32, because Deep Learning is about floats.
        datum = np.array(gdal.Open(datum_path).ReadAsArray(), dtype=np.float32)
        # Retain specific channels, if it was specified.
        if channels:
            datum = datum[channels, ...]
        # Convert label dtype into uint8 if you have less than 255 labels ;)
        label = np.array(gdal.Open(label_path).ReadAsArray(), dtype=np.uint8)
        # In the SpaceNet Dataset, the absence of building is denoted by a 0, the presence by a 1 or a 100.
        # and the boundary by a 255. But Caffe accepts only consecutive labels starting with 0.
        # label[label == 100] = 1
        label[label == 255] = 2
        # SpaceNet labels are 2-D tensors/blobs, but Caffe accepts only 3-D tensors/blobs. So we expand it to 3.
        if label.ndim < 4:
            label = np.expand_dims(label, 0)
        data.append(datum)
        labels.append(label)

        # Artificially expand the dataset by flipping the image up, side and down.
        if symmetry:
            v_sym_datum, v_sym_label = datum[..., ::-1, :], label[..., ::-1, :]  # Vertical symmetry.
            h_sym_datum, h_sym_label = datum[..., ::-1], label[..., ::-1]  # Horizontal symmetry.
            a_sym_datum, a_sym_label = datum[..., ::-1, ::-1], label[..., ::-1, ::-1]  # Linear axial symmetry.
            data.append(v_sym_datum), data.append(h_sym_datum), data.append(a_sym_datum)
            labels.append(v_sym_label), labels.append(h_sym_label), labels.append(a_sym_label)

        # Writes a batch of data/labels into a HDF5 file.
        if len(data) >= max_data_per_file or i + 1 == len(set_paths):
            data = np.array(data)
            labels = np.array(labels)
            print data.shape, labels.shape
            # Printed for information, just to check data/labels distribution.
            print data.mean(axis=(0, 2, 3)), labels.mean(axis=(0, 2, 3))
            print "{:d} data and labels processed.".format(len(data))
            hdf5_name = "File_{:d}.h5".format(hfd5_file_number)
            hdf5_path = os.path.join(hdf5_dir, hdf5_name)
            hdf5_paths.append(hdf5_path)
            print hdf5_name
            print "Writing in {}.".format(hdf5_name)
            with h5py.File(hdf5_path, "w") as hdf5_file:
                hdf5_file.create_dataset("data", data=data)
                hdf5_file.create_dataset("label", data=labels)
            print "Done."
            data = []
            labels = []
            hfd5_file_number += 1
    hdf5_list_path = os.path.join(hdf5_dir, "hdf5_list.txt")
    print "HDF5 Files indexed in {}.".format(hdf5_list_path)
    # Writes in a text file all of the paths to each HDF5 file.
    with open(hdf5_list_path, "w") as list_of_files:
        for hdf5_path in hdf5_paths:
            list_of_files.write(hdf5_path + "\n")


if __name__ == '__main__':
    root_dir = "/home/grochette/Documents/SegNet"
    clean_data_dir = os.path.join(root_dir, "data/CleanData")
    cities = ["Vegas", "Paris", "Shanghai", "Khartoum"]
    label_paths = []
    data_paths = []
    for city in cities:
        data_dir = os.path.join(clean_data_dir, "{}/MUL_PAN".format(city))
        label_dir = os.path.join(clean_data_dir, "{}/Labels".format(city))
        data_paths += sorted(glob.glob(os.path.join(data_dir, "*")))
        label_paths += sorted(glob.glob(os.path.join(label_dir, "*")))

    h5_dir = os.path.join(root_dir, "data/HDF5")
    train_dir = os.path.join(h5_dir, "Train")
    val_dir = os.path.join(h5_dir, "Validation")
    if not os.path.isdir(train_dir):
        os.makedirs(train_dir)
    if not os.path.isdir(val_dir):
        os.makedirs(val_dir)

    train_set, val_set = split_train_val_sets(data_paths, label_paths, split_ratio=0.90, seed=1337)
    print "Whole set contains {} files".format(len(data_paths))
    print "Train set contains {} files.".format(len(train_set))
    print "Validation set contains {} files.".format(len(val_set))
    create_hdf5(train_set, train_dir, max_data_per_file=1000, symmetry=False, channels=[1, 2, 4, 6])
    create_hdf5(val_set, val_dir, max_data_per_file=1000, symmetry=False, channels=[1, 2, 4, 6])
