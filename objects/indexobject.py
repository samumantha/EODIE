"""

class to calculate indices

TODO:
    * hardcoded stuff in config
    * more indices
"""
import numpy as np
np.seterr(divide='ignore', invalid='ignore')
from bandobject import BandObject

class IndexObject(BandObject):

    def __init__(self, inpath, resolution):
        super().__init__(inpath)
        self.resolution = resolution 
        

    def calculate_ndvi(self):

        red = self.get_array('B04',self.resolution)
        nir = self.get_array('B08',self.resolution)
        #bands= self.get_arrays()
        #print(len(bands))
        #red = bands[0]
        #nir = bands[1]

        up = nir-red
        down = nir+red

        ndviarray = np.divide(up,down)
        
        return ndviarray

    def calculate_rvi(self):

        red = self.get_array('B04',self.resolution)
        nir = self.get_array('B08',self.resolution)

        rviarray = np.divide(nir,red)

        return rviarray

    def calculate_savi(self): 

        red = self.get_array('B04',self.resolution)
        nir = self.get_array('B08',self.resolution)

        saviarray=np.divide(1.5*(nir-red),nir+red+0.5)

        return saviarray

    def calculate_nbr(self):
        #(B08 - B12) / (B08 + B12)
        nir = self.get_array('B08',self.resolution)
        swir = self.get_array('B12',self.resolution)

        #resample band 12 to 10m (original 20m), with all 4 10m cells having same value as one 20m cell
        swir = np.kron(swir, np.ones((2,2),dtype=float))

        up = nir - swir
        down = nir + swir

        nbrarray = np.divide(up,down)

        return nbrarray



