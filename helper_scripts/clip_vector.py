"""

Script for clipping vectorfile extent based on another vectorfile or the tile data found in givne directory.
Author: Arttu Kivimäki (FGI) July 2022.

Use python clip_vector.py --help for instructions. 

"""

import argparse
import os
import geopandas as gpd
import glob
import warnings

# Filter out unnecessary warnings
warnings.filterwarnings("ignore", message="pandas.Float64Index")
warnings.filterwarnings("ignore", message="pandas.Int64Index")

# Create argument parser
parser = argparse.ArgumentParser()

# Define arguments

parser.add_argument(
    "--vector",
    dest="vector",
    required=True,
    help="Full path to the vectorfile that shall be clipped.",
)

extent = parser.add_mutually_exclusive_group(required=True)
extent.add_argument(
    "--extent",
    dest="extent",
    default=None,
    help="Full path to the vectorfile whose extent should be use for clipping.",
)

extent.add_argument(
    "--dir",
    dest="dir",
    default=None,
    help="Full path to the directory containing S2 SAFE files.",
)

# Parse arguments
args = parser.parse_args()

# Check that inputs exist; exit if not
if not os.path.isfile(args.vector):
    exit("ERROR: The input vector does not exist. Please check your inputs.")

if args.extent is not None:
    if not os.path.isfile(args.extent):
        exit("ERROR: The extent vector does not exist. Please check your inputs.")

if args.dir is not None:
    if not os.path.isdir(args.dir):
        exit("ERROR: The data directory does not exist. Please check your inputs.")


# Read input vector into a geodataframe
print("Reading input vector into a geodataframe...")
vectorfile = gpd.read_file(args.vector)
print("Geodataframe ready.")

# Get the path to vectorfile for building outputpath
head, tail = os.path.split(args.vector)
name, ext = os.path.splitext(tail)
outputpath = os.path.join(head, name + "_clipped" + ext)

# Clip by another vectorfile
if args.extent is not None:
    print("Reading extent vector into a geodataframe...")
    extentfile = gpd.read_file(args.extent)
    print("Extent geodataframe ready.")
    # Reproject if necessary
    if not vectorfile.crs == extentfile.crs:
        print("Inputs are in different coordinate reference system, reprojecting...")
        vectorfile.to_crs(crs=extentfile.crs, inplace=True)
        print("Reprojection completed.")
    print("Clipping {} based on {}".format(args.vector, args.extent))
    # Clip
    clipped_vectorfile = gpd.clip(vectorfile, extentfile, keep_geom_type=True)
    # Write output to a file
    clipped_vectorfile.to_file(outputpath)
    print("Clipped vectorfile was written to {}".format(outputpath))

# Clip based on SAFE files in given directory
if args.dir is not None:
    # Glob all SAFE files in dir
    safes = glob.glob(os.path.join(args.dir, "*.SAFE"))
    # Create an empty list for tiles
    tiles = []
    # Loop through safes
    for safedir in safes:
        # Extract SAFE file name
        head, tail = os.path.split(safedir)
        # Read tilecode without beginning T
        tile = tail.split("_")[5][1:6]
        # If tilecode is not in tiles, add it
        if tile not in tiles:
            tiles.append(tile)

    # Get parent directory
    parent_dir = os.path.abspath(os.path.join(os.getcwd(), os.pardir))
    # Read Sentinel-2 tiles into a geodataframe
    tileframe = gpd.read_file(
        os.path.join(
            parent_dir, "src", "sentinel2_tiles_world", "sentinel2_tiles_world.shp"
        )
    )
    print("Tileframe read to a dataframe")
    # Only select rows where tilename can be found in the list of tiles
    tileframe = tileframe[tileframe["Name"].isin(tiles)]

    # Reproject if necessary
    if not vectorfile.crs == tileframe.crs:
        print("Inputs are in different coordinate reference system, reprojecting...")
        vectorfile.to_crs(crs=tileframe.crs, inplace=True)
        print("Reprojection completed.")

    print("Clipping {} based on data in {}.".format(args.vector, args.dir))
    # Clip
    clipped_vectorfile = gpd.clip(vectorfile, tileframe, keep_geom_type=True)
    # Write output to a file
    clipped_vectorfile.to_file(outputpath)
    print("Clipped vectorfile was written to {}".format(outputpath))
