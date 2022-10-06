"""
author: Petteri Lehti

"""

import os

# Checks for a file if it has the wanted properties based on the input
class FileChecker(object):
    def __init__(self, filename):
        parts = filename.split("_")
        if (
            len(parts) == 4
        ):  # Assuming format index_date_tile_array, if other this needs changing.
            self.index = parts[0]
            self.date = parts[1]
            self.tile = parts[2]
            self.end = parts[3].split(".")[0]
            self.wrong_format = False
        else:
            self.wrong_format = True

    def check_index(self, index):
        if "all" in index:
            return True
        else:
            return self.index in index

    def check_date(self, startdate, enddate):
        return self.date >= startdate and self.date <= enddate
        # Note: startdate and enddate both included

    def check_tile(self, tiles):
        if "all" in tiles:
            return True
        else:
            return self.tile in tiles

    def check_end(self):
        return self.end == "array"

    def check_file(self, index, startdate, enddate, tiles):
        if self.wrong_format:
            return False
        bool_index = self.check_index(index)
        bool_date = self.check_date(startdate, enddate)
        bool_tile = self.check_tile(tiles)
        bool_end = self.check_end()
        isWanted = bool_index and bool_date and bool_tile and bool_end
        return isWanted
