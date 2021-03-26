"""

class for writing results into file

TODO:
* more options

"""

import os
import csv
import logging

class WriterObject(object):

    def __init__(self,outdir, date, tile, extractedarrays, index, statistics):
        self.outpath = os.path.join(outdir ,index+ '_statistics_' + date +'_'+ tile + '.csv')
        self.extractedarrays = extractedarrays
        self.statistics = statistics

    def write_csv(self):
    
        logging.info(self.outpath)
        with open(self.outpath, mode='w') as csv_file:
            csv_writer = csv.writer(csv_file, delimiter=',')
            csv_writer.writerow(['id']+ self.statistics )
            for key in self.extractedarrays.keys():
                onerow = [key] + self.extractedarrays[key]
                csv_writer.writerow(onerow)

    def write_csv_arr(self):

        with open(self.outpath, 'w') as csv_file:
            writer = csv.writer(csv_file)
            writer.writerows(self.extractedarrays)