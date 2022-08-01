# !/usr/bin/env/ python
# -*- coding: utf-8 -*-
""" 
Script for merging combined EODIE output statistics to the attributes to the vectorfile used in index calculation.
This script is supposed to be run after running combine_statistics_by_index.py. 
The script loops through the combined csv files, removes the rows where count is 0 and renames the columns to match the index or band. All combined indices and bands are merged into a single dataframe.
The vector file used as EODIE input will be converted into csv file, and the attribute data will be further merged to the index/band data.

Usage: python EODIE_merger.py   --dir path/to/dir/where/combined/csv-files/are
                                --output path/to/output/folder
                                --vector path/to/the/vectorfile
                                --id unique/identifier/of/vector/features

Use python EODIE_merger.py --help for more details.

Written by Arttu Kivimäki (FGI/NLS) in May 2022.

"""
# Necessary imports
import argparse
import os
import glob
import pandas as pd
from osgeo import gdal

# Create argument parser
arguments = argparse.ArgumentParser()

# Add arguments
arguments.add_argument(
    "--dir",
    type=str,
    help="Full path to the directory where csv-files to be merged are.",
)
arguments.add_argument(
    "--output",
    type=str,
    default=os.getcwd(),
    help="Full path to the directory where output files should be written. Defaults to current working directory.",
)
arguments.add_argument(
    "--vector",
    type=str,
    help="Full path to the vector file to be merged to the results.",
)
arguments.add_argument(
    "--id",
    type=str,
    default="id",
    help="The ID for joining the data. Defaults to 'id'.",
)

# Parse arguments
args = arguments.parse_args()

# Print a status update
print("Starting vector to csv conversion...")

# Define GDAL VectorTranslateOptions for vectorfile to csv conversion
gdal_options = gdal.VectorTranslateOptions(format="CSV")

# Extract vectorfile's name from the path given by user
vectorfilename = os.path.basename(args.vector).split(".")[0]

# Build output path
vector_output = args.output + "/" + vectorfilename + ".csv"

# Convert vectorfile to csv
gdal.VectorTranslate(
    destNameOrDestDS=vector_output, srcDS=args.vector, options=gdal_options
)

# Print a status update
print("Vector successfully converted to CSV!")

# Define the search string for glob to look for csv-files with 'combined' in their name
search_string = args.dir + "/combined*.csv"

# List all files matching the search string pattern
csv_list = glob.glob(search_string)


# Print a status update
print("Starting to process csv files...")
# Looping through the csv files:
for csv in csv_list:
    # Read csv into a data frame
    df = pd.read_csv(csv, parse_dates=["Dates"])
    # Filter out rows where count = 0
    df_count = df.query("count > 0")
    # Convert id into integer
    df_count = df_count.astype({"id": int})
    # Extract the index or band name from filename
    indexname = os.path.basename(csv).split("_")[1].split(".csv")[0]
    # Leave the first 5 columns untouched but loop through the latter ones
    for i in range(5, len(df_count.columns)):
        # Extract the current name
        current_name = df_count.columns[i]
        # Build the new name
        new_name = indexname + "_" + current_name
        # Rename the column
        df_count.rename(columns={current_name: new_name}, inplace=True)

    # Build the output path
    outputpath = args.output + "/combined_" + indexname + "_renamed.csv"
    # Write the output into a csv file
    df_count.to_csv(outputpath, index=False)

print("All csv files processed!")
# Create new search string
search_string = "/combined*renamed.csv"
# List the renamed files with glob
renamed_csv = glob.glob(args.output + search_string)
# Sort the list alphabetically so data will be in reasonable order in output
renamed_csv.sort()
# Read first file from the list
first_csv = pd.read_csv(renamed_csv[0])
# Remove the first file from the list
del renamed_csv[0]
# Loop through the remaining files
for csv in renamed_csv:
    # Read csv
    file = pd.read_csv(csv)
    # Merge the content of the csv with the first file read outside the loop
    first_csv = pd.merge(first_csv, file, on=["Dates", "Tiles", "id", "orbit", "count"])

# Print a status update
print("All renamed csv files merged!")
# Now the combined statistics can be merged with the csv made from vectorfile
vector = pd.read_csv(vector_output)

# Extract number of columns from vector
vector_columns = len(vector.columns)

# Merge vector and results
merged_stats = pd.merge(vector, first_csv, left_on=args.id, right_on="id")
# Sort the data frame by id and dates
# merged_stats.sort_values(by = [args.id, "Dates"], inplace = True)

# Drop the column with duplicate ID
merged_stats.drop(labels=vector_columns + 3)

# Define output path for merged statistics
merged_output = args.output + "/Merged_statistics.csv"
# Write results to CSV
merged_stats.to_csv(merged_output, index=False)

# Print a status update
print("Merged statistics are now written to", merged_output)

# Remove the files that were created during the process
os.remove(vector_output)
# List the renamed files with glob
renamed_csv = glob.glob(args.output + search_string)
# Remove files
for file in renamed_csv:
    os.remove(file)

# Print a status update
print("Temporary files created during the process have been removed.")
