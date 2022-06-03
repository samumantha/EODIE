"""

class to extract pixel values or statistics per polygon from rasterfile

authors: Samantha Wittke, Juuso Varho
 
"""


import os
import csv
import numpy as np
from rasterstats import zonal_stats

class Extractor(object):

    """Extracting object based information from an array with affine information and a shapefile"""

    def __init__(self, maskedarray, shapefile, idname, affine, statistics, exclude_border=False):
        """Initializing the Extractor object

        Parameters
        ----------
        maskedarray: array
            the array to extract information from
        shapefile: str
            Path to the shapefile containing polygons to extract information for
        idname: str
            Fieldname of unique ID field of the shapefile (will be used as polygon identifier for storing statistics)
        affine: Affine object
            containing affine/transform information of the array
        statsistics: list of str, optional, default: empty list
            list of statistics to be extracted for each polygon
        exclude_border: boolean, optional, default: False
            indicator if border pixels should be in- (False) or excluded (True)
        
        """
        
        self.affine = affine
        self.shapefile = shapefile
        self.idname = idname
        self.all_touched = not exclude_border
        self.maskedarray = maskedarray
        self.statistics = statistics

    def extract_format(self, format):
        """ runs own class method based on format given 

        Parameters
        -----------
        format: str
            format to be calculated

        Returns
        --------
        nothing itself, but runs given format function which returns a dictionary for the given format 

        """

        default = "Unavailable format"
        return getattr(self, 'extract_' + format, lambda: default)()
        
    def extract_statistics(self):
        """extracting per polygon statistics from rasterfile with affine information"""
        # following is necessary for external tif which is not a masked array
        try:
            self.maskedarray.dtype
            filledraster = self.maskedarray.filled(-99999)
        except AttributeError:
            filledraster = self.maskedarray
        
        a=zonal_stats(self.shapefile, filledraster, stats=self.statistics, band=1, geojson_out=True, all_touched=self.all_touched, raster_out=False, affine=self.affine, nodata=-99999)
        extractedarrays = {}
        for x in a:
            try:
                myid = x['properties'][self.idname]
            except KeyError:
                myid = x[self.idname]
            statlist = []
            for stat in self.statistics:
                if stat == 'count':
                    onestat = str(int(x['properties'][stat]))
                else:
                    #setting precision of results to .3
                    #WARNING: std should always be rounded up, but is not with this approach
                    if not x['properties'][stat] is None:
                        onestat = format(x['properties'][stat], '.3f')
                    else:
                        onestat = None
                
                statlist.append(onestat)
            extractedarrays[myid] = statlist
        return extractedarrays

    def extract_array(self):
        """extracting per polygon arrays from rasterfile with affine information"""
        try:
            self.maskedarray.dtype
            filledraster = self.maskedarray.filled(+99999)
        except AttributeError:
            filledraster = self.maskedarray
        
        a=zonal_stats(self.shapefile, filledraster, stats=self.statistics, band=1, geojson_out=True, all_touched=self.all_touched, raster_out=True, affine=self.affine, nodata=-99999)

        extractedarrays = {}
        for x in a:
            myarray = x['properties']['mini_raster_array']
            myid = x['properties'][self.idname]
            extractedarrays[myid] = myarray.filled(-99999)
        return extractedarrays

    def extract_geotiff(self):
        try:
            self.maskedarray.dtype
            filledraster = self.maskedarray.filled(+99999)
        except AttributeError:
            filledraster = self.maskedarray
        a=zonal_stats(self.shapefile, filledraster, stats=self.statistics, band=1, geojson_out=True, all_touched=self.all_touched, raster_out=True, affine=self.affine, nodata=-99999)

        extractedarrays = {}
        for x in a:
            myarray = x['properties']['mini_raster_array']
            myid = x['properties'][self.idname]
            extractedarrays[myid] = {}
            extractedarrays[myid]['array'] = myarray.filled(-99999)
            extractedarrays[myid]['affine'] = x['properties']['mini_raster_affine']
        return extractedarrays
    
    def extract_database(self):
        """extracting per polygon statistics from rasterfile with affine information"""
        # following is necessary for external tif which is not a masked array
        try:
            self.maskedarray.dtype
            filledraster = self.maskedarray.filled(-99999)
        except AttributeError:
            filledraster = self.maskedarray
        
        a=zonal_stats(self.shapefile, filledraster, stats=self.statistics, band=1, geojson_out=True, all_touched=self.all_touched, raster_out=False, affine=self.affine, nodata=-99999)
        extractedarrays = {}
        for x in a:
            try:
                myid = x['properties'][self.idname]
            except KeyError:
                myid = x[self.idname]
            statlist = []
            for stat in self.statistics:
                if stat == 'count':
                    onestat = str(int(x['properties'][stat]))
                else:
                    #setting precision of results to .3
                    #WARNING: std should always be rounded up, but is not with this approach
                    if not x['properties'][stat] is None:
                        onestat = format(x['properties'][stat], '.3f')
                    else:
                        onestat = None
                
                statlist.append(onestat)
            extractedarrays[myid] = statlist
        return extractedarrays

    
