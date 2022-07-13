"""
author: Petteri Lehti

"""


import pickle
import numpy as np
from matplotlib import pyplot as plt
from matplotlib import cm
from matplotlib import colors
from copy import copy
import argparse
import os
import sys
import yaml

from file_checker import FileChecker

with open("ap_cfg.yml", "r") as f:
    cfg = yaml.full_load(f)
indexTable = cfg["index_table"]

# About the inputs: --dir has directory to EODIE result files
# --lookup has full path to the lookup table, which is a textfile containing all the tiles in
# the results and what IDs are in the tiles. Format: 34VFN:1,2,3 (this is one row, there is one per tile).
# --end and --start included in the timeframe (see check_date in file_finder.py)
# --id and --index take lists (1 or more inputs) or all. If list has all in it, it acts as just all
# --cmap can change the used colormap/scale, see https://matplotlib.org/stable/tutorials/colors/colormaps.html for more maps
# Output will be a png with name index_id_date.png in the directory --out. To also open each figure window while running, use --show 1
# Defaults are defined in the dep_cfg.yml file
parser = argparse.ArgumentParser()
parser.add_argument(
    "--dir",
    dest="mydir",
    default=cfg["default_dir"],
    help="directory where data is stored",
)
parser.add_argument(
    "--lookup",
    dest="lookup_table",
    default=cfg["default_lookup"],
    help="complete path to lookup table",
)
parser.add_argument(
    "--out",
    dest="outdir",
    default=cfg["default_out"],
    help="directory where the results will be stored",
)
parser.add_argument(
    "--index",
    dest="index",
    default=cfg["default_index"],
    nargs="*",
    help="index or list of indices wanted",
)
parser.add_argument(
    "--start",
    dest="startdate",
    default=cfg["default_start"],
    help="start date for the wanted time period",
)
parser.add_argument(
    "--end",
    dest="enddate",
    default=cfg["default_end"],
    help="end date for the wanted time period",
)
parser.add_argument(
    "--id",
    dest="id",
    default=cfg["default_id"],
    nargs="*",
    help="ID or list of IDs of the field parcel we want to plot",
)
parser.add_argument(
    "--show",
    dest="show",
    type=int,
    default=cfg["default_show"],
    help="1 for opening each figure window, default is 0 to not open",
)
parser.add_argument(
    "--cmap",
    dest="cmap",
    default=cfg["default_cmap"],
    help="which colormap/scale to use, viridis by default",
)
parser.add_argument(
    "--series",
    dest="timeseries",
    type=int,
    default=cfg["default_series"],
    help="1 if you want timeseries over whole timeperiod",
)
input = parser.parse_args()

my_cmap = copy(cm.get_cmap(input.cmap))  # Getting (and copying) the wanted colormap
my_cmap.set_under("k")  # pixel values < min are black
my_cmap.set_bad("k")  # Invalid values (e.g. NaN) are black
my_cmap.set_over(
    "w"
)  # Uncomment for setting pixel values > max to white (masked values)

# Opening and reading lookuptable into a list of the lines:
with open(input.lookup_table, "r") as f:
    table = f.read().splitlines()


if not input.timeseries:  # Individual plots for each timepoint
    # Finding the wanted tiles based on --id input and the lookup table:
    tiles = []
    if "all" in input.id:
        tiles = ["all"]
    else:
        for line in table:
            idlist = line.split(":")[1].split(",")
            for wantedID in input.id:
                if wantedID in idlist:
                    tiles.append(line.split(":")[0])

    if len(tiles):  # This is true only if we found any fitting tiles for the wanted IDs
        for entry in os.scandir(input.mydir):
            fileChecker = FileChecker(
                entry.name
            )  # FileChecker checks if the file mathces the input
            if entry.is_file() and fileChecker.check_file(
                input.index, input.startdate, input.enddate, tiles
            ):
                with open(entry, "rb") as f:
                    new_dict = pickle.load(
                        f
                    )  # Data goes into a dictionary where IDs are keys and the arrays are values
                for id_key in new_dict:  # Loop through all IDs in the dictionary
                    if (
                        str(id_key) in input.id or "all" in input.id
                    ):  # Check for each ID if it is wanted
                        pickle_arr = new_dict[id_key]  # Array for current ID

                        fig, ax = plt.subplots(1, 1)

                        title = (
                            fileChecker.index
                            + "_"
                            + str(id_key)
                            + "_"
                            + fileChecker.date
                        )

                        # Just take values from the valid range of this index based on the config file:
                        indexLimits = indexTable[fileChecker.index]
                        my_norm = colors.Normalize(
                            vmin=indexLimits["min"], vmax=indexLimits["max"], clip=False
                        )
                        img = ax.imshow(pickle_arr, norm=my_norm, cmap=my_cmap)
                        ax.set_xticks([])  # Getting rid of axis ticks
                        ax.set_yticks([])
                        fig.colorbar(img)
                        plt.title(title)
                        if input.show:
                            plt.show()
                        fig.savefig(os.path.join(input.outdir, title + ".png"))
                        plt.close()


