import os
import csv
import numpy as np
from rasterstats import zonal_stats
from geometryobject import GeometryObject

class Extractor(object):

    def __init__(self, cloudarray, indexarray, shapefile, idname, affine):
        self.indexarray = indexarray
        self.maskedarray = self.mask_index(cloudarray)
        self.affine = affine
        self.shapefile = shapefile
        self.idname = idname
        

    def mask_index(self, cloudarray):

        return np.ma.array(self.indexarray, mask = cloudarray, fill_value=-99999) 

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
        
        if int(stat) == 0:
            myarrays = []
            for x in a:
                myarray = x['properties']['mini_raster_array']
                myid = [x['properties'][self.idname]]
                arr = myarray.tolist()
                myid.extend(arr)
                myarrays.append(myid)
            return myarrays
        
   