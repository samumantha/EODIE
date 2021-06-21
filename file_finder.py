import os

class FileFinder(object):

    def __init__(self, filename):
        parts = filename.split('_')
        if len(parts) == 4:
            self.index = parts[0]
            self.date = parts[1]
            self.tile = parts[2]
            self.end = parts[3]
            self.wrong_format = False
        else:
            self.wrong_format = True

    def check_index(self, index):
        return self.index in index

    def check_date(self, startdate, enddate):
        return (self.date >= startdate and self.date < enddate)

    def check_tile(self, tilename):
        return self.tile == tilename
    
    def check_end(self):
        return self.end == "array"


    def check_file(self, index, startdate, enddate, tilename):
        if self.wrong_format:
            return False
        bool_index = self.check_index(index)
        bool_date = self.check_date(startdate, enddate)
        bool_tile = self.check_tile(tilename)
        bool_end = self.check_end()
        isWanted = (bool_index and bool_date and bool_tile and bool_end)
        return isWanted