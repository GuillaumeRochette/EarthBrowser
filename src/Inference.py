import os
import numpy as np
from osgeo import gdal
import caffe
import matplotlib.pyplot as plt

root_dir = "/home/grochette/Documents/SegNet"
model_def = "/home/grochette/Documents/SegNet/resources/SegNet7/deploy.prototxt"
model_weights = "/home/grochette/Documents/SegNet/resources/SegNet7/snapshots/segnet_infogain_iter_12500.caffemodel"
# Load the model, a .prototxt containing the model definition, and a .caffemodel (proto binary)
# containing the weight values are needed.
net = caffe.Net(model_def, caffe.TEST, weights=model_weights)
mul_pan_dir = os.path.join(root_dir, "data/CleanData/MUL_PAN")
mul_pan_names = sorted(os.listdir(mul_pan_dir))
label_dir = os.path.join(root_dir, "data/CleanData/Labels")
label_names = sorted(os.listdir(label_dir))
print "There are currently {} listed data and labels.".format(len(mul_pan_names))
while True:
    i = int(input())
    print mul_pan_names[i], label_names[i]
    mul_pan_path = os.path.join(mul_pan_dir, mul_pan_names[i])
    label_path = os.path.join(label_dir, label_names[i])

    mul_pan = np.array(gdal.Open(mul_pan_path).ReadAsArray())
    label = np.array(gdal.Open(label_path).ReadAsArray())

    print mul_pan.shape, mul_pan.dtype
    print label.shape, label.dtype
    # Select the channels that were chosen for training.
    channels = [1, 2, 4, 6]
    mul_pan = mul_pan[channels, ...]

    # An image is a 3-D tensor/blob, but Caffe only accept 4-D tensor/blob (for batch computation).
    # See the deploy.prototxt to check data shapes. So we expand it.
    mul_pan = np.expand_dims(mul_pan, axis=0)
    out = net.forward_all(data=mul_pan)
    # Collect the result, which comes here from the "prob" layer (last layer in the deploy).
    seg_result = out["prob"][0]
    # Keep only the probability map of building presence.
    probabilty_map = seg_result[1]

    # Creates the classification map, which is a probability map with a threshold.
    epsilon = 1e-2
    classification = np.array(probabilty_map)
    mean = np.mean(classification)
    median = np.median(classification)
    classification[classification - epsilon > 0.5] = 1
    classification[classification + epsilon < 0.5] = 0

    print probabilty_map.shape, probabilty_map.dtype
    print probabilty_map.min(), probabilty_map.max()

    # Creates an image that can be seen with matplotlib.
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
