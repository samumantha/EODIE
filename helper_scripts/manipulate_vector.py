"""
Script for manipulating or inspecting vectordata before running EODIE. 
Use python manipulate_vector.py --help for detailed instructions.

Written by Arttu Kivimäki (FGI) in June 2022. 
The script should work with all vector data formats supported by EODIE (.shp, .gpkg, .geojson, .fgb and .csv) but has not been extensively tested.

"""

import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt
import argparse
import os
from shapely.validation import explain_validity

# Create argument parser

parser = argparse.ArgumentParser()

# Add flag arguments for different functions

parser.add_argument(
    "--vector",
    dest="vector",
    required=True,
    help="Full path to vector file to process, extension included. Please be aware that even if completing multiple tasks at one run, each task uses only the original vectorfile as input.",
)
parser.add_argument(
    "--epsg_for_csv",
    dest="epsg",
    help="EPSG code if the input vectorfile is CSV. Not needed for other vector formats.",
)

parser.add_argument(
    "--add_unique_field",
    dest="unique",
    default=None,
    help="The field name in vectorfile to base the unique id field on.",
)
parser.add_argument(
    "--check_validity",
    dest="validity",
    action="store_true",
    help="Flag to indicate if geometry validity within vectorfile should be checked.",
)
parser.add_argument(
    "--drop_invalid",
    dest="drop",
    action="store_true",
    default=False,
    help="Flag to indicate if a vectorfile with only valid geometries shall be written. The original vectorfile will not be deleted. Requires --check_validity.",
)
parser.add_argument(
    "--remove_fields",
    dest="fields",
    default=[],
    nargs="*",
    help="Names or index numbers of the fields that should be removed from the vectorfile. A new vectorfile without given fields will be written.",
)
parser.add_argument(
    "--plot_tiles",
    dest="plot",
    action="store_true",
    help="Flag to indicate that features should be plotted in relation to Sentinel-2 tiles.",
)
parser.add_argument(
    "--simplify_tolerance",
    dest="tolerance",
    type=float,
    default=None,
    help="Tolerance value for simplifying geometries.",
)
parser.add_argument(
    "--simplify_topology",
    dest="topology",
    type=bool,
    default=True,
    help="True/False to indicate if feature topology should be preserved during simplifying. Defaults to True. Requires --simplify_tolerance.",
)


args = parser.parse_args()


def add_unique_field(vectorfile, fieldname):
    """Add unique id field to the vectorfile based on another column.

    Parameters:
    -----------
        vectorfile: geodataframe of the user-defined vectorfile
    fieldname:
        fieldname to base the unique ID's on

    Returns:
    --------
        None but writes a vectorfile with unique ID field to the same folder with original vectorfile.
    """
    print("Adding an unique ID...")
    vectorfile["unique_id"] = pd.factorize(vectorfile[fieldname])[0]
    # Extract path, filename and extension from the filename
    head, tail = os.path.split(args.vector)
    filename, extension = tail.split(".")
    # Build outputpath
    outputpath = os.path.join(head, filename + "_with_unique_ID." + extension)
    # Save the filtered output
    print("Writing the vectorfile with unique ID...")
    vectorfile.to_file(outputpath, index=False)
    print("Vectorfile with unique ID can now be found from {}".format(outputpath))


def check_validity(vectorfile):
    """Check the validity of vectorfile geometries.

    Parameters:
    -----------
        vectorfile: geodataframe of the user-defined vectorfile
    Returns:
    --------
        None; prints the rows with invalid geometries.
        If --drop_invalid was defined, will write a filtered vectorfile to the same folder as original vectorfile. Original will not be deleted.
    """
    # Check rows with empty geometries
    check_empty(vectorfile)
    print("Checking the validity of existing geometries...")
    # Check validity of geometries
    vectorfile["validity"] = vectorfile["geometry"].is_valid
    # Extract only rows with existing geometries
    vectorfile_with_geom = vectorfile.loc[vectorfile["geometry"] != None].copy()
    # Filter rows where geometries were invalid
    vectorfile_with_geom = vectorfile_with_geom.loc[
        vectorfile_with_geom["validity"] == False
    ]
    # If invalid geometries exist, run explain_validity for them
    if len(vectorfile_with_geom) > 0:
        vectorfile_with_geom["explanation"] = vectorfile_with_geom.apply(
            lambda row: explain_validity(row.geometry), axis=1
        )
        print(
            "Following features have invalid geometries:\n\n {}".format(
                vectorfile_with_geom
            )
        )

        if args.drop:
            # Filter out rows without geometry
            vectorfile = vectorfile.loc[vectorfile["geometry"] != None]
            # Filter out rows with invalid geometries
            vectorfile = vectorfile.loc[vectorfile["validity"] == True]
            # Extract path, filename and extension from the filename
            head, tail = os.path.split(args.vector)
            filename, extension = tail.split(".")
            # Build outputpath
            outputpath = os.path.join(head, filename + "_valid." + extension)
            # Save the filtered output
            print("Writing the valid vectorfile...")
            vectorfile.to_file(outputpath, index=False)
            print("Valid vectorfile can now be found from {}".format(outputpath))
    else:
        print("All features have valid geometries.")


