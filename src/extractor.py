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

    def __init__(self, maskedarray, shapefile, idname, affine, statistics=[], exclude_border=False):
        self.affine = affine
        self.shapefile = shapefile
        self.idname = idname
        self.all_touched = not exclude_border
        self.statistics = statistics
        self.maskedarray = maskedarray
        
        
    def extract_arrays_stat(self):
        """extracting per polygon statistics from rasterfile"""
        filledraster = self.maskedarray.filled(-99999)
        a=zonal_stats(self.shapefile, filledraster, stats=['count']+self.statistics, band=1, geojson_out=True, all_touched=self.all_touched, raster_out=True, affine=self.affine, nodata=-99999)
        if self.statistics is None:
            self.statistics = ['count']
        extractedarrays = {}
        for x in a:
            myid = x['properties'][self.idname]
            statlist = []
            for stat in self.statistics:
                if stat == 'count':
                    onestat = str(int(x['properties'][stat]))
                else:
                    #setting precision of results to .3
                    #WARNING: std should always be rounded up, but is not with this approach
                    onestat = format(x['properties'][stat], '.3f')
                
                statlist.append(onestat)
            extractedarrays[myid] = statlist
        return extractedarrays

    def extract_arrays(self):
        """extracting per polygon arrays"""
        filledraster = self.maskedarray.filled(-99999)
        a=zonal_stats(self.shapefile, filledraster, stats=['count'], band=1, geojson_out=True, all_touched=self.all_touched, raster_out=True, affine=self.affine, nodata=-99999)

        extractedarrays = {}
        for x in a:
            myarray = x['properties']['mini_raster_array']
            myid = x['properties'][self.idname]
            extractedarrays[myid] = myarray.filled(-99999)
        return extractedarrays

    def extract_array_geotiff(self):
        filledraster = self.maskedarray.filled(-99999)
        a=zonal_stats(self.shapefile, filledraster, stats=['count'], band=1, geojson_out=True, all_touched=self.all_touched, raster_out=True, affine=self.affine, nodata=-99999)

        extractedarrays = {}
        for x in a:
            myarray = x['properties']['mini_raster_array']
            myid = x['properties'][self.idname]
            extractedarrays[myid] = {}
            extractedarrays[myid]['array'] = myarray.filled(-99999)
            extractedarrays[myid]['affine'] = x['properties']['mini_raster_affine']
        return extractedarrays
        

    
