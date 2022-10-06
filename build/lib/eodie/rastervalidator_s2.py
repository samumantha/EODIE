"""

Class to check that cloudcover is below the maximum given by user and to check that area of interest is not within nodata zone - only Sentinel-2.

Authors: Samantha Wittke

"""


import os
import glob
import logging
from xml.dom import minidom
from rasterstats import zonal_stats


class RasterValidatorS2(object):
    """Check validity for processing of Sentinel-2 raster product.

    Attributes
    -----------
    SAFEpath: str
        location and name of a raster product
    maxcloudcover: int
        maximum cloudcover allowed for processing
    geometryobject: object
        object containing the vector data to be processed
    not_cloudcovered: boolean
        if rasterproduct is below maximum cloudcover
    datacovered: boolean
        if area of interest (given with geometryobject) is datacovered (not all nan)
    """

    def __init__(self, SAFEpath, maxcloudcover):
        """Initialize raster validator object.

        Parameters
        ----------
        SAFEpath: str
            location and name of a raster product
        maxcloudcover: int
            maximum cloudcover allowed for processing
        """
        self.SAFEpath = SAFEpath
        self.maxcloudcover = maxcloudcover

    def check_integrity(self):
        """Check the integrity of the SAFE directory. Images for all bands and metadata XML file should be found.

        Returns
        --------
        Integrity: boolean
            integrity of the file, true if all necessary files can be found
        """

        # Check that metadata file exists
        xmlname = "MTD_MSIL2A.xml"
        xmlpath = os.path.join(self.SAFEpath, xmlname)
        # Default integrity to True
        integrity = True

        # If xml file exists, check for individual band directories.
        if os.path.isfile(xmlpath):

            # In a complete SAFE directory, there are 35 .jp2 files.
            granulepath = os.path.join(
                self.SAFEpath, "GRANULE", "*", "IMG_DATA", "*", "*.jp2"
            )
            # With less than 35 .jp2 files, log an error message and set integrity to False
            if len(glob.glob(granulepath)) < 35:
                logging.error(
                    " At least one image band from {} is missing.".format(self.SAFEpath)
                )
                integrity = False
        # If xml file does not exist, log an error message and set integrity to False
        else:
            logging.error(
                " Metadata .XML file for {} was not found.".format(self.SAFEpath)
            )
            integrity = False

        return integrity

    def get_xml(self):
        """Build the location and name of the xml file containing metadata for Sentinel-2."""
        xmlname = "MTD_MSIL2A.xml"
        xmlpath = os.path.join(self.SAFEpath, xmlname)
        return xmlpath

    def read_xml(self, xmlpath):
        """Parse the XML file into doc to be read.

        Parameters
        -----------
        xmlpath: str
            location and name of the metadata xmlfile
        Returns
        -------
        doc:
            accessible version of the xml file
        """
        doc = minidom.parse(xmlpath)
        return doc

    def get_cloudcover_percentage(self, doc):
        """Retrieve the cloudcover information from opened XML file.

        Parameters
        -----------
        doc:
            accessible version of the xml file
        Returns
        --------
        cc_perc: float
            Cloudcover percentage for whole raster product tile
        """
        cc_perc = float(
            doc.getElementsByTagName("Cloud_Coverage_Assessment")[0].firstChild.data
        )
        return cc_perc

    def check_cloudcover(self):
        """Check that according to metadata the cloudcover is below user given threshold."""
        cloudcover_percentage = self.get_cloudcover_percentage(
            self.read_xml(self.get_xml())
        )
        if cloudcover_percentage <= self.maxcloudcover:
            return True
        else:
            return False

    def get_bandpath(self):
        """Get a representative band location and name (red band)."""
        bandpath = glob.glob(
            os.path.join(
                self.SAFEpath, "*", "*", "IMG_DATA", "R60m", "*" + "B04_60m.jp2"
            )
        )[0]
        return bandpath

    def check_datacover(self, convex_hull):
        """Check hat there is data within the convexhull of the given shapefile.

        Parameters
        -----------
        geometryobject: VectorData
            Polygons of areas of interest

        Returns
        --------
        boolean
            whether there is raster data on the area(s) of interest
        """
        # convex_hull = geometryobject.get_convex_hull()
        tile = str(self.SAFEpath[-26:-24])
        epsgcode = "EPSG:326" + tile
        convex_hull_reprojected = convex_hull.to_crs(epsgcode)

        zonal_statistics = zonal_stats(
            convex_hull_reprojected,
            self.get_bandpath(),
            stats="mean",
            band=1,
            nodata=-99999,
        )
        if (
            zonal_statistics[0]["mean"] == 0.0
            or type(zonal_statistics[0]["mean"]) is not float
        ):
            return False
        else:
            return True
