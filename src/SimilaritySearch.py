import argparse
import glob
import os
from osgeo import gdal

import caffe
import matplotlib.pyplot as plt
import numpy as np


def plottable(data, disp_channels=None):
    """
    Alter data to make it plottable.
    :param data: 3-D Array (C,H,W) to be plotted.
    :param disp_channels: Channels to keep for plotting.
    :return: 3-D Array of uint8 ready for plot.
    """
    if disp_channels:
        data = data[disp_channels]
    img = np.transpose(data, axes=[1, 2, 0])
    min_pixel = np.min(img, axis=(0, 1))
    max_pixel = np.max(img, axis=(0, 1))
    img = np.array(img, dtype=np.float32)
    img = (img - min_pixel) / (max_pixel - min_pixel)
    img *= 256
    img = np.array(img, dtype=np.uint8)
    return img


if __name__ == '__main__':
    caffe.set_mode_gpu()
    parser = argparse.ArgumentParser(description="Use this to perform a similarity search on data given a model.")
    parser.add_argument("--model", required=True, help="Model definition.")
    parser.add_argument("--weights", required=True, help="Model weights.")
    parser.add_argument("--data_dir", required=True, help="Directory containing the data.")
    parser.add_argument("--layer", required=True, help="Name of the layer where the features will be extracted.")
    parser.add_argument("--channels", nargs="+", type=int,
                        help="Channels to keep during inference for multispectral images.")
    parser.add_argument("--disp_channels", nargs="+", type=int, help="Channels to keep for display.")

    args = parser.parse_args()
    model = args.model
    weights = args.weights
    data_dir = args.data_dir
    layer = args.layer
    channels = args.channels
    disp_channels = args.disp_channels

    # Loads network according to model definition and weights.
    net = caffe.Net(model, caffe.TEST, weights=weights)

    # Checks if the layer is in the network.
    if layer not in net.blobs:
        raise TypeError("Invalid layer name, please check the deploy.prototxt for model definition.")

    # Lists data.
    data_paths = sorted(glob.glob(os.path.join(data_dir, "*")))

    print "There are currently {} listed data and labels.".format(len(data_paths))
    features = []
    batch_size = 64
    batch = []
    for data_path in data_paths:
        print data_path
        # Open data raster.
        data = np.array(gdal.Open(data_path).ReadAsArray())
        # Select the channels that were chosen for training.
        if channels:
            data = data[channels, ...]
        batch.append(data)
        if len(batch) >= batch_size:
            # An image is a 3-D tensor/blob, but Caffe only accept 4-D tensor/blob for batch computation.
            # See the deploy.prototxt to check data shapes.
            batch = np.array(batch)
            print batch.shape, batch.dtype
            out = net.forward(data=batch, end=layer)
            feature_batch = np.array(out[layer], dtype=np.float16)
            print feature_batch.shape, feature_batch.dtype
            # Collect the batch of features and add it to the total.
            features.append(feature_batch)
            batch = []
    features = np.concatenate(features)
    print features.shape, features.dtype
    # Reshape features to 1-D array for future cross-correlation.
    features = features.reshape(features.shape[0], np.prod(features.shape[1:]))
    print features.shape, features.dtype

    # Compute the correlation matrix.
    corr_mat = np.corrcoef(features)
    print corr_mat.shape, corr_mat.dtype

    # Display the 8 most correlated to the selected image.
    while True:
        i = int(input()) % len(data_paths)
        corr_vect = corr_mat[i]
        sorted_indices = np.argsort(corr_vect)[::-1]
        top_indices = sorted_indices[:9]
        top_corrcoefs = corr_vect[top_indices]
        print top_indices
        print top_corrcoefs

        plt.figure()
        i = 1
        for index in top_indices:
            plt.subplot(3, 3, i)
            data_path = data_paths[index]
            data = np.array(gdal.Open(data_path).ReadAsArray())
            img = plottable(data, disp_channels)
            plt.imshow(img)
            i += 1
        plt.show()
