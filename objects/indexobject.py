"""

class to calculate indices
returns an indexarray based on index input

TODO:
    * hardcoded stuff in config
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
        swir = self.get_array('B12',self.resolution)

        #resample band 12 to 10m (original 20m), with all 4 10m cells having same value as one 20m cell
        swir = np.kron(swir, np.ones((2,2),dtype=float))

        up = nir - swir
        down = nir + swir

        nbrarray = np.divide(up,down)

        return nbrarray

    def calculate_ndwi(self):
        #'NDWI':'(B3-B8)/(B3+B8)'
        print('index not yet implemented')

    def calculate_mndwi(self):
        #'MNDWI':'(B3 - B11)/(B3 + B11)'
        print('index not yet implemented')

    def calculate_msi(self):
        #'MSI':'B11 / B8'
        print('index not yet implemented')

    def calculate_ndbi(self):
        #'NDBI':'(B11 - B8)/(B11 + B8)'
        print('index not yet implemented')

    def calculate_evi(self):
        #'EVI':'2.5*(B8 - B4) / (B8 + 6*B4 - 7.5*B2 + 1)'
        print('index not yet implemented')

    def calculate_evi2(self):
        #'EVI2':'2.5 * (B8 - B4) / (B8 + 2.4 * B4 + 1)'
        print('index not yet implemented')

    def calculate_tcw(self):
        #'TCW': '0.1509 * B2 + 0.1973 * B3 + 0.3279 * B4 + 0.3406 * B8 + 0.7112 * B11 + 0.4572 * B12'
        print('index not yet implemented')

    def calculate_tcb(self):
        #'TCB': '0.3037 *B2 + 0.2793 * B3 + 0.4743 * B4 + 0.5585 * B8 + 0.5082 * B11 + 0.1863 * B12'
        print('index not yet implemented')

    def calculate_tcg(self):
        #'TCG' : '-0.2848 * B2 - 0.2435 * B3 - 0.5436 * B4 + 0.7243 * B8 + 0.0840 * B11 - 0.1800 * B12'
        print('index not yet implemented')

    def calculate_kndvi(self):
        #https://advances.sciencemag.org/content/advances/suppl/2021/02/22/7.9.eabc7447.DC1/abc7447_SM.pdf
        #https://advances.sciencemag.org/content/7/9/eabc7447
        #?
        red = self.get_array('B04',self.resolution)
        nir = self.get_array('B08',self.resolution)
        sigma = np.multiply(0.5,(nir + red))
        knr = np.exp(np.divide(-(nir-red)**2,(2*sigma**2)))
        kndvi = np.divide((1-knr),(1+knr))
        return kndvi

   
