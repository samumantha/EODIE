"""

class to extract pixel values or statistics per polygon from rasterfile
 
TODO: 
* description of in/out

"""


import os
import csv
import numpy as np
from rasterstats import zonal_stats

class Extractor(object):

    def __init__(self, maskedarray, shapefile, idname, affine, statistics='count'):
        self.affine = affine
        self.shapefile = shapefile
        self.idname = idname
        self.statistics = statistics
        self.maskedarray = maskedarray
        
    def extract_arrays_stat(self):
        """extracting per polygon statistics from rasterfile"""
        filledraster = self.maskedarray.filled(-99999)
        a=zonal_stats(self.shapefile, filledraster, stats=['count']+self.statistics, band=1, geojson_out=True, all_touched=True, raster_out=True, affine=self.affine, nodata=-99999)

        extractedarrays = {}
        for x in a:
            myid = x['properties'][self.idname]
            statlist = []
            for stat in self.statistics:
                onestat = x['properties'][stat]
                statlist.append(str(onestat))
            extractedarrays[myid] = statlist
        return extractedarrays

    def extract_arrays(self):
        """extracting per polygon arrays"""
        filledraster = self.maskedarray.filled(-99999)
        a=zonal_stats(self.shapefile, filledraster, stats=['count'], band=1, geojson_out=True, all_touched=True, raster_out=True, affine=self.affine, nodata=-99999)

        extractedarrays = {}
        for x in a:
            myarray = x['properties']['mini_raster_array']
            myid = x['properties'][self.idname]
            extractedarrays[myid] = myarray.filled(-99999)
        return extractedarrays


    
