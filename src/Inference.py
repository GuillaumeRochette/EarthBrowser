import os
import numpy as np
from osgeo import gdal
import caffe
import matplotlib.pyplot as plt

root_dir = "/home/grochette/Documents/SegNet"
# model_def = os.path.join(root_dir, "resources/segnet_deploy.prototxt")
# model_weights = os.path.join(root_dir, "resources/segnet_iter_1895.caffemodel")
model_def = "/home/grochette/Documents/SegNet/resources/fcn32/deploy.prototxt"
model_weights = "/home/grochette/Documents/SegNet/resources/fcn32/snapshot_iter_260.caffemodel"

net = caffe.Net(model_def, caffe.TEST, weights=model_weights)
data_dir = os.path.join(root_dir, "data/CleanData/Data")
data_names = sorted(os.listdir(data_dir))
label_dir = os.path.join(root_dir, "data/CleanData/Labels")
label_names = sorted(os.listdir(label_dir))
i = 27898
# i = 65235
print data_names[i], label_names[i]
data_path = os.path.join(data_dir, data_names[i])
label_path = os.path.join(label_dir, label_names[i])

data = np.array(gdal.Open(data_path).ReadAsArray())
label = np.array(gdal.Open(label_path).ReadAsArray())

print data.shape, data.dtype
print label.shape, label.dtype

out = net.forward_all(data=np.expand_dims(data, axis=0))
# seg_result = out["prob"]
seg_result = out["score"]
prediction = seg_result
print prediction.shape, prediction.dtype
print prediction.min(), prediction.max()

img = np.transpose(data, axes=[1, 2, 0])

plt.figure()
plt.subplot(1, 3, 1)
plt.imshow(img)
plt.subplot(1, 3, 2)
plt.imshow(label)
plt.subplot(1, 3, 3)
plt.imshow(prediction)
plt.show()
