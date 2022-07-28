# Script for converting the official Sentinel-2 tilegrid KML to a shapefile.
# The official tilegrid KML file can be downloaded from https://sentinels.copernicus.eu/web/sentinel/missions/sentinel-2/data-products

# Author: Arttu Kivimäki 

# Usage: python tilegrid_to_shp.py path/to/your/downloaded/kml/file 

from osgeo import gdal
import sys
import os
import glob

filepath = sys.argv[1]

# Define translation options

gdal_options = gdal.VectorTranslateOptions(format = "ESRI Shapefile", geometryType = 'POLYGON', selectFields = ['Name'])

# Define the output path
# Get current dir
cwd = os.getcwd()

# Get parent dir
parent_dir = os.path.abspath(os.path.join(cwd, os.pardir))

# Build output path

output_path = os.path.join(parent_dir, "src", "sentinel2_tiles_world")

# Translate to shapefile

gdal.VectorTranslate(destNameOrDestDS=output_path, srcDS=filepath, options = gdal_options)

# This will create a folder called sentinel2_tiles_world, which contains two shapefiles: Features and Info. Features is the one we need.

# Go to directory
os.chdir(output_path)
# List files with Info in their name
infofiles = glob.glob('Info*')

# Remove Info files
for file in infofiles:
    try:
        os.remove(file)
    except:
        print("Error while deleting file", file)

# List files with Feature in their name

featurefiles = glob.glob('Feature*')

# Rename Feature files
for file in featurefiles:
    try:
        extension = file.split(".")[1]
        outputname = "sentinel2_tiles_world" + "." + extension
        os.rename(file, outputname)
    except:
        print("Error renaming file ", file)

print("Conversion completed.")