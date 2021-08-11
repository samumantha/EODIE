import os
import glob
import re
import yaml


class Pathfinder(object):
    """ class dealing with paths 
    Attributes
    ----------
    cfg
    rasterdir
    imgpath
    tile 
    date
    """

    def __init__(self,rasterdir:str, configfile:str):
        """initializing Pathfinder object
        Parameters
        -----------
        rasterdir: str
            location and name of a raster product
        configfile: str
            location and name of the configuration file
        """
        
        with open(configfile, "r") as ymlfile:
            self.cfg = yaml.safe_load(ymlfile)
        self.rasterdir = rasterdir
        self.get_imgpath()
        self.get_tileinfo()
        self.get_dateinfo()
        

    def get_imgpath(self):
        """creating the path to the raster data band files based on path given in bandlocation"""
        bandlocation = os.path.join(*self.cfg['bandlocation'])
        patternimg = os.path.join(self.rasterdir ,bandlocation)
        self.imgpath = glob.glob(patternimg)[0]

    def get_tileinfo(self):
        """extract tilename from filename according to pattern from from config"""
        tilepattern = r'%s' % self.cfg['tilepattern']
        self.tile = re.search(tilepattern,self.imgpath).group(0)

    def get_dateinfo(self):
        """extract date from filename according to pattern from from config"""
        datepattern = r'%s' % self.cfg['datepattern']
        self.date = re.search(datepattern,self.imgpath).group(0)

