"""

Class to find paths dependent on config/platform.

Authors: Samantha Wittke

"""


import os
import glob
import re


class Pathfinder(object):
    """Class dealing with paths.

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

    def __init__(self, rasterdir: str, cfg: dict):
        """Initialize Pathfinder object.

        Parameters
        -----------
        rasterdir: str
            location and name of a raster product
        cfg: dict
            dictionary with configuration elements
        """
        self.cfg = cfg
        self.rasterdir = rasterdir

        if not self.cfg["platform"] == "tif":
            self.get_imgpath()
            self.get_tileinfo()
            self.get_dateinfo()
        else:
            self.tile = ""
            self.imgpath = self.rasterdir
            self.date = ""

    def get_imgpath(self):
        """Create the path to the raster data band files based on path given in bandlocation."""
        bandlocation = os.path.join(*self.cfg["bandlocation"])
        patternimg = os.path.join(self.rasterdir, bandlocation)
        self.imgpath = glob.glob(patternimg)[0]

    def get_tileinfo(self):
        """Extract tilename from filename according to pattern from from config."""
        tilepattern = r"%s" % self.cfg["tilepattern"]
        self.tile = re.search(tilepattern, self.imgpath).group(0)

    def get_dateinfo(self):
        """Extract date from filename according to pattern from from config."""
        datepattern = r"%s" % self.cfg["datepattern"]
        splitted_imgpath = self.imgpath.split("/")[-5]
        self.date = re.search(datepattern, splitted_imgpath).group(0)
