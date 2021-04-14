"""

class to extract pixel values or statistics per polygon from rasterfile
 
TODO: 
* description of in/out

"""


import os
import csv
import numpy as np
from rasterstats import zonal_stats
from geometry import Geometry

class Extractor(object):

    def __init__(self, cloudarray, indexarray, shapefile, idname, affine, statistics='count'):
        self.maskedarray = self.mask_index(indexarray,cloudarray)
        self.affine = affine
        self.shapefile = shapefile
        self.idname = idname
        self.statistics = statistics
        

    def mask_index(self, indexarray,cloudarray):
        # masking out cloudpixels from indexarray
        return np.ma.array(indexarray, mask = cloudarray, fill_value=-99999)

    def test_masking(self):
        inarray = np.array([[0.1,0.2,0.4],[0.4,0.1,0.2]])
        cloudarray  = np.array([[1,0,0],[0,1,0]])
        rightarray = np.ma.array([[0,0.2,0.4],[0.4,0,0.2]], mask = [[True,False,False],[False,True,False]], fill_value=-99999).filled()
        maskedarray = self.mask_index(inarray,cloudarray).filled()
        assert (maskedarray == rightarray).all(), 'Masking fails'



    def extract_arrays_stat(self):
        # extracting per polygon statistics from rasterfile
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
        #extracting per polygon arrays
        filledraster = self.maskedarray.filled(-99999)
        a=zonal_stats(self.shapefile, filledraster, stats=['count'], band=1, geojson_out=True, all_touched=True, raster_out=True, affine=self.affine, nodata=-99999)

        extractedarrays = {}
        for x in a:
            myarray = x['properties']['mini_raster_array']
            myid = x['properties'][self.idname]
            extractedarrays[myid] = myarray.filled(-99999)
            #print(myarray.filled(-99999))
        return extractedarrays

    """
    def extract_arrays(self):

        filledraster = self.maskedarray.filled(-99999)
        a=zonal_stats(self.shapefile, filledraster, stats=self.statistics, band=1, geojson_out=True, all_touched=True, raster_out=True, affine=self.affine, nodata=-99999)

        myarrays = []
        for x in a:
            myarray = x['properties']['mini_raster_array']
            myid = [x['properties'][self.idname]]
            arr = myarray.tolist()
            myid.extend(arr)
            myarrays.append(myid)
        return myarrays
    """

    
