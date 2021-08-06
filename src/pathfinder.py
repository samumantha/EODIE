import os
import glob
import re
import yaml


class Pathfinder(object):

    def __init__(self,rasterdir, configfile):
        #loading config file
        with open(configfile, "r") as ymlfile:
            self.cfg = yaml.safe_load(ymlfile)
        self.rasterdir = rasterdir
        
        if not self.cfg['platform'] == 'tif':
            self.get_imgpath()
            self.get_tileinfo()
        else:
            self.tile = ''
            self.imgpath = self.rasterdir
        self.get_dateinfo()
        

    def get_imgpath(self):
        # getting the path until IMG_DATA
        patternimg = os.path.join(self.rasterdir ,self.cfg['bandlocation'])
        self.imgpath = glob.glob(patternimg)[0]

    def get_tileinfo(self):
        """extract tilename from filename according to pattern from from config"""
        tilepattern = r'%s' % self.cfg['tilepattern']
        self.tile = re.search(tilepattern,self.imgpath).group(0)

    def get_dateinfo(self):
        """extract date from filename according to pattern from from config"""
        datepattern = r'%s' % self.cfg['datepattern']
        self.date = re.search(datepattern,self.imgpath).group(0)

