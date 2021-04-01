"""

class for writing results into file

TODO:
* more options

"""

import os
import csv
import logging
import pickle

class WriterObject(object):

    def __init__(self,outdir, date, tile, extractedarrays, index, statistics):
        self.outpath = os.path.join(outdir ,index+ '_statistics_'+ date +'_'+ tile)
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


    def write_csv_arr(self):
        self.outpath = self.outpath + '_array.csv'
        logging.info('arrays to csv in: ' + self.outpath)
        with open(self.outpath, 'w') as csv_file:
            writer = csv.writer(csv_file)
            for key, value in self.extractedarrays.items():
                writer.writerow([key,value])
            """
            for key in self.extractedarrays.keys():
                onerow = [key] + self.extractedarrays[key]
                writer.writerow(onerow)
            """
            