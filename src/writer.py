"""

class for writing results into file

"""

import os
import csv
import logging
import pickle
import fiona
import rasterio

class Writer(object):
    """ 
    Writing lists/arrays/georeferenced arrays to file
    Attributes
    -----------
    outpath: str
        location and basename of the file where results should be stored
    extractedarrays: dict with numpy arrays
        extracted array and its information
    statistics: list of str
        extracted statistics
    tile: str
        tilename of the raster product where data was extracted from
    """

    def __init__(self,outdir, date, tile, extractedarrays, index):
        """initialize writer object
        Parameters
        -----------
        outdir: str
            location where results should be stored
        date: str
            date of the data to be stored
        tile: str
            tilename of the data to be stored
        extractedarrays: dict with numpy arrays
            extracted array and its information
        index: str
            indexname of the data to be stored

        """
        self.outpath = os.path.join(outdir ,index+ '_' + date +'_'+ tile)
        self.extractedarrays = extractedarrays
        self.tile = tile

    def write_csv(self, statistics):
        """ writing statistics results from json into csv
        Parameters
        -----------
        statistics: list of str
            extracted statistics
        """
        self.outpath = self.outpath + '_stat.csv'
        logging.info('stat to csv in: ' + self.outpath)
        with open(self.outpath, mode='w') as csv_file:
            csv_writer = csv.writer(csv_file, delimiter=',')
            csv_writer.writerow(['id']+ statistics )
            for key in self.extractedarrays.keys():
                onerow = [key] + self.extractedarrays[key]
                csv_writer.writerow(onerow)

    def write_pickle_arr(self):
        """ writing extracted arrays to pickle"""
        self.outpath = self.outpath + '_array'
        logging.info('arrays to pickle in: ' + self.outpath)
        with open(self.outpath, mode='wb') as pkl_file:
            pickle.dump(self.extractedarrays,pkl_file)

    def write_geotiff(self, epsgcode):
        """ Writing extracted arrays to geotiff file
        Parameters
        -----------
        epsgcode: str
            EPSG code of the data to be stored
        """
        self.outpath = self.outpath + '_array_geotiff'
        logging.info('arrays to geotiff in: ' + self.outpath)
        for key in self.extractedarrays.keys():
            logging.info('arrays to geotiff in: ' + self.outpath)
            data = self.extractedarrays[key]
            nrows, ncols = data['array'].shape
            #this may happen with external tif file, int64 is not supported
            if data['array'].dtype == 'int64':
                data['array'] = data['array'].astype('int32')

            CRS = rasterio.crs.CRS.from_dict(init=epsgcode)

            with rasterio.open(self.outpath+'_id_'+str(key)+'.tif', 'w', driver='GTiff', height=nrows, width=ncols, count=1, crs=CRS,  
                dtype=data['array'].dtype, transform=data['affine']) as dst: 
                dst.write(data['array'],1)




