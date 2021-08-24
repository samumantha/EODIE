"""

class to find paths dependent on config/platform

authors: Samantha Wittke

"""


import os
import glob
import re


class Pathfinder(object):
    """ class dealing with paths 
    Attributes
    ----------
    cfg: dict
        dictionary with configuration elements
    rasterdir: str
        location and name of a raster product
    imgpath: str
        location and name of the bands within the raster product
    tile: str
        tile information (if available) of the raster product
    date: str
        date information of the raster product
    """

    def __init__(self,rasterdir:str, cfg:dict):
        """initializing Pathfinder object
        Parameters
        -----------
        rasterdir: str
            location and name of a raster product
        cfg: dict
            dictionary with configuration elements
        """
        
        self.cfg = cfg
        self.rasterdir = rasterdir
        
        if not self.cfg['platform'] == 'tif':
            self.get_imgpath()
            self.get_tileinfo()
        else:
            self.tile = ''
            self.imgpath = self.rasterdir
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

