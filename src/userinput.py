"""
Class with all userinput for running eodie as command line tool
"""

import argparse
import os
from datetime import datetime 
import glob
from validator import Validator

class UserInput(object):

    def __init__(self):
        self.get_userinput()

    def get_userinput(self):

        parser = argparse.ArgumentParser()
        parser.add_argument('--platform', dest='platform',help='which platform does the data come from? options: s2,ls8')
        parser.add_argument('--dir', dest='mydir', help='directory where S2 data is stored')
        parser.add_argument('--file', dest='myfile', help='one S2 file')
        parser.add_argument('--shp', dest='shpbase', help='name of the shapefile (without extension)')
        parser.add_argument('--out', dest='outpath', default='./results', help='directory where results shall be saved')
        parser.add_argument('--id', dest='idname', help='name of ID field in shapefile')
        parser.add_argument('--stat', dest='stat',default='1',help='1 for statistics, 0 for full array')
        parser.add_argument('--statistics', dest='statistics',default=['mean', 'std', 'median'],help='statistics to be extracted', nargs='*')
        parser.add_argument('--index', dest='indexlist', help=' give names of indices to be processed', nargs='*')
        parser.add_argument('--start', dest='startdate',default = '20160101', help='give startdate of timerange of interest')
        parser.add_argument('--end', dest='enddate',default= datetime.now().strftime("%Y%m%d") ,help='give enddate of timerange of interest')
        args = parser.parse_args()

        self.platform = args.platform
        self.configfile = './config_'+ self.platform + '.yml'

        Validator(args)

        self.mydir = args.mydir
        self.myfile = args.myfile
        if args.myfile is not None:
            self.input = [args.myfile]
        else:
            self.input = glob.glob(os.path.join(args.mydir,'*.SAFE'))
        # remove extension if given by mistake
        if args.shpbase.endswith('.shp'):
            self.shpbase = os.path.splitext(args.shpbase)[0]
        else:
            self.shpbase = args.shpbase
        self.outpath = args.outpath
        self.idname = args.idname
        self.stat = args.stat
        self.indexlist = args.indexlist
        self.statistics = args.statistics
        self.startdate = args.startdate
        self.enddate = args.enddate
