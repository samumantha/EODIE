import os
import csv
import numpy as np
from rasterstats import zonal_stats
from geometryobject import GeometryObject

class ResultObject(object):

    def __init__(self, cloudarray, indexarray, shapefile,outdir, date, tile, idname,stat):
        self.cloudarray = cloudarray
        self.indexarray = indexarray.indexarray
        self.maskedarray = self.mask_index()
        self.affine = indexarray.affine
        self.outpath = os.path.join(outdir ,'ndvi_statistics_' + date +'_'+ tile + '.csv')
        self.shapefile = shapefile
        self.extract_arrays(idname,stat)

    def mask_index(self):

        return np.ma.array(self.indexarray, mask = self.cloudarray, fill_value=-99999) 

    def extract_arrays(self, idname,stat):

        filledraster = self.maskedarray.filled(-99999)
        a=zonal_stats(self.shapefile, filledraster, stats=['mean', 'std', 'median'], band=1, geojson_out=True, all_touched=True, raster_out=True, affine=self.affine, nodata=-99999)
        
        if int(stat) == 0:
            myarrays = []
            for x in a:
                myarray = x['properties']['mini_raster_array']
                myid = [x['properties'][idname]]
                arr = myarray.tolist()
                myid.extend(arr)
                myarrays.append(myid)
            self.write_csv_arr(myarrays)
        elif int(stat) ==1:
            extractedarrays = {}
            for x in a:
                mymean = x['properties']['mean']
                mystd = x['properties']['std']
                mymedian = x['properties']['median']
                myid = x['properties'][idname]
                mystats = [str(mymean), str(mystd),str(mymedian)]
                extractedarrays[myid] = mystats
            self.write_csv(extractedarrays)


    def write_csv_arr(self,arrays):

        with open(self.outpath, "w") as f:
            writer = csv.writer(f)
            writer.writerows(arrays)

    def write_csv(self,extractedarrays):
    # this is writing the array in short rows, multiple lines? -> solve!

        with open(self.outpath, mode='a') as csv_file:
            csv_writer = csv.writer(csv_file, delimiter=',')
            for key in extractedarrays.keys():
                onerow = [key] + extractedarrays[key]
                csv_writer.writerow(onerow)