import pickle
import numpy as np
from matplotlib import pyplot as plt
from matplotlib import cm
from matplotlib import colors
from copy import copy
import argparse
import os

from file_finder import FileFinder

# About the inputs: --dir has directory to EODIE result files
# --lookup has full path to the lookup table, which is a textfile containing all the tiles in
# the results and what IDs are in the tiles. Format: 34VFN:1,2,3 (this is one row, there is one per tile).
# --end is currently excluded and --start included in the timeframe (see check_date in file_finder.py)
# --id and --index take lists (1 or more inputs) or all. If list has all in it, it acts as just all
# --cmap can change the used colormap/scale, see https://matplotlib.org/stable/tutorials/colors/colormaps.html for more maps
# Output will be a png with name index_id_date.png in the directory --out. To also open each figure window while running, use --show 1 
# Most of the default-values are just for debugging 
parser = argparse.ArgumentParser()
parser.add_argument('--dir', dest='mydir', default='/home/petteri/EODIE/results/', help='directory where data is stored')
parser.add_argument('--lookup', dest='lookup_table', default='/home/petteri/EODIE/results/script_test/lookuptable.txt', help='complete path to lookup table')
parser.add_argument('--out', dest='outdir', default='/home/petteri/EODIE/pngresults', help='directory where the results will be stored')
parser.add_argument('--index', dest='index', default=['all'], nargs='*', help='index or list of indices wanted')
parser.add_argument('--start', dest='startdate', default='20200101', help='start date for the wanted time period')
parser.add_argument('--end', dest='enddate', default='20201231', help='end date for the wanted time period')
parser.add_argument('--id', dest='id', default=['all'], nargs='*', help='ID or list of IDs of the field parcel we want to plot')
parser.add_argument('--show', dest='show', default='0', help='1 for opening each figure window, default is 0 to not open')
parser.add_argument('--cmap', dest='cmap', default='viridis', help='which colormap/scale to use, viridis by default')
parser.add_argument('--series', dest='timeseries', default='0', help='1 if you want timeseries over whole timeperiod')
input = parser.parse_args()

my_cmap = copy(cm.get_cmap(input.cmap)) # Getting (and copying) the wanted colormap
my_norm = colors.Normalize(vmin=-1, vmax=1, clip=False) # Just take values between -1 and 1
my_cmap.set_under('k') # pixel values < -1 are black
my_cmap.set_bad('k') # Invalid values (e.g. NaN) are black
#my_cmap.set_over('w') # Uncomment for setting pixel values > 1 to white (masked values?)

# Opening and reading lookuptable into a list of the lines:
f = open(input.lookup_table, "r")
table = f.read().splitlines()
f.close()

if not int(input.timeseries): # Individual plots for each timepoint
    # Finding the wanted tiles based on --id input and the lookup table:
    tiles=[]
    if 'all' in input.id:
        tiles = ['all']
    else:
        for line in table:
            idlist = line.split(":")[1].split(",")
            for wantedID in input.id:
                if wantedID in idlist:
                    tiles.append(line.split(":")[0])

    if len(tiles): # This is true only if we found any fitting tiles for the wanted IDs
        for entry in os.scandir(input.mydir):
            fileFinder = FileFinder(entry.name) # FileFinder checks if the file mathces the input
            if (entry.is_file() and fileFinder.check_file(input.index, input.startdate, input.enddate, tiles)):
                infile = open(entry, 'rb')
                new_dict = pickle.load(infile) # Data goes into a dictionary where IDs are keys and the arrays are values
                infile.close()
                for id_key in new_dict: # Loop through all IDs in the dictionary
                    if str(id_key) in input.id or 'all' in input.id: # Check for each ID if it is wanted
                        pickle_arr = new_dict[id_key] # Array for current ID

                        fig, ax = plt.subplots(1,1)

                        title = fileFinder.index + '_' + str(id_key) + '_' + fileFinder.date

                        img = ax.imshow(pickle_arr, norm=my_norm, cmap=my_cmap)
                        ax.set_xticks([]) # Getting rid of axis ticks
                        ax.set_yticks([])
                        fig.colorbar(img)
                        plt.title(title)
                        if int(input.show):
                            plt.show()
                        fig.savefig(os.path.join(input.outdir, title + '.png'))
                        plt.close()


elif int(input.timeseries): # Timeseries where id and index stay the same
    wantedIDs = input.id 
    if 'all' in input.id: # If input is 'all', we want all the IDs available
        wantedIDs=[]
        for line in table:
            wantedIDs.extend(line.split(":")[1].split(",")) # Every ID extracted from lookup table
    wantedIDs = list(dict.fromkeys(wantedIDs)) # Removes duplicates

    for wantedID in wantedIDs:
        tiles = []
        for line in table:
                idlist = line.split(":")[1].split(",")
                if wantedID in idlist:
                    tiles.append(line.split(":")[0]) # Add each tile with wanted IDs
        
        wantedIndices = input.index
        if 'all' in input.index: # If input is 'all', we want all indices available
            wantedIndices=[]
            for entry in os.scandir(input.mydir):
                fileFinder = FileFinder(entry.name)
                if(entry.is_file() and fileFinder.check_file(input.index, input.startdate, input.enddate, tiles)):
                    wantedIndices.append(fileFinder.index) #Add index to list for each wanted file
            wantedIndices = list(dict.fromkeys(wantedIndices)) # Removes duplicates

        for index in wantedIndices:
            files = []
            for entry in os.scandir(input.mydir):
                fileFinder = FileFinder(entry.name)
                if(entry.is_file() and fileFinder.check_file([index], input.startdate, input.enddate, tiles)):
                    files.append(entry) # Add all the files with correct index and ID to a list 
            if len(files): # Try to loop thorugh them only if the list is not empty
                grid_size = len(files) # Needed grid size is amount of files
                grid_width = int(np.floor(np.sqrt(grid_size))) # This will make width less than or equal to height
                grid_height = int(np.ceil(np.divide(grid_size, grid_width)))
                fig, axs = plt.subplots(grid_height, grid_width)
                title = index + '_' + wantedID
                plt.suptitle(title)

                grid_index = 1 # We start from subplot 1 (indexing starts from 1 here because of how plt.subplot works)
                files = sorted(files, key=lambda x: x.name.split("_")[1]) # Sort the list of files based on time
                for file in files:
                    infile = open(file, 'rb')
                    new_dict = pickle.load(infile)
                    infile.close()
                    for id_key in new_dict:
                        if str(id_key) == wantedID:
                            pickle_arr = new_dict[id_key] # find correct array based on wantedID
                    plt.subplot(grid_height, grid_width, grid_index) # Plotting in the correct spot
                    img = plt.imshow(pickle_arr, norm=my_norm, cmap=my_cmap)
                    plt.title(file.name.split("_")[1]) # Title for each subplot is just the time
                    plt.subplot(grid_height, grid_width, grid_index).set_xticks([]) # Getting rid of axis ticks
                    plt.subplot(grid_height, grid_width, grid_index).set_yticks([])
                    grid_index += 1 # Increment index to plot the next subplot in the correct spot

                # Adding colorbar:
                fig.subplots_adjust(right=0.8)
                cbar_ax = fig.add_axes([0.85, 0.15, 0.05, 0.7])
                fig.colorbar(img, cax=cbar_ax)
                
                if int(input.show):
                    plt.show()
                fig.savefig(os.path.join(input.outdir, title + "_timeseries.png"))
                plt.close()



