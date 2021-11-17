"""

class for writing results into file


authors: Samantha Wittke, Juuso Varho
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

    def __init__(self,outdir, date, tile, extractedarrays, index, statistics = ['count'],crs=None):
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
        statistics: list of str, default=['count']
            extracted statistics
        crs: str
            coordinate reference system

        """
        self.outpath = os.path.join(outdir ,index+ '_' + date +'_'+ tile)
        self.extractedarrays = extractedarrays
        self.tile = tile
        self.statistics = statistics
        self.crs = crs

    def write_format(self, format):
        """ runs own class method based on format given 

        Parameters
        -----------
        format: str
            what to write

        Returns
        --------
        nothing itself, but runs given format function which writes data to file

        """

        default = "Unavailable format"
        return getattr(self, 'write_' + format, lambda: default)()

    def write_statistics(self):
        """ writing statistics results from json into csv
        """
        self.outpath = self.outpath + '_statistics.csv'
        logging.info('stat to csv in: ' + self.outpath)
        with open(self.outpath, mode='w') as csv_file:
            csv_writer = csv.writer(csv_file, delimiter=',')
            csv_writer.writerow(['id']+ self.statistics )
            for key in self.extractedarrays.keys():
                onerow = [key] + self.extractedarrays[key]
                csv_writer.writerow(onerow)

    def write_array(self):
        """ writing extracted arrays to pickle"""
        self.outpath = self.outpath + '_array.pickle'
        logging.info('arrays to pickle in: ' + self.outpath)
        with open(self.outpath, mode='wb') as pkl_file:
            pickle.dump(self.extractedarrays,pkl_file)

    def write_geotiff(self):
        """ Writing extracted arrays to geotiff file
        """
        self.outpath = self.outpath + '_array'
        logging.info('arrays to geotiff in: ' + self.outpath)
        for key in self.extractedarrays.keys():
            logging.info('arrays to geotiff in: ' + self.outpath)
            data = self.extractedarrays[key]
            nrows, ncols = data['array'].shape
            #this may happen with external tif file, int64 is not supported
            if data['array'].dtype == 'int64':
                data['array'] = data['array'].astype('int32')

            with rasterio.open(self.outpath+'_id_'+str(key)+'.tif', 'w', driver='GTiff', height=nrows, width=ncols, count=1, crs=self.crs,  
                dtype=data['array'].dtype, transform=data['affine']) as dst: 
                dst.write(data['array'],1)

    def write_lookup(self, lookup, shapefile, idname):
        """ Writing a lookup table when extracting arrays
        Parameters
        -----------
        lookup: string
           location and name of lookup table
        shapefile: string
            location and name of shapefile
        idname: string
            name of id in shapefile
        """
        if os.path.isfile(lookup):
            with open(lookup) as f:
                table = f.read().splitlines()
            lookup_tiles = []
            for line in table:
                lookup_tiles.append(line.split(':')[0])
            intable = self.tile in lookup_tiles
        else:
            intable = False

        if not intable:
            IDs = []
            with fiona.open(shapefile) as shp:
                for polygon in shp:
                    IDs.append(polygon['properties'][idname])
            with open(lookup, 'a') as f:
                f.write(self.tile + ':' + ','.join(str(id) for id in IDs) + "\n")
            logging.info('Appended tile ' + self.tile + ' to lookup table')



