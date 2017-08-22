import os

if __name__ == '__main__':
    root_dir = "/home/grochette/Documents/SegNet/data"
    city = "Khartoum"
    aoi_number = 5
    data_dir = os.path.join(root_dir, "RawData/{}/Data").format(city)
    label_dir = os.path.join(root_dir, "RawData/{}/Labels").format(city)
    print data_dir
    print label_dir

    data_names = os.listdir(data_dir)
    for data_name in data_names:
        num = int(
            data_name.replace("RGB-PanSharpen_AOI_{}_{}_8bit_img".format(aoi_number, city), "").replace(".tif", ""))
        # num = int(data_name.replace("3band_AOI_1_RIO_8bit_img", "").replace(".tif", ""))
        new_name = "RGB_PAN_{}_{:05d}.tif".format(city, num)
        data_path = os.path.join(data_dir, data_name)
        new_path = os.path.join(data_dir, new_name)
        print data_path, new_path
        os.rename(data_path, new_path)

    label_names = os.listdir(label_dir)
    for label_name in label_names:
        num = int(
            label_name.replace("RGB-PanSharpen_AOI_{}_{}_img".format(aoi_number, city), "").replace("segcls.tif", ""))
        # num = int(label_name.replace("3band_AOI_1_RIO_img", "").replace("segcls.tif", ""))
        new_name = "CLASS_SEG_{}_{:05d}.tif".format(city, num)
        label_path = os.path.join(label_dir, label_name)
        new_path = os.path.join(label_dir, new_name)
        print label_path, new_path
        os.rename(label_path, new_path)
