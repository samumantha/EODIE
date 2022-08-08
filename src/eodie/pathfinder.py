"""

Class to find paths dependent on config/platform.

Authors: Samantha Wittke

"""


import os
import glob
import re
from xml.dom import minidom


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

        if self.cfg["platform"] == "s2":
            self.get_imgpath()
            self.get_tileinfo()
            self.get_dateinfo()
            self.get_orbit()
        elif self.cfg["platform"] == "tif":
            self.tile = ""
            self.imgpath = self.rasterdir
            self.filename = os.path.splitext(os.path.split(self.imgpath)[1])[0]
            self.date = ""
            self.orbit = 0
        elif self.cfg["platform"] == "ls8":
            self.get_imgpath()
            self.get_tileinfo()
            self.get_dateinfo()
            self.orbit = self.tile

    def get_imgpath(self):
        """Create the path to the raster data band files based on path given in bandlocation."""
        bandlocation = os.path.join(*self.cfg["bandlocation"])
        patternimg = os.path.join(self.rasterdir, bandlocation)
        self.imgpath = glob.glob(patternimg)[0]

    def get_tileinfo(self):
        """Extract tilename from filename according to pattern from config."""
        tilepattern = r"%s" % self.cfg["tilepattern"]
        self.tile = re.search(tilepattern, self.imgpath).group(0)
        if self.tile.endswith("_"):
            self.tile = self.tile[0:6]

    def get_dateinfo(self):
        """Extract date from filename according to pattern from config."""
        datepattern = r"%s" % self.cfg["datepattern"]
        if self.cfg["platform"] == "s2":
            splitted_imgpath = self.imgpath.split(os.sep)[-5]
            self.date = re.search(datepattern, splitted_imgpath).group(0)
        if self.cfg["platform"] == "ls8":
            self.date = re.search(datepattern, self.imgpath).group(0)

    def get_orbit(self):
        xmlname = "MTD_MSIL2A.xml"
        xmlpath = os.path.join(self.rasterdir, xmlname)
        doc = minidom.parse(xmlpath)
        orbit_number = int(
            doc.getElementsByTagName("SENSING_ORBIT_NUMBER")[0].firstChild.data
        )
        self.orbit = orbit_number
