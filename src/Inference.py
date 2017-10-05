import glob
import numpy as np
import os
from osgeo import gdal

import caffe
import matplotlib.pyplot as plt

model_def = "/home/grochette/Documents/SegNet/resources/SegNet7/deploy.prototxt"
model_weights = "/home/grochette/Documents/SegNet/resources/SegNet7/snapshots/segnet_infogain_iter_10500.caffemodel"
# Load the model, a .prototxt containing the model definition, and a .caffemodel (proto binary)
# containing the weight values are needed.
net = caffe.Net(model_def, caffe.TEST, weights=model_weights)

root_dir = "/home/grochette/Documents/SegNet"
clean_data_dir = os.path.join(root_dir, "data/CleanData")
# cities = ["Vegas", "Paris", "Shanghai", "Khartoum"]
cities = ["Vegas"]
mul_pan_paths = []
label_paths = []
for city in cities:
    city_dir = os.path.join(clean_data_dir, city)
    mul_pan_dir = os.path.join(city_dir, "MUL_PAN")
    label_dir = os.path.join(city_dir, "Labels")
    mul_pan_paths += glob.glob(os.path.join(mul_pan_dir, "*"))
    label_paths += glob.glob(os.path.join(label_dir, "*"))

mul_pan_paths = sorted(mul_pan_paths)
label_paths = sorted(label_paths)

print "There are currently {} listed data and labels.".format(len(mul_pan_paths))
while True:
    i = int(input())
    mul_pan_path = mul_pan_paths[i]
    label_path = label_paths[i]
    print mul_pan_path
    print label_path

    mul_pan = np.array(gdal.Open(mul_pan_path).ReadAsArray())
    label = np.array(gdal.Open(label_path).ReadAsArray())

    print mul_pan.shape, mul_pan.dtype
    print label.shape, label.dtype
    # Select the channels that were chosen for training.
    channels = [1, 2, 4, 6]
    mul_pan = mul_pan[channels, ...]

    # An image is a 3-D tensor/blob, but Caffe only accept 4-D tensor/blob (for batch computation).
    # See the deploy.prototxt to check data shapes. So we expand it.
    data = np.expand_dims(mul_pan, axis=0)
    out = net.forward_all(data=data)
    # Collect the result, which comes here from the "prob" layer (last layer in the deploy).
    seg_result = out["prob"][0]
    # Keep only the probability map of building presence.
    probabilty_map = seg_result[1]

    # Creates the classification map, which is a probability map with a threshold.
    epsilon = 5e-2
    threshold = 0.75
    classification = np.array(probabilty_map)
    mean = np.mean(classification)
    median = np.median(classification)
    classification[classification - epsilon > threshold] = 1
    classification[classification + epsilon < threshold] = 0

    print probabilty_map.shape, probabilty_map.dtype
    print probabilty_map.min(), probabilty_map.max()

    # Creates an image that can be seen with matplotlib.
    print mul_pan.shape
    img = np.transpose(mul_pan[:-1, ...][::-1, ...], axes=[1, 2, 0])
    min_pixel = np.min(img, axis=(0, 1))
    max_pixel = np.max(img, axis=(0, 1))
    img = np.array(img, dtype=np.float32)
    img = (img - min_pixel) / (max_pixel - min_pixel)
    img *= 256
    img = np.array(img, dtype=np.uint8)

    # Plot.
    plt.figure()
    plt.subplot(2, 2, 1)
    plt.imshow(img)
    plt.subplot(2, 2, 2)
    plt.imshow(label)
    plt.subplot(2, 2, 3)
    plt.imshow(probabilty_map)
    plt.subplot(2, 2, 4)
    plt.imshow(classification)
    plt.show()
