import argparse
from datetime import datetime 


class UserInput(object):

    def __init__(self):
        self.get_userinput()

    def get_userinput(self):


        parser = argparse.ArgumentParser()
        parser.add_argument('--dir', dest='mydir', help='directory where S2 data is stored')
        parser.add_argument('--file', dest='myfile', help='if only one file shall be processed give name here')
        parser.add_argument('--shp', dest='shpbase', help='name of the shapefile (without extension)')
        parser.add_argument('--out', dest='outpath', help='directory where results shall be saved')
        parser.add_argument('--id', dest='idname', help='name of ID field in shapefile')
        parser.add_argument('--stat', dest='stat',default='1',help='1 for statistics, 0 for full array')
        parser.add_argument('--statistics', dest='statistics',default=['mean', 'std', 'median'],help='statistics to be extracted', nargs='*')
        parser.add_argument('--index', dest='indexlist', help=' give names of indices to be processed', nargs='*')
        parser.add_argument('--start', dest='startdate',default = '20160101', help='give startdate of timerange of interest')
        parser.add_argument('--end', dest='enddate',default= datetime.now().strftime("%Y%m%d") ,help='give enddate of timerange of interest')
        args = parser.parse_args()

        self.mydir = args.mydir
        self.myfile = args.myfile
        self.shpbase = args.shpbase
        self.outpath = args.outpath
        self.idname = args.idname
        self.stat = args.stat
        self.indexlist = args.indexlist
        self.statistics = args.statistics
        self.startdate = args.startdate
        self.enddate = args.enddate