import pickle
import numpy as np
from matplotlib import pyplot as plt
from matplotlib import cm
from matplotlib import colors
from copy import copy
import argparse
import os

from file_finder import FileFinder

parser = argparse.ArgumentParser()
parser.add_argument('--dir', dest='mydir', default='/home/petteri/EODIE/results/script_test/', help='directory where data is stored')
parser.add_argument('--out', dest='outdir')
parser.add_argument('--index', dest='index', default='ndvi', nargs='*')
parser.add_argument('--start', dest='start', default='20200625')
parser.add_argument('--end', dest='end', default='20200630')
parser.add_argument('--tile', dest='tile', default='34VFN', help='The tilename')
parser.add_argument('--id', dest='id', default='1', help='ID of the field parcel we want to plot')
parser.add_argument('--cmap', dest='cmap', default='viridis', help='Which colormap/scale to use')

args = parser.parse_args()

for entry in os.scandir(args.mydir):
    fileFinder = FileFinder(entry.name)
    if (entry.is_file() and fileFinder.check_file(args.index, args.start, args.end, args.tile)):
        infile = open(entry, 'rb')
        new_dict = pickle.load(infile)
        infile.close()
        pickle_arr = new_dict[args.id]

        fig, ax = plt.subplots(1,1)

        my_cmap = copy(cm.get_cmap(args.cmap))
        my_norm = colors.Normalize(vmin=-1, vmax=1, clip=False)
        my_cmap.set_under('k')
        my_cmap.set_bad('k')

        title = fileFinder.index + '_' + args.id + '_' + fileFinder.date

        img = ax.imshow(pickle_arr, norm=my_norm, cmap=my_cmap)
        ax.set_xticks([])
        ax.set_yticks([])
        fig.colorbar(img)
        plt.title(title)
        plt.show()
        fig.savefig(title + '.png')
