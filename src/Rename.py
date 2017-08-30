import os


def rename_files(file_dir, old_prefix, old_suffix, new_pattern, file_extension, verbose=True, rename=False):
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
            if verbose:
                print file_name, new_file_name
            if rename:
                os.rename(old_path, new_path)


if __name__ == '__main__':
    root_dir = "/home/grochette/Documents/SegNet/data/RawData"
    # cities = ["Rio", "Vegas", "Paris", "Shanghai", "Khartoum"]
    city = "Vegas"
    city_dir = os.path.join(root_dir, city)
    # file_dir = os.path.join(city_dir, "MUL_PAN")
    # file_dir = os.path.join(city_dir, "RGB_PAN")
    file_dir = os.path.join(city_dir, "Labels")
    old_prefix = "CLASS_SEG_Vegas_"
    old_suffix = ""
    new_pattern = city
    file_extension = "tif"
    rename_files(file_dir, old_prefix, old_suffix, new_pattern, file_extension, rename=False)
