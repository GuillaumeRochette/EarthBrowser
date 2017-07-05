from osgeo import gdal

ds = gdal.Open("/home/guillaume/Documents/SegNet/data/Oakland.tif")
west, xres, xskew, north, yskew, yres = ds.GetGeoTransform()
xres = 0.5
yres = -0.5
ds.SetGeoTransform([west, xres])
