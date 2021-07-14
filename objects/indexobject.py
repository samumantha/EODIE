"""

class to calculate indices
returns an indexarray based on index input

TODO:
    * config update 
    * more indices
    * extract bands
    * resample
    * significant numbers for mean
    
"""
import numpy as np
import re
np.seterr(divide='ignore', invalid='ignore')
from bandobject import BandObject

class IndexObject(BandObject):

    def __init__(self, inpath, resolution):
        super().__init__(inpath)
        self.resolution = resolution 
        self.supportedindices = ['ndvi', 'rvi','savi','nbr','kndvi']

    def get_band(self, band):
        return self.get_array(band,self.resolution)

    def norm_diff(a, b):
        return np.divide(a-b, a+b)

    def resample(self, band, bandres):
        if self.resolution != bandres:
            a = bandres / self.resolution
            band = np.kron(band, np.ones((a,a),dtype=float))
        return band

    def calculate_index(self, index):
        """ runs own class method based on index given """
        default = "Unavailable index"
        return getattr(self, 'calculate_' + index, lambda: default)()
        

    def calculate_ndvi(self):

        red = self.get_array('B04',self.resolution)
        nir = self.get_array('B08',self.resolution)

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
        swir = self.get_array('B12',20)

        #resample band 12 to 10m (original 20m), with all 4 10m cells having same value as one 20m cell
        if not self.resolution == 20:
            swir = np.kron(swir, np.ones((2,2),dtype=float))

        up = nir - swir
        down = nir + swir

        nbrarray = np.divide(up,down)

        return nbrarray

    def calculate_kndvi(self):
        # according to https://github.com/IPL-UV/kNDVI

        red = self.get_array('B04',self.resolution)
        nir = self.get_array('B08',self.resolution)
        
        #pixelwise sigma calculation
        sigma = 0.5*(nir + red)
        knr = np.exp(-(nir-red)**2/(2*sigma**2))
        kndvi = (1-knr)/(1+knr)

        return kndvi


    def calculate_ndmi(self): # NDMI (moisture) as it is used by Wilson (2002) similar to the Gao (1996) NDWI, NOT McFeeters NDWI (1996) https://en.wikipedia.org/wiki/Normalized_difference_water_index
        nir = self.get_array('B08', self.resolution) # B8A would be more accurate for NDWI and would fit well w/ NDMI as well?
        swir = self.get_array('B11', 20)

        swir = self.resample(swir, 20)

        ndmi = self.norm_diff(nir, swir)

        return ndmi

    def calculate_mndwi(self): #https://d1wqtxts1xzle7.cloudfront.net/47301066/Modification_of_normalised_difference_water_index_NDWI_to_enhance_openwater_features_in_remotely_sensed_imagery_1-with-cover-page-v2.pdf?Expires=1626274448&Signature=Ui~MJhkT2CLPYTzDsM-xOWcf7VKsMQTn16NXkNiqtTseHecbvqtWFYCeJ~UWFOZZwRwpnMS0yHQN3PdRIM29HwGeThyJnagpLBcLkveIok7nXgfieSclMUKmh7KHgtU2-294dC9nHyoZ40wr~kn71sZkGfb2ckvY3CzZ7s0JNlmGKVNA0A~C9bvTjPW4kOTDjjrriq7N3f9wZlW3Nfa8T0V0CP5o-0zEo6-a-s4bon~AdX7OhLe-rG6-cIdrfRtLDAr2x0L9jJXSNWe58P~~pz4Dm3OWJDpN6D7YmUELUyx-2PI--ql-r4Dr8~Y4EXxi-s-smRwaWsCFCyxeiMMpww__&Key-Pair-Id=APKAJLOHF5GGSLRBV4ZA
        green = self.get_array('B03', self.resolution) # Modified from McFeeters NDWI
        mir = self.get_array('B11', 20)

        mir = self.resample(mir, 20)

        mndwi = self.norm_diff(green, mir)
        return mndwi



    def calculate_evi(self):                            # https://www.ncbi.nlm.nih.gov/pmc/articles/PMC3965234/
        nir = self.get_array('B08', self.resolution)    # IDB used different bands, no idea why (B09, B05 and B01 respectively)
        red = self.get_array('B04', self.resolution)
        blue = self.get_array('B02', self.resolution)

        L = 1
        C1 = 6
        C2 = 7.5
        G = 2.5

        num = nir - red
        denom = nir + C1 * red - C2 * blue + L
        evi = G * np.divide(num, denom)
        return evi

    def calculate_evi2(self): # Jiang, Huete, Didan & Miura (2008)
        nir = self.get_array('B08', self.resolution)
        red = self.get_array('B04', self.resolution)

        L = 1
        C = 2.4
        G = 2.5

        num = nir-red
        denom = nir + C * red + L
        evi2 = G * np.divide(num, denom)
        return evi2
