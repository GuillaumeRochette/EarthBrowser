import os

if __name__ == '__main__':
    root_dir = "/home/guillaume/Documents/SegNet/data"
    # data_dir = os.path.join(root_dir, "RawData/Paris/Data")
    # label_dir = os.path.join(root_dir, "RawData/Paris/Labels")
    data_dir = os.path.join(root_dir, "RawData/Rio/Data")
    label_dir = os.path.join(root_dir, "RawData/Rio/Labels")
    print data_dir
    print label_dir

    data_names = os.listdir(data_dir)
    for data_name in data_names:
        # num = int(data_name.replace("RGB-PanSharpen_AOI_3_Paris_8bit_img", "").replace(".tif", ""))
        # new_name = "RGB_PAN_Paris_{:05d}.tif".format(num)
        num = int(data_name.replace("3band_AOI_1_RIO_img", "").replace(".tif", ""))
        new_name = "RGB_PAN_Rio_{:05d}.tif".format(num)
        data_path = os.path.join(data_dir, data_name)
        new_path = os.path.join(data_dir, new_name)
        print data_path, new_path
        # os.rename(data_path, new_path)

    label_names = os.listdir(label_dir)
    for label_name in label_names:
        # num = int(label_name.replace("RGB-PanSharpen_AOI_3_Paris_img", "").replace("segcls.tif", ""))
        # new_name = "CLASS_SEG_Paris_{:05d}.tif".format(num)
        num = int(label_name.replace("3band_AOI_1_RIO_img", "").replace("segcls.tif", ""))
        new_name = "CLASS_SEG_Rio_{:05d}.tif".format(num)
        label_path = os.path.join(label_dir, label_name)
        new_path = os.path.join(label_dir, new_name)
        print label_path, new_path
        # os.rename(label_path, new_path)
