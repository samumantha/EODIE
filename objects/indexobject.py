"""
TODO:
    * hardcoded stuff in config
"""
import numpy as np
np.seterr(divide='ignore', invalid='ignore')
from rasterobject import RasterObject

class IndexObject(RasterObject):

    def __init__(self, inpath, resolution, band):
        super().__init__(inpath, resolution, band)
        self.indexarray = self.calculate_NDVI()

    def calculate_NDVI(self):

        bands= self.get_array()
        print(len(bands))
        red = bands[0]
        nir = bands[1]

        up = nir-red
        down = nir+red

        ndviarray = np.divide(up,down)
        
        return ndviarray


