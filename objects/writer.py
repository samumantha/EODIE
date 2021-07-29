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

class WriterObject(object):

    def __init__(self,outdir, date, tile, extractedarrays, index, statistics):
        self.outpath = os.path.join(outdir ,index+ '_' + date +'_'+ tile)
        self.extractedarrays = extractedarrays
        self.statistics = statistics

    def write_csv(self):
        self.outpath = self.outpath + '_stat.csv'
        logging.info('stat to csv in: ' + self.outpath)
        with open(self.outpath, mode='w') as csv_file:
            csv_writer = csv.writer(csv_file, delimiter=',')
            csv_writer.writerow(['id']+ self.statistics )
            for key in self.extractedarrays.keys():
                onerow = [key] + self.extractedarrays[key]
                csv_writer.writerow(onerow)

    def write_pickle_arr(self):
        self.outpath = self.outpath + '_array'
        logging.info('arrays to pickle in: ' + self.outpath)
        with open(self.outpath, mode='wb') as pkl_file:
            pickle.dump(self.extractedarrays,pkl_file)

    def write_lookup(self, lookup, shapefile, tile, idname):
        with open(lookup) as f:
                table = f.read().splitlines()

        IDs = []
        with fiona.open(shapefile) as shp:
            for polygon in shp:
                IDs.append(polygon['properties'][idname])

        lookup_tiles = []
        for line in table:
            lookup_tiles.append(line.split(':')[0])
        intable = tile in lookup_tiles

        if not intable:
            with open(lookup, 'a') as f:
                f.write(tile + ':' + ','.join(str(id) for id in IDs) + "\n")
            logging.info('appended tile ' + tile + ' to lookup table')
