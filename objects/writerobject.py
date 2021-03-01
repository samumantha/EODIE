import os
import csv

class WriterObject(object):

    def __init__(self,outdir, date, tile, extractedarrays):
        self.outpath = os.path.join(outdir ,'ndvi_statistics_' + date +'_'+ tile + '.csv')
        self.extractedarrays = extractedarrays

    def write_csv(self):
    # this is writing the array in short rows, multiple lines? -> solve!
        print(self.outpath)
        with open(self.outpath, mode='a') as csv_file:
            csv_writer = csv.writer(csv_file, delimiter=',')
            for key in self.extractedarrays.keys():
                onerow = [key] + self.extractedarrays[key]
                csv_writer.writerow(onerow)

    def write_csv_arr(self):

        with open(self.outpath, 'w') as csv_file:
            writer = csv.writer(csv_file)
            writer.writerows(self.extractedarrays)