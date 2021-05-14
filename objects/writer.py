"""

class for writing results into file

TODO:
* more options

"""

import os
import csv
import logging
import pickle
import pandas as pd

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


