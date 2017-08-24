import os

def rename_from_utilities(data_dir, label_dir, city, aoi_number):
    print data_dir
    print label_dir

    data_names = os.listdir(data_dir)
    for data_name in data_names:
        if aoi_number == 1:
            num = int(data_name.replace("3band_AOI_1_RIO_8bit_img", "").replace(".tif", ""))
        else:
            num = int(data_name.replace("RGB-PanSharpen_AOI_{}_{}_8bit_img".format(aoi_number, city), "").replace(".tif", ""))
        new_name = "RGB_PAN_{}_{:05d}.tif".format(city, num)
        data_path = os.path.join(data_dir, data_name)
        new_path = os.path.join(data_dir, new_name)
        print data_path, new_path
        os.rename(data_path, new_path)

    label_names = os.listdir(label_dir)
    for label_name in label_names:
        if aoi_number == 1:
            num = int(label_name.replace("3band_AOI_1_RIO_img", "").replace("segcls.tif", ""))
        else:
            num = int(label_name.replace("RGB-PanSharpen_AOI_{}_{}_img".format(aoi_number, city), "").replace("segcls.tif", ""))
        new_name = "CLASS_SEG_{}_{:05d}.tif".format(city, num)
        label_path = os.path.join(label_dir, label_name)
        new_path = os.path.join(label_dir, new_name)
        print label_path, new_path
        os.rename(label_path, new_path)

def rename_for_digits(data_dir, label_dir):
    data_names = sorted(os.listdir(data_dir))
    for data_name in data_names:
        new_data_name = data_name.replace("RGB_PAN_", "")
        data_path = os.path.join(data_dir, data_name)
        new_data_path = os.path.join(data_dir, new_data_name)
        print data_name, new_data_name
        os.rename(data_path, new_data_path)

    label_names = sorted(os.listdir(label_dir))
    for label_name in label_names:
        new_label_name = label_name.replace("CLASS_SEG_", "")
        label_path = os.path.join(label_dir, label_name)
        new_label_path = os.path.join(label_dir, new_label_name)
        print label_name, new_label_name
        os.rename(label_path, new_label_path)



if __name__ == '__main__':
    root_dir = "/home/grochette/Documents/SegNet/data"
    # cities = ["Rio", "Vegas", "Paris", "Shanghai", "Khartoum"]
    # for i, city in enumerate(cities):
    #     data_dir = os.path.join(root_dir, "RawData/{}/Data").format(city)
    #     label_dir = os.path.join(root_dir, "RawData/{}/Labels").format(city)
    #     aoi_number = i + 1
    #     rename_from_utilities(data_dir, label_dir, city, aoi_number)

    # data_dir = os.path.join(root_dir, "CleanData/Data")
    # label_dir = os.path.join(root_dir, "CleanData/Labels")
    # rename_for_digits(data_dir, label_dir)

