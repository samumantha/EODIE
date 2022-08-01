# Script for moving the official Landsat8 imaging grid to EODIE directory.
# The grid can be downloaded as zipfile from https://www.usgs.gov/landsat-missions/landsat-shapefiles-and-kml-files (WRS-2, daytime).
# After downloading, this script can be run to correctly relocate Landsat8 tiling.

# Author: Arttu Kivimäki (FGI) - July 2022

# Usage: python move_ls8_grid.py path/to/WRS2_descending.zip

import zipfile
import os
import sys

# Read argument into a variable
zippath = sys.argv[1]

# Get current dir
cwd = os.getcwd()

# Get parent dir
parent_dir = os.path.abspath(os.path.join(cwd, os.pardir))

# Build outputpath

output_path = os.path.join(parent_dir, "src", "landsat8_tiles_world")

# Extract files to EODIE directory
with zipfile.ZipFile(zippath, "r") as zip_ref:
    zip_ref.extractall(output_path)

print("Extraction completed.")
