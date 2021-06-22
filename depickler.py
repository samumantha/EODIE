import pickle
import numpy as np
from matplotlib import pyplot as plt
from matplotlib import cm
from matplotlib import colors
from copy import copy
import argparse
import os

from file_finder import FileFinder

# Most of the default-values are just for debugging
parser = argparse.ArgumentParser()
parser.add_argument('--dir', dest='mydir', default='/home/petteri/EODIE/results/', help='directory where data is stored')
parser.add_argument('--lookup', dest='lookup_table', default='/home/petteri/EODIE/results/script_test/lookuptable.txt')
parser.add_argument('--out', dest='outdir', default='/home/petteri/EODIE/pngresults', help='directory where the results will be stored')
parser.add_argument('--index', dest='index', default=['ndvi'], nargs='*', help='index or list of indices wanted')
parser.add_argument('--start', dest='start', default='20200101', help='start date for the wanted time period')
parser.add_argument('--end', dest='end', default='20211231', help='end date for the wanted time period')
parser.add_argument('--id', dest='id', default=['1'], nargs='*', help='ID of the field parcel we want to plot')
parser.add_argument('--cmap', dest='cmap', default='viridis', help='which colormap/scale to use, viridis by default')
args = parser.parse_args()

f = open(args.lookup_table, "r")
table = f.read().splitlines()
f.close()

tiles=[]
idFound = False
if 'all' in args.id:
    idFound = True
    tiles = ['all']
else:
    for line in table:
        idlist = line.split(":")[1].split(",")
        for wantedID in args.id:
            if wantedID in idlist:
                tiles.append(line.split(":")[0])
                idFound = True

if idFound:
    for entry in os.scandir(args.mydir):
        fileFinder = FileFinder(entry.name)
        if (entry.is_file() and fileFinder.check_file(args.index, args.start, args.end, tiles)):
            infile = open(entry, 'rb')
            new_dict = pickle.load(infile)
            infile.close()
            for id_key in new_dict:
                if str(id_key) in args.id or 'all' in args.id:
                    pickle_arr = new_dict[id_key]

                    fig, ax = plt.subplots(1,1)

                    my_cmap = copy(cm.get_cmap(args.cmap))
                    my_norm = colors.Normalize(vmin=-1, vmax=1, clip=False)
                    my_cmap.set_under('k')
                    my_cmap.set_bad('k')

                    title = fileFinder.index + '_' + str(id_key) + '_' + fileFinder.date

                    img = ax.imshow(pickle_arr, norm=my_norm, cmap=my_cmap)
                    ax.set_xticks([])
                    ax.set_yticks([])
                    fig.colorbar(img)
                    plt.title(title)
                    plt.show()
                    fig.savefig(os.path.join(args.outdir, title + '.png'))
                    plt.close()
