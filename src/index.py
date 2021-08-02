"""

class to calculate indices
returns an indexarray based on index input

TODO:
    * resample
    * significant numbers for mean

    
"""
import numpy as np
import re
np.seterr(divide='ignore', invalid='ignore')
from rasterdata import RasterData
import yaml

class Index(RasterData):

    def __init__(self, inpath, configfile):
        super().__init__(inpath,configfile)
        self.supportedindices = ['ndvi', 'rvi','savi','nbr','kndvi']

    def calculate_index(self, index):
        """ runs own class method based on index given """
        default = "Unavailable index"
        return getattr(self, 'calculate_' + index, lambda: default)()
        
    def calculate_ndvi(self):
        """ Calculates NDVI (Kriegler FJ, Malila WA, Nalepka RF, Richardson W (1969) Preprocessing transformations and their effect on multispectral recognition. Remote Sens Environ VI:97–132)
        from red and nir bands"""

        red = self.get_array('red')
        nir = self.get_array('nir')

        up = nir-red
        down = nir+red

        ndviarray = np.divide(up,down)
        
        return ndviarray

    def calculate_rvi(self):
        """ Calculates RVI (ref) from red and nir bands """


        red = self.get_array('red')
        nir = self.get_array('nir')

        rviarray = np.divide(nir,red)

        return rviarray

    def calculate_savi(self): 
        """ Calculates SAVI (ref) from red and nir bands with factors 1.5 and 0.5 """

        red = self.get_array('red')
        nir = self.get_array('nir')

        saviarray=np.divide(1.5*(nir-red),nir+red+0.5)

        return saviarray

    def calculate_nbr(self):
        """ Calculates NBR (ref) from nir and swir (resampled to 10 meter) bands """
        #(B08 - B12) / (B08 + B12)
        nir = self.get_array('nir')
        swir2 = self.get_array('swir2')
        #resample band 12 to 10m (original 20m), with all 4 10m cells having same value as one 20m cell
        swir2 = self._resample(swir2,'f4')

        up = nir - swir2
        down = nir + swir2

        nbrarray = np.divide(up,down)

        return nbrarray

    def calculate_kndvi(self):
        """ Calculates kNDVI (https://github.com/IPL-UV/kNDVI) from red and nir bands with sigma pixelwise calculation """

        red = self.get_array('red')
        nir = self.get_array('nir')
        
        #pixelwise sigma calculation
        sigma = 0.5*(nir + red)
        knr = np.exp(-(nir-red)**2/(2*sigma**2))
        kndvi = (1-knr)/(1+knr)

        return kndvi
   
    def mask_array(self, array,maskarray):
        """ creates a masked array from an array and a mask with fill value -99999 for masked out values ; e.g. masking out cloudpixels from indexarray"""
        
        return np.ma.array(array, mask = maskarray, fill_value=-99999)

    