"""

class to extract pixel values or statistics per polygon from rasterfile
 
TODO: 
* description of in/out

"""


import os
import csv
import numpy as np
from rasterstats import zonal_stats
from geometryobject import GeometryObject

class Extractor(object):

    def __init__(self, cloudarray, indexarray, shapefile, idname, affine):
        self.maskedarray = self.mask_index(indexarray,cloudarray)
        self.affine = affine
        self.shapefile = shapefile
        self.idname = idname
        

    def mask_index(self, indexarray,cloudarray):

        return np.ma.array(indexarray, mask = cloudarray, fill_value=-99999) 

    def test_masking(self):

        inarray = np.array([[0.1,0.2,0.4][0.4,0.1,0.2]])
        cloudarray  = np.array([[1,0,0][0,1,0]])
        rightarray = np.array([[-99999,0.2,0.4][0.4,-99999,0.2]])
        maskedarray = self.mask_index(inarray,cloudarray)
        assert (maskedarray != rightarray).all(), 'Masking fails'

    def extract_arrays_stat(self):

        filledraster = self.maskedarray.filled(-99999)
        a=zonal_stats(self.shapefile, filledraster, stats=['mean', 'std', 'median'], band=1, geojson_out=True, all_touched=True, raster_out=True, affine=self.affine, nodata=-99999)

        extractedarrays = {}
        for x in a:
            mymean = x['properties']['mean']
            mystd = x['properties']['std']
            mymedian = x['properties']['median']
            myid = x['properties'][self.idname]
            mystats = [str(mymean), str(mystd),str(mymedian)]
            extractedarrays[myid] = mystats
        return extractedarrays


    def extract_arrays(self):

        filledraster = self.maskedarray.filled(-99999)
        a=zonal_stats(self.shapefile, filledraster, stats=['mean', 'std', 'median'], band=1, geojson_out=True, all_touched=True, raster_out=True, affine=self.affine, nodata=-99999)
        
        
        myarrays = []
        for x in a:
            myarray = x['properties']['mini_raster_array']
            myid = [x['properties'][self.idname]]
            arr = myarray.tolist()
            myid.extend(arr)
            myarrays.append(myid)
        return myarrays