elif input.timeseries:  # Timeseries where id and index stay the same
    wantedIDs = input.id
    if "all" in input.id:  # If input is 'all', we want all the IDs available
        wantedIDs = []
        for line in table:
            wantedIDs.extend(
                line.split(":")[1].split(",")
            )  # Every ID extracted from lookup table
    wantedIDs = list(dict.fromkeys(wantedIDs))  # Removes duplicates

    for wantedID in wantedIDs:
        tiles = []
        for line in table:
            idlist = line.split(":")[1].split(",")
            if wantedID in idlist:
                tiles.append(line.split(":")[0])  # Add each tile with wanted IDs

        wantedIndices = input.index
        if "all" in input.index:  # If input is 'all', we want all indices available
            wantedIndices = []
            for entry in os.scandir(input.mydir):
                fileChecker = FileChecker(entry.name)
                if entry.is_file() and fileChecker.check_file(
                    input.index, input.startdate, input.enddate, tiles
                ):
                    wantedIndices.append(
                        fileChecker.index
                    )  # Add index to list for each wanted file
            wantedIndices = list(dict.fromkeys(wantedIndices))  # Removes duplicates

        for index in wantedIndices:
            files = []
            for entry in os.scandir(input.mydir):
                fileChecker = FileChecker(entry.name)
                if entry.is_file() and fileChecker.check_file(
                    [index], input.startdate, input.enddate, tiles
                ):
                    files.append(
                        entry
                    )  # Add all the files with correct index and ID to a list
            if len(files):  # Try to loop thorugh them only if the list is not empty
                fig_size = cfg["fig_size"]
                fig_w = fig_size["w"]
                fig_h = fig_size["h"]
                fig = plt.figure(figsize=(fig_w, fig_h))
                grid_size = len(files)  # Needed grid size is amount of files
                x = np.sqrt(np.divide(grid_size, np.multiply(fig_w, fig_h)))
                grid_height = max(
                    1, int(np.floor(np.multiply(fig_h, x)))
                )  # This will make height less than or equal to width
                grid_width = int(np.ceil(np.divide(grid_size, grid_height)))

                files = sorted(
                    files, key=lambda x: x.name.split("_")[1]
                )  # Sort the list of files based on time
                firstdatadate = files[0].name.split("_")[1]
                lastdatadate = files[-1].name.split("_")[1]
                title = (
                    index
                    + "_"
                    + wantedID
                    + "_timeseries_"
                    + firstdatadate
                    + "-"
                    + lastdatadate
                )
                plt.suptitle(title, size="xx-large")

                grid_index = 1  # We start from subplot 1 (indexing starts from 1 here because of how plt.subplot works)
                for file in files:
                    with open(file, "rb") as f:
                        new_dict = pickle.load(f)
                    for id_key in new_dict:
                        if str(id_key) == wantedID:
                            pickle_arr = new_dict[
                                id_key
                            ]  # find correct array based on wantedID
                    ax = plt.subplot(
                        grid_height, grid_width, grid_index
                    )  # Plotting in the correct spot

                    # Just take values from the valid range of this index based on the config file:
                    indexLimits = indexTable[index]
                    my_norm = colors.Normalize(
                        vmin=indexLimits["min"], vmax=indexLimits["max"], clip=False
                    )
                    img = plt.imshow(pickle_arr, norm=my_norm, cmap=my_cmap)
                    plt.title(
                        file.name.split("_")[1]
                    )  # Title for each subplot is just the time
                    ax.set_xticks([])  # Getting rid of axis ticks
                    ax.set_yticks([])
                    grid_index += 1  # Increment index to plot the next subplot in the correct spot

                fig.tight_layout(pad=3.0)
                # Adding colorbar:
                fig.subplots_adjust(right=0.8)
                cbar_ax = fig.add_axes([0.85, 0.15, 0.05, 0.7])
                fig.colorbar(img, cax=cbar_ax)

                fig.subplots_adjust(top=0.9)
                if input.show:
                    plt.show()
                fig.savefig(os.path.join(input.outdir, title + ".png"))
                plt.close()
