import argparse
import glob
import os
import random
from osgeo import gdal

import h5py
import numpy as np


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
    training_set = zipped_list[:train_val_index]
    validation_set = zipped_list[train_val_index:]
    return training_set, validation_set


def create_hdf5(couple_paths, h5_dir, max_data_per_file=2500, symmetry=False, channels=None):
    """
    Creates a HDF5 database, that will serve as input for the segmentation model.
    :param couple_paths: Array containing pairs of data/labels.
    :param h5_dir: Directory where the HDF5 files will be stored.
    :param max_data_per_file: Max number of data/labels pairs to be written in a single HDF5 file.
    Big files will take significantly more time to take to load in memory, thus slowing down training.
    :param symmetry: Creates "synthetic" data, as it flips data and labels up-side-down.
    :param channels: Channels to be retained for the task.
    To imitate Pleiades sensor, we retain channels [1,2,4,6] from WorldView-3 sensor. (Blue, Green, Red, NIR1).
    :return: Paths of the newly created HDF5 files.
    """
    print "Output directory : {}".format(h5_dir)
    h5_paths = []
    h5_file_number = 0
    data = []
    labels = []
    for i, couple_path in enumerate(couple_paths):
        datum_path, label_path = couple_path
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
        # label[label == 255] = 2
        # SpaceNet labels are 2-D tensors/blobs, but Caffe accepts only 3-D tensors/blobs. So we expand it to 3.
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
        if len(data) >= max_data_per_file or i + 1 == len(couple_paths):
            data = np.array(data)
            labels = np.array(labels)
            print data.shape, labels.shape
            # Print informations, just to check data/labels distribution.
            print data.mean(axis=(0, 2, 3)), labels.mean(axis=(0, 2, 3))
            print "{:d} data and labels processed.".format(len(data))
            h5_name = "File_{:d}.h5".format(h5_file_number)
            h5_path = os.path.join(h5_dir, h5_name)
            h5_paths.append(h5_path)
            print h5_name
            print "Writing in {}.".format(h5_name)
            with h5py.File(h5_path, "w") as h5_file:
                h5_file.create_dataset("data", data=data)
                h5_file.create_dataset("label", data=labels)
            print "Done."
            data = []
            labels = []
            h5_file_number += 1
    return h5_paths


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Set up the HDF5 Database with ready-for-use data.")
    parser.add_argument("--input_dir", required=True,
                        help="Directory containing the city directories, themselves containing data and labels.")
    parser.add_argument("--output_dir", required=True,
                        help="ABSOLUTE PATH of the directory where the HDF5 files will be written.")
    parser.add_argument("--channels", nargs="+", type=int,
                        help="Channels to keep for multispectral images, WV3 -> PHR = [1,2,4,6].")
    parser.add_argument("--ratio", default=0.9, type=float,
                        help="Ratio for train/val to be split, e.g if ratio=0.9 then 90% of the data will be for training.")
    parser.add_argument("--max_data_per_file", type=int, default=2000,
                        help="Maximum data to be written in each HDF5 file.")
    parser.add_argument("--seed", help="Seed to reproduce the same dataset.")

    args = parser.parse_args()

    h5_train_list = []
    h5_val_list = []

    input_dir = args.input_dir
    h5_dir = args.output_dir
    split_ratio = args.ratio
    seed = args.seed
    max_data_per_file = args.max_data_per_file
    channels = args.channels

    cities = os.listdir(input_dir)

    train_dir = os.path.join(h5_dir, "Train")

    val_dir = os.path.join(h5_dir, "Validation")
    train_set_len = 0
    val_set_len = 0
    for city in cities:
        city_dir = os.path.join(input_dir, city)
        data_dir = os.path.join(city_dir, "MUL_PAN")
        label_dir = os.path.join(city_dir, "Labels")

        data_paths = sorted(glob.glob(os.path.join(data_dir, "*")))
        label_paths = sorted(glob.glob(os.path.join(label_dir, "*")))

        city_train_dir = os.path.join(train_dir, city)
        city_val_dir = os.path.join(val_dir, city)
        if not os.path.isdir(city_train_dir):
            os.makedirs(city_train_dir)
        if not os.path.isdir(city_val_dir):
            os.makedirs(city_val_dir)

        train_set, val_set = split_train_val_sets(data_paths, label_paths, split_ratio=split_ratio, seed=seed)
        train_set_len += len(train_set)
        val_set_len += len(val_set)
        print "Whole set contains {} files".format(len(train_set) + len(val_set))
        print "Train set contains {} files.".format(len(train_set))
        print "Validation set contains {} files.".format(len(val_set))
        h5_train_list += create_hdf5(train_set, city_train_dir, max_data_per_file=max_data_per_file, symmetry=False,
                                     channels=channels)
        h5_val_list += create_hdf5(val_set, city_val_dir, max_data_per_file=max_data_per_file, symmetry=False,
                                   channels=channels)

    print "Whole set contains {} files".format(train_set_len + val_set_len)
    print "Train set contains {} files.".format(train_set_len)
    print "Validation set contains {} files.".format(val_set_len)
    for a_dir, a_list in zip([train_dir, val_dir], [h5_train_list, h5_val_list]):
        h5_list_path = os.path.join(a_dir, "hdf5_list.txt")
        print "HDF5 Files indexed in {}.".format(h5_list_path)
        # Writes in a text file all of the paths to each HDF5 file.
        with open(h5_list_path, "w") as h5_list_file:
            for hdf5_path in a_list:
                h5_list_file.write(hdf5_path + "\n")
