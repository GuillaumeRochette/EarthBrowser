import os


def rename_files(file_dir, old_prefix, old_suffix, new_pattern, file_extension, rename=False):
    """
    Small script made orignally to rename SpaceNet files, because they are not named to be sorted in
    the same order for data and labels ... It is because they added a suffix for the labels.
    They also didn't add {:05d} when indexing the files, but {:d} only.

    :param file_dir: Directory where the files are located.
    :param old_prefix: Old prefix that needs to be removed.
    :param old_suffix: Old suffix that needs to be removed.
    :param new_pattern: New pattern to name the files after.
    :param file_extension: File extension.
    :param rename: When set to True, it actually renames the files, but you can test without renaming
    with this flag set to False.
    :return:
    """
    print file_dir
    file_names = os.listdir(file_dir)
    for file_name in file_names:
        if old_prefix not in file_name or old_suffix not in file_name:
            print "{} doesn't match either prefix or suffix.".format(file_name)
        else:
            num = int(
                file_name.replace(old_prefix, "").replace(old_suffix, "").replace(".{}".format(file_extension), ""))
            new_file_name = "{}_{:05d}.{}".format(new_pattern, num, file_extension)
            old_path = os.path.join(file_dir, file_name)
            new_path = os.path.join(file_dir, new_file_name)
            print file_name, new_file_name
            if rename:
                os.rename(old_path, new_path)


if __name__ == '__main__':
    root_dir = "/home/guillaume/Documents/SegNet/data/RawData"
    cities = ["Vegas", "Paris", "Shanghai", "Khartoum"]
    aois = [2, 3, 4, 5]
    for aoi, city in zip(aois, cities):
        city_dir = os.path.join(root_dir, city)
        file_extension = "tif"
        data_dir = os.path.join(city_dir, "MUL_PAN")
        rename_files(file_dir=data_dir,
                     old_prefix="MUL-PanSharpen_AOI_{}_{}_img".format(aoi, city),
                     old_suffix="",
                     new_pattern="{}".format(city),
                     file_extension=file_extension, rename=True)
        # label_dir = os.path.join(city_dir, "Labels")
        # rename_files(file_dir=label_dir,
        #              old_prefix="MUL-PanSharpen_AOI_{}_{}_img".format(aoi, city),
        #              old_suffix="segcls",
        #              new_pattern="{}".format(city),
        #              file_extension=file_extension, rename=False)
