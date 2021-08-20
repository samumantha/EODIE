"""
Class with all userinput for running eodie as command line tool
"""

import argparse
import os
from datetime import datetime 
import glob
from validator import Validator
import yaml

class UserInput(object):
    """ Userinput object for EODIE
    Attributes
    -----------
    see help text for description of each attribute
    """

    def __init__(self):
        self.get_userinput()

    def get_userinput(self):
        """ gets all userinput from commandline call to run the tool and stores them as userinput attributes """

        parser = argparse.ArgumentParser()
        parser.add_argument('--platform', dest='platform',help='which platform does the data come from? options: s2')
        parser.add_argument('--dir', dest='mydir', help='directory where data is stored')
        parser.add_argument('--file', dest='myfile', help='one file')
        parser.add_argument('--shp', dest='shpbase', help='name of the shapefile (without extension)')
        parser.add_argument('--out', dest='outpath', default='./results', help='directory where results shall be saved')
        parser.add_argument('--id', dest='idname', help='name of ID field in shapefile')
        parser.add_argument('--statistics_out', dest='statistics_out',action='store_true',help='flag to indicate that statistics shall be calculated')
        parser.add_argument('--array_out', dest= 'array_out', action='store_true', help='flag to indicate that arrays shall be extracted')
        parser.add_argument('--statistics', dest='statistics',default=['mean', 'std', 'median'],help='statistics to be extracted', nargs='*')
        parser.add_argument('--index', dest='indexlist', help=' give names of indices to be processed', nargs='*')
        parser.add_argument('--start', dest='startdate',default = '20160101', help='give startdate of timerange of interest')
        parser.add_argument('--end', dest='enddate',default= datetime.now().strftime("%Y%m%d") ,help='give enddate of timerange of interest')
        parser.add_argument('--keep_shp', dest='keep_shp', action='store_true', help='flag to indicate that newly created shapefiles should be stored')
        parser.add_argument('--geotiff_out', dest='geotiff_out', action='store_true', help='flag to indicate that geotiffs shall be extracted')
        parser.add_argument('--test', dest='test', action='store_true', help='only needed for automatic testing')
        parser.add_argument('--exclude_border', dest='exclude_border', action='store_true',help='if this flag is set border pixels are excluded from calculations')
        parser.add_argument('--external_cloudmask', dest= 'extmask', default = None, help= ' location and name of external cloudmask (without tile and date and extension) if available')
        parser.add_argument('--exclude_splitshp', dest='exclude_splitshp', action='store_true',help='if this flag is set, it is assumed that splitshp has been run manually beforehand')
        parser.add_argument('--verbose',dest='verbose', action='store_true',help=' logging in logfile and prints in terminal')

        args = parser.parse_args()

        self.platform = args.platform
        configfile = './config_'+ self.platform + '.yml'

        #loading config files and merging into one dict
        with open(configfile, "r") as ymlfile:
            platform_cfg = yaml.safe_load(ymlfile)

        with open('./user_config.yml', "r") as ymlfile:
            user_cfg = yaml.safe_load(ymlfile)

        #starting python 3.9: platform_cfg | user_cfg also works
        self.config = {**platform_cfg, **user_cfg}

        Validator(args)

        self.mydir = args.mydir
        self.myfile = args.myfile
        if args.myfile is not None:
            self.input = [args.myfile]
        else:
            self.input = glob.glob(os.path.join(args.mydir,self.config['productnameidentifier']))
        # remove extension if given by mistake
        if args.shpbase.endswith('.shp'):
            self.shpbase = os.path.splitext(args.shpbase)[0]
        else:
            self.shpbase = args.shpbase
        self.outpath = args.outpath
        self.idname = args.idname
        self.statistics_out = args.statistics_out
        self.array_out = args.array_out
        self.indexlist = args.indexlist
        self.statistics = args.statistics
        self.startdate = args.startdate
        self.enddate = args.enddate
        self.keep_shp = args.keep_shp

        self.geotiff_out = args.geotiff_out
        self.test = args.test
        self.exclude_border = args.exclude_border
        self.extmask = args.extmask
        self.exclude_splitshp = args.exclude_splitshp
        self.verbose = args.verbose
