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

    def __init__(self, inpath, resolution, quantification_value):
        super().__init__(inpath)
        self.resolution = resolution 
        self.quantification_value = quantification_value
        self.supportedindices = ['ndvi', 'rvi','savi','nbr','kndvi', 'ndmi', 'mndwi', 'evi', 'evi2', 'dvi', 'cvi', 'mcari', 'ndi45m']

    def get_band(self, band, resolution):
        return np.divide(self.get_array(band, max(resolution, self.resolution)), self.quantification_value)

    def norm_diff(self, a, b):
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

        red = self.get_band('B04',self.resolution)
        nir = self.get_band('B08',self.resolution)

        ndviarray = self.norm_diff(nir, red)
        
        return ndviarray

    def calculate_rvi(self):

        red = self.get_band('B04',self.resolution)
        nir = self.get_band('B08',self.resolution)

        rviarray = np.divide(nir,red)

        return rviarray

    def calculate_savi(self): 

        red = self.get_band('B04',self.resolution)
        nir = self.get_band('B08',self.resolution)

        saviarray=np.divide(1.5*(nir-red),nir+red+0.5)

        return saviarray

    def calculate_nbr(self):
        #(B08 - B12) / (B08 + B12)
        nir = self.get_band('B08',self.resolution)
        swir = self.get_band('B12',20)

        #resample band 12 to 10m (original 20m), with all 4 10m cells having same value as one 20m cell
        if not self.resolution == 20:
            swir = np.kron(swir, np.ones((2,2),dtype=float))

        up = nir - swir
        down = nir + swir

        nbrarray = np.divide(up,down)

        return nbrarray

    def calculate_kndvi(self):
        # according to https://github.com/IPL-UV/kNDVI

        red = self.get_band('B04',self.resolution)
        nir = self.get_band('B08',self.resolution)
        
        #pixelwise sigma calculation
        sigma = 0.5*(nir + red)
        knr = np.exp(-(nir-red)**2/(2*sigma**2))
        kndvi = (1-knr)/(1+knr)

        return kndvi


    def calculate_ndmi(self): # NDMI (moisture) as it is used by Wilson (2002) similar to the Gao (1996) NDWI, NOT McFeeters NDWI (1996) https://en.wikipedia.org/wiki/Normalized_difference_water_index
        nir = self.get_band('B08', self.resolution) # B8A would be more accurate for NDWI and would fit well w/ NDMI as well?
        swir = self.get_band('B11', 20)

        swir = self.resample(swir, 20)

        ndmi = self.norm_diff(nir, swir)

        return ndmi

    def calculate_mndwi(self): #https://d1wqtxts1xzle7.cloudfront.net/47301066/Modification_of_normalised_difference_water_index_NDWI_to_enhance_openwater_features_in_remotely_sensed_imagery_1-with-cover-page-v2.pdf?Expires=1626274448&Signature=Ui~MJhkT2CLPYTzDsM-xOWcf7VKsMQTn16NXkNiqtTseHecbvqtWFYCeJ~UWFOZZwRwpnMS0yHQN3PdRIM29HwGeThyJnagpLBcLkveIok7nXgfieSclMUKmh7KHgtU2-294dC9nHyoZ40wr~kn71sZkGfb2ckvY3CzZ7s0JNlmGKVNA0A~C9bvTjPW4kOTDjjrriq7N3f9wZlW3Nfa8T0V0CP5o-0zEo6-a-s4bon~AdX7OhLe-rG6-cIdrfRtLDAr2x0L9jJXSNWe58P~~pz4Dm3OWJDpN6D7YmUELUyx-2PI--ql-r4Dr8~Y4EXxi-s-smRwaWsCFCyxeiMMpww__&Key-Pair-Id=APKAJLOHF5GGSLRBV4ZA
        green = self.get_band('B03', self.resolution) # Modified from McFeeters NDWI
        mir = self.get_band('B11', 20)

        mir = self.resample(mir, 20)

        mndwi = self.norm_diff(green, mir)
        return mndwi



    def calculate_evi(self):                            # https://www.ncbi.nlm.nih.gov/pmc/articles/PMC3965234/
        nir = self.get_band('B08', self.resolution)    # IDB used different bands, no idea why (B09, B05 and B01 respectively)
        red = self.get_band('B04', self.resolution)
        blue = self.get_band('B02', self.resolution)

        L = 1
        C1 = 6
        C2 = 7.5
        G = 2.5

        num = nir - red
        denom = nir + C1 * red - C2 * blue + L
        evi = G * np.divide(num, denom)
        return evi

    def calculate_evi2(self): # Jiang, Huete, Didan & Miura (2008) https://doi.org/10.1016%2Fj.rse.2008.06.006
        nir = self.get_band('B08', self.resolution)
        red = self.get_band('B04', self.resolution)

        L = 1
        C = 2.4
        G = 2.5

        num = nir-red
        denom = np.multiply(nir + C, red) + L
        evi2 = G * np.divide(num, denom)
        return evi2

    def calculate_dvi(self):   #https://iopscience.iop.org/article/10.1088/1742-6596/1003/1/012083/pdf
        nir = self.get_band('B08', self.resolution)
        red = self.get_band('B04', self.resolution)

        dvi = nir - red
        return dvi

    def calculate_cvi(self): #https://doi.org/10.3390/rs9050405
        nir = self.get_band('B08', self.resolution)
        red = self.get_band('B04', self.resolution)
        green = self.get_band('B03', self.resolution)

        cvi = np.divide(np.multiply(nir, red), green**2)
        return cvi

    def calculate_mcari(self):
        red = self.get_band('B04', self.resolution)
        green = self.get_band('B03', self.resolution)
        r_edge = self.get_band('B05', 20)

        r_edge = self.resample(r_edge, 20)

        mcari = np.multiply(r_edge - red - 0.2 * (r_edge - green), np.divide(r_edge, red))
        return mcari

    def calculate_ndi45m(self): #https://www.researchgate.net/profile/Praveen-Kumar-221/publication/350389170_An_Approach_for_Fraction_of_Vegetation_Cover_Estimation_in_Forest_Above-Ground_Biomass_Assessment_Using_Sentinel-2_Images/links/6064149b299bf173677ddd9a/An-Approach-for-Fraction-of-Vegetation-Cover-Estimation-in-Forest-Above-Ground-Biomass-Assessment-Using-Sentinel-2-Images.pdf
        nir = self.get_band('B05', 20)
        red = self.get_band('B04', self.resolution)

        nir = self.resample(nir, 20)

        ndi45m = self.norm_diff(nir, red)
        return ndi45m