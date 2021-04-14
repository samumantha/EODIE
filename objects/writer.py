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


"""
#following do not write full arrays
    def write_csv_arr(self):
        self.outpath = self.outpath + '_array.csv'
        logging.info('arrays to csv in: ' + self.outpath)
        with open(self.outpath, 'w') as csv_file:
            writer = csv.writer(csv_file)
            for key, value in self.extractedarrays.items():
                writer.writerow([key,value])

    def write_csv_arr_pd(self):
        self.outpath = self.outpath + '_array_pd.csv'
        logging.info('arrays to csv in: ' + self.outpath)
        #df = pd.DataFrame.from_records(self.extractedarrays)
        df = pd.Series(self.extractedarrays).to_frame()
        print(df.columns)
        print(df.index)
        print(df.head(5))
        print(df.iloc[0,0])
        print(type(df.iloc[0,0]))
        df.to_csv(self.outpath,reduced=False)
"""
