"""

class for writing results into file

TODO:
* more options

"""

import os
import csv
import logging
import pickle
import fiona
import rasterio

class Writer(object):

    def __init__(self,outdir, date, tile, extractedarrays, index, statistics):
        self.outpath = os.path.join(outdir ,index+ '_' + date +'_'+ tile)
        self.extractedarrays = extractedarrays
        self.statistics = statistics
        self.tile = tile

    def write_csv(self):
        """ writing statistics results from json into csv"""
        self.outpath = self.outpath + '_stat.csv'
        logging.info('stat to csv in: ' + self.outpath)
        with open(self.outpath, mode='w') as csv_file:
            csv_writer = csv.writer(csv_file, delimiter=',')
            csv_writer.writerow(['id']+ self.statistics )
            for key in self.extractedarrays.keys():
                onerow = [key] + self.extractedarrays[key]
                csv_writer.writerow(onerow)

    def write_pickle_arr(self):
        """ writing extracted arrays to pickle"""
        self.outpath = self.outpath + '_array'
        logging.info('arrays to pickle in: ' + self.outpath)
        with open(self.outpath, mode='wb') as pkl_file:
            pickle.dump(self.extractedarrays,pkl_file)

    def write_geotiff(self, epsg_number):
        """ Writing extracted arrays to geotiff file"""
        self.outpath = self.outpath + '_array_geotiff'
        logging.info('arrays to geotiff in: ' + self.outpath)
        for key in self.extractedarrays.keys():
            logging.info('arrays to geotiff in: ' + self.outpath)
            data = self.extractedarrays[key]
            nrows, ncols = data['array'].shape
            #this may happen with external tif file, int64 is not supported
            if data['array'].dtype == 'int64':
                data['array'] = data['array'].astype('int32')

            CRS = rasterio.crs.CRS.from_dict(init=epsg_number)

            with rasterio.open(self.outpath+'_id_'+key+'.tif', 'w', driver='GTiff', height=nrows, width=ncols, count=1, crs=CRS,  
                dtype=data['array'].dtype, transform=data['affine']) as dst: 
                dst.write(data['array'],1)