def check_empty(vectorfile):
    """Check for empty geometries in vectorfile.

    Parameters:
    -----------
        vectorfile: geodataframe the user-defined vectorfile
    Returns:
    --------
        None; prints the rows with non-existent geometries.
    """
    print("Checking empty geometries now...")
    # Filter rows with no geometry
    vectorfile_nogeom = vectorfile[vectorfile["geometry"] == None]
    if len(vectorfile_nogeom) > 0:
        print("Following features have no geometry:\n\n {}".format(vectorfile_nogeom))
    else:
        print("All features have geometries.")


def remove_fields(vectorfile, fields):
    """Remove the fields (columns) from vectorfile based on user input.

    Parameters:
    -----------
        vectorfile: geodataframe of the user-defined vectorfile
        fields: the labels or index numbers of fields to be dropped.
    Returns:
    --------
        None but writes the filtered vectorfile to the same folder with the original.
    """
    print("Checking that given fields can be found in vectorfile...")
    # Create an empty list for field names
    field_names = []

    # Try converting field indices to field names and appending to list
    try:
        for value in fields:
            # Convert to integer as they are originally stringd
            value = int(value)
            # Add column name to field_names
            field_names.append(vectorfile.columns[value])

        print("Following columns will be filtered out: {}".format(field_names))
    except:
        # Check if error is caused by invalid index value or because the values being strings instead of integers
        if (type(value) == int) and (value > len(vectorfile.columns)):
            exit(
                "ERROR: Given index exceeds the number of columns in vectorfile. Please check your input."
            )
        else:
            # If values are column names, use them directly
            field_names = fields

    # Check that all given fields exist
    for field in field_names:
        if not field in vectorfile.columns:
            exit(
                "ERROR: The field {} was not found in {}, please check your input.".format(
                    field, args.vector
                )
            )

    # Create a filtered file by dropping the defined fields
    vectorfile_filtered = vectorfile.drop(columns=field_names)
    # Extract path, filename and extension from the filename
    head, tail = os.path.split(args.vector)
    filename, extension = tail.split(".")
    # Build outputpath
    outputpath = os.path.join(head, filename + "_filtered." + extension)
    # Save the filtered output
    print("Writing the filtered vectorfile...")
    vectorfile_filtered.to_file(outputpath, index=False)
    print("Filtered vectorfile can now be found from {}".format(outputpath))
    # Empty variable
    vectorfile_filtered = None


def plot_tiles(vectorfile):
    """Plots the Sentinel-2 tiles that overlay with vectorfile polygons.

    Parameters:
    -----------
        vectorfile: geodataframe of the user-defined vectorfile
    Returns:
    --------
        None but shows and saves the plot of tiles in the folder of the vectorfile.
    """
    # Get parent directory
    parent_dir = os.path.abspath(os.path.join(os.getcwd(), os.pardir))
    # Read Sentinel-2 tiles into a geodataframe
    sen2tiles = gpd.read_file(
        os.path.join(
            parent_dir, "src", "sentinel2_tiles_world", "sentinel2_tiles_world.shp"
        )
    )
    # Change vectorfile crs to match sen2tiles crs
    vectorfile = vectorfile.to_crs(sen2tiles.crs)
    vectorplot = vectorfile.plot(color="red")
    # Store the first column names of vectorfile for further use (it's unlikely geometry)
    column_name = vectorfile.columns[0]
    # Do overlay analysis for tiles and vectorfile
    print("Running overlay analysis for Sentinel-2 tiles and vectorfile...")
    overlay = sen2tiles.overlay(vectorfile, how="intersection")
    # Filter out rows where values of vectorfile column are false (thus the tiles that don't reach objects)
    overlay = overlay[overlay[column_name].isna() == False]
    # Extract tile names
    tiles = list(overlay["Name"].unique())
    print("Following tiles are covering the areas of interest: {}".format(tiles))
    # Choose rows from sen2tiles where the Name of tile is in tiles
    sen2tiles = sen2tiles[sen2tiles["Name"].isin(tiles)]
    # Plot edges of sen2tiles
    sen2tiles.boundary.plot(ax=vectorplot, color="blue")
    # Add labels for tiles
    sen2tiles.apply(
        lambda x: vectorplot.annotate(
            text=x["Name"], xy=x.geometry.centroid.coords[0], ha="center", size=5
        ),
        axis=1,
    )
    # Show figure (not working in Puhti)
    plt.show()
    # Define output path
    head, tail = os.path.split(args.vector)
    filename, extension = tail.split(".")
    # Build outputpath
    outputpath = os.path.join(head, "Tiles_for_" + filename + ".png")
    # Save figure
    plt.savefig(outputpath, dpi=300)
    print("Figure showing the tiles has been saved to {}".format(outputpath))
    # Save a text file
    outputpath = os.path.join(head, "Tiles_for_" + filename + ".txt")
    with open(outputpath, "w") as textfile:
        for tile in tiles:
            textfile.write("{}\n".format(tile))
    print("Textfile listing the tiles has been saved to {}".format(outputpath))
    # Empty variables
    overlay = None
    sen2tiles = None


def simplify(vectorfile, tolerance_value, topology):
    """Simplifies vectorfile geometries by given tolerance value.

    Parameters:
    -----------
        vectorfile: geodataframe of the user-defined vectorfile
        tolerance: All points in the simplified object will be within the tolerance distance of the original geometry (quote from https://shapely.readthedocs.io/en/stable/manual.html)
    Returns:
    --------
        None but writes a vectorfile with simplified geometries to the folder of original vectorfile.
    """
    print("Simplifying geometries...")
    # Run simplifying with given parameters to vectorfile geometries
    vectorfile_simplified = vectorfile.simplify(
        tolerance=tolerance_value, preserve_topology=topology
    )
    # Replace original geometries with the simplified ones
    vectorfile["geometry"] = vectorfile_simplified
    # Define output path
    head, tail = os.path.split(args.vector)
    filename, extension = tail.split(".")
    # Build outputpath
    outputpath = os.path.join(head, filename + "_simplified." + extension)
    vectorfile.to_file(outputpath, index=False)
    print("Simplified geometries have been written to {}".format(outputpath))


def check_csv_epsg(vectorfile, EPSG):
    """Checks if the EPSG code was given for csv vectorfile.

    Parameters:
    -----------
        vectorfile: geodataframe of the user-defined vectorfile.
        EPSG: EPSG code from user input

    Returns:
    --------
        If EPSG was given, a geodataframe with set EPSG.
        If EPSG was not given, exits.
    """
    # If EPSG was not given, exit:
    if EPSG is None:
        exit("For csv vector inputs, EPSG has to be defined. Please define EPSG.")
    # Otherwise
    else:
        # Set vectorfile EPSG
        vectorfile.set_crs(epsg=EPSG, inplace=True)
        print("Vectorfile EPSG has been set to {}.".format(EPSG))
        return vectorfile


def main():
    # Read user-defined vectorfile into a geopandas geodataframe

    vectorfile = gpd.read_file(args.vector)
    print("{} has been read to a geodataframe!".format(args.vector))
    if args.vector.lower().endswith(".csv"):
        vectorfile = check_csv_epsg(vectorfile, args.epsg)
    # Go through inputs and proceed accordingly
    if args.unique is not None:
        add_unique_field(vectorfile, args.unique)
    if args.validity:
        check_validity(vectorfile)
    if len(args.fields) > 0:
        remove_fields(vectorfile, args.fields)
    if args.plot:
        plot_tiles(vectorfile)
    if args.tolerance is not None:
        simplify(vectorfile, args.tolerance, args.topology)
    print("All inputs processed.")


if __name__ == "__main__":
    main()
