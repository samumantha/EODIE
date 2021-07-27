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
        self.supportedindices = ['ndvi', 'rvi','savi','nbr','kndvi', 'ndmi', 'mndwi', 'evi', 'evi2', 'dvi', 'cvi', 'mcari', 'ndi45', 'tctb', 'tctg', 'tctw', 'ndwi']

    def get_band(self, band):
        if re.match('B0[2348]', band):
            bandres = 10
        elif re.match('B0[567]', band) or re.match('B1[12]', band) or band == 'B8A':
            bandres = 20
        else:
            bandres = 60
        try:
            array = np.divide(self.get_resampled_array(band, max(bandres, self.resolution), self.resolution), self.quantification_value)
        except IndexError:
            array =  np.divide(self.get_resampled_array(band, min(bandres, self.resolution), self.resolution), self.quantification_value)
        return array

    def norm_diff(self, a, b):
        return np.divide(a-b, a+b)


    def calculate_index(self, index):
        """ runs own class method based on index given """
        default = "Unavailable index"
        return getattr(self, 'calculate_' + index, lambda: default)()
        

    def calculate_ndvi(self):

        red = self.get_band('B04')
        nir = self.get_band('B08')

        ndviarray = self.norm_diff(nir, red)
        
        return ndviarray

    def calculate_rvi(self):

        red = self.get_band('B04')
        nir = self.get_band('B08')

        rviarray = np.divide(nir,red)

        return rviarray

    def calculate_savi(self): 

        red = self.get_band('B04')
        nir = self.get_band('B08')

        saviarray=np.divide(1.5*(nir-red),nir+red+0.5)

        return saviarray

    def calculate_nbr(self):
        #(B08 - B12) / (B08 + B12)
        nir = self.get_band('B08')
        swir = self.get_band('B12')

        nbrarray = self.norm_diff(nir, swir)

        return nbrarray

    def calculate_kndvi(self):
        # according to https://github.com/IPL-UV/kNDVI

        red = self.get_band('B04')
        nir = self.get_band('B08')
        
        #pixelwise sigma calculation
        sigma = 0.5*(nir + red)
        knr = np.exp(-(nir-red)**2/(2*sigma**2))
        kndviarray = (1-knr)/(1+knr)

        return kndviarray


    def calculate_ndmi(self): # NDMI (moisture) as it is used by Wilson (2002) https://doi.org/10.1016/S0034-4257(01)00318-2
        #similar to the Gao (1996) NDWI, NOT McFeeters NDWI (1996) https://en.wikipedia.org/wiki/Normalized_difference_water_index
        nir = self.get_band('B08') # B8A would be more accurate for NDWI and would fit well w/ NDMI as well?
        swir = self.get_band('B11')

        ndmiarray = self.norm_diff(nir, swir)

        return ndmiarray

    def calculate_ndwi(self): # McFeeters NDWI https://doi.org/10.1080/01431169608948714
        green = self.get_band('B03')
        nir = self.get_band('B08')

        ndwiarray = self.norm_diff(green, nir)
        return ndwiarray

    def calculate_mndwi(self): #https://doi.org/10.1080/01431160600589179
        green = self.get_band('B03') # Modified from McFeeters NDWI
        mir = self.get_band('B11')

        mndwiarray = self.norm_diff(green, mir)
        return mndwiarray



    def calculate_evi(self):                            # https://doi.org/10.3390/s7112636
        nir = self.get_band('B08')    # IDB used different bands, no idea why (B09, B05 and B01 respectively)
        red = self.get_band('B04')
        blue = self.get_band('B02')

        L = 1
        C1 = 6
        C2 = 7.5
        G = 2.5

        num = nir - red
        denom = nir + C1 * red - C2 * blue + L
        eviarray = G * np.divide(num, denom)
        return eviarray

    def calculate_evi2(self): # Jiang, Huete, Didan & Miura (2008) https://doi.org/10.1016%2Fj.rse.2008.06.006
        nir = self.get_band('B08')
        red = self.get_band('B04')

        L = 1
        C = 2.4
        G = 2.5

        num = nir-red
        denom = np.multiply(C, red) + nir + L
        evi2array = G * np.divide(num, denom)
        return evi2array

    def calculate_dvi(self):   #https://doi.org/10.1088/1742-6596/1003/1/012083
        nir = self.get_band('B08')
        red = self.get_band('B04')

        dviarray = nir - red
        return dviarray

    def calculate_cvi(self): #https://doi.org/10.3390/rs9050405
        nir = self.get_band('B08')
        red = self.get_band('B04')
        green = self.get_band('B03')

        cviarray = np.divide(np.multiply(nir, red), green**2)
        return cviarray

    def calculate_mcari(self):  #https://doi.org/10.1016/S0034-4257(00)00113-9
        red = self.get_band('B04')
        green = self.get_band('B03')
        r_edge = self.get_band('B05')

        mcariarray = np.multiply(r_edge - red - 0.2 * (r_edge - green), np.divide(r_edge, red))
        return mcariarray

    def calculate_ndi45(self): #https://doi.org/10.1007/978-981-16-1086-8_1 
        nir = self.get_band('B05')
        red = self.get_band('B04')

        ndi45array = self.norm_diff(nir, red)
        return ndi45array

    def calculate_tct(self, coeffs):    #https://doi.org/10.1109/JSTARS.2019.2938388
        blue = self.get_band('B02')
        green = self.get_band('B03')
        red = self.get_band('B04')
        nir = self.get_band('B08')
        swir1 = self.get_band('B11')
        swir2 = self.get_band('B12')
        bands = [blue, green, red, nir, swir1, swir2]
        weighted_bands = []
        for i in range(len(bands)):
            weighted_bands.append(np.multiply(coeffs[i], bands[i]))
        tctarray = sum(weighted_bands)
        return tctarray

    def calculate_tctb(self):
        coeffs = [0.3510, 0.3813, 0.3437, 0.7196, 0.2396, 0.1949]

        tctbarray = self.calculate_tct(coeffs)
        return tctbarray

    def calculate_tctg(self):
        coeffs = [-0.3599, -0.3533, -0.4734, 0.6633, 0.0087, -0.2856]
        
        tctgarray = self.calculate_tct(coeffs)
        return tctgarray

    def calculate_tctw(self):
        coeffs = [0.2578, 0.2305, 0.0883, 0.1071, -0.7611, -0.5308]
        
        tctwarray = self.calculate_tct(coeffs)
        return tctwarray


