"""

Class to extract pixel values or statistics per polygon from rasterfile.

Authors: Samantha Wittke, Juuso Varho
 
"""


import os
import csv
import numpy as np
from rasterstats import zonal_stats


class Extractor(object):
    """Extracting object based information from an array with affine information and a geodataframe."""

    def __init__(
        self,
        maskedarray,
        geodataframe,
        idname,
        affine,
        statistics,
        orbit=0,
        band=1,
        exclude_border=False,
    ):
        """Initialize the Extractor object.

        Parameters
        ----------
        maskedarray: array
            the array to extract information from
        geodataframe: GeoDataframe
            geodataframe containing the (polygon) features to extract zonal statistics from
        idname: str
            Fieldname of unique ID field of the geodataframe (will be used as polygon identifier for storing statistics)
        affine: Affine object
            containing affine/transform information of the array
        statistics: list of str, optional, default: empty list
            list of statistics to be extracted for each polygon
        orbit: None
            orbit information of input raster data (Sentinel-2)
        band: integer, default = 1
            which band from a multiband geotif should be handled
        exclude_border: boolean, optional, default: False
            indicator if border pixels should be in- (False) or excluded (True)

        """
        self.affine = affine
        self.geodataframe = geodataframe
        self.idname = idname
        self.all_touched = not exclude_border
        self.maskedarray = maskedarray
        self.statistics = statistics
        self.orbit = orbit
        self.band = int(band)

    def extract_format(self, format):
        """Run own class method based on format given.

        Parameters
        -----------
        format: str
            format to be calculated

        Returns
        --------
        nothing itself, but runs given format function which returns a dictionary for the given format

        """
        default = "Unavailable format"
        if format == "database":
            format = "statistics"
        return getattr(self, "extract_" + format, lambda: default)()

    def extract_statistics(self):
        """Extract per polygon statistics from rasterfile with affine information."""
        # following is necessary for external tif which is not a masked array
        try:
            self.maskedarray.dtype
            filledraster = self.maskedarray.filled(-99999)
        except AttributeError:
            filledraster = self.maskedarray

        a = zonal_stats(
            self.geodataframe,
            filledraster,
            stats=self.statistics,
            band=self.band,
            geojson_out=True,
            all_touched=self.all_touched,
            raster_out=False,
            affine=self.affine,
            nodata=-99999,
        )
        extractedarrays = {}
        for x in a:
            try:
                myid = x["properties"][self.idname]
            except KeyError:
                myid = x[self.idname]
            statlist = []
            for stat in self.statistics:
                if stat == "count":
                    onestat = str(int(x["properties"][stat]))
                else:
                    # setting precision of results to .3
                    # WARNING: std should always be rounded up, but is not with this approach
                    if not x["properties"][stat] is None:
                        onestat = format(x["properties"][stat], ".3f")
                    else:
                        onestat = None

                statlist.append(onestat)
            statlist.insert(0, self.orbit)
            extractedarrays[myid] = statlist
        return extractedarrays

    def extract_array(self):
        """Extract per polygon arrays from rasterfile with affine information."""
        try:
            self.maskedarray.dtype
            filledraster = self.maskedarray.filled(+99999)
        except AttributeError:
            filledraster = self.maskedarray

        a = zonal_stats(
            self.geodataframe,
            filledraster,
            stats=self.statistics,
            band=self.band,
            geojson_out=True,
            all_touched=self.all_touched,
            raster_out=True,
            affine=self.affine,
            nodata=-99999,
        )

        extractedarrays = {}
        for x in a:
            myarray = x["properties"]["mini_raster_array"]
            myid = x["properties"][self.idname]
            extractedarrays[myid] = myarray.filled(-99999)
        return extractedarrays

    def extract_geotiff(self):
        """Extract per polygon geotiffs."""
        try:
            self.maskedarray.dtype
            filledraster = self.maskedarray.filled(+99999)
        except AttributeError:
            filledraster = self.maskedarray
        a = zonal_stats(
            self.geodataframe,
            filledraster,
            stats=self.statistics,
            band=self.band,
            geojson_out=True,
            all_touched=self.all_touched,
            raster_out=True,
            affine=self.affine,
            nodata=-99999,
        )

        extractedarrays = {}
        for x in a:
            myarray = x["properties"]["mini_raster_array"]
            myid = x["properties"][self.idname]
            extractedarrays[myid] = {}
            extractedarrays[myid]["array"] = myarray.filled(-99999)
            extractedarrays[myid]["affine"] = x["properties"]["mini_raster_affine"]
        return extractedarrays
