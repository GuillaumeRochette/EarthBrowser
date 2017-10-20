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
    parser = argparse.ArgumentParser(description="Use this to perform inference on data given a model.")
    parser.add_argument("--model", required=True, help="Model definition.")
    parser.add_argument("--weights", required=True, help="Model weights.")
    parser.add_argument("--data_dir", required=True, help="Directory containing the data.")
    parser.add_argument("--label_dir", help="Directory containing the labels.")
    parser.add_argument("--channels", nargs="+", type=int,
                        help="Channels to keep during inference for multispectral images.")
    parser.add_argument("--disp_channels", nargs="+", type=int, help="Channels to keep for display.")

    args = parser.parse_args()
    model = args.model
    weights = args.weights
    data_dir = args.data_dir
    channels = args.channels
    disp_channels = args.disp_channels

    # Loads network according to model definition and weights.
    net = caffe.Net(model, caffe.TEST, weights=weights)

    # Lists data.
    data_paths = sorted(glob.glob(os.path.join(data_dir, "*")))
    label_dir = args.label_dir
    # Lists labels if given as argument.
    if label_dir:
        label_paths = sorted(glob.glob(os.path.join(label_dir, "*")))

    print "There are currently {} listed data and labels.".format(len(data_paths))
    while True:
        i = int(input()) % len(data_paths)
        data_path = data_paths[i]
        # Open data raster.
        data = np.array(gdal.Open(data_path).ReadAsArray())
        print data_path
        print data.shape, data.dtype
        # Open label raster if provided.
        if label_dir:
            label_path = label_paths[i]
            label = np.array(gdal.Open(label_path).ReadAsArray())
            print label_path
            print label.shape, label.dtype

        # Select the channels that were chosen for training.
        if channels:
            input_data = data[channels, ...]
        else:
            input_data = data

        # An image is a 3-D tensor/blob, but Caffe only accept 4-D tensor/blob (for batch computation).
        # See the deploy.prototxt to check data shapes. So we expand it.
        input_data = np.expand_dims(input_data, axis=0)
        out = net.forward_all(data=input_data)
        # Collect the result, which comes here from the "prob" layer (last layer in the deploy).
        probability_map = out["prob"][0]
        # Creates the classification map, which is a probability map with a threshold.
        classification = np.argmax(probability_map, axis=0).astype(dtype=np.uint8)
        # Creates an image that can be displayed with matplotlib.
        img = plottable(data, disp_channels)
        # Creates an probability map that can be displayed with matplotlib.
        p_img = plottable(probability_map)
        # p_img = probability_map[1]
        # Plot.
        if label_dir:
            plt.figure()
            plt.subplot(2, 2, 1)
            plt.imshow(img)
            plt.subplot(2, 2, 2)
            plt.imshow(p_img)
            plt.subplot(2, 2, 3)
            plt.imshow(label)
            plt.subplot(2, 2, 4)
            plt.imshow(classification)
            plt.show()
        else:
            plt.figure()
            plt.subplot(1, 3, 1)
            plt.imshow(img)
            plt.subplot(1, 3, 2)
            plt.imshow(p_img)
            plt.subplot(1, 3, 3)
            plt.imshow(classification)
            plt.show()
