"""

class to calculate indices
returns an indexarray based on index input
    
"""
import numpy as np
import re
np.seterr(divide='ignore', invalid='ignore')
from rasterdata import RasterData
import yaml

class Index(RasterData):

    """ Calculating vegetation indices from remote sensing raster products"""

    def __init__(self, inpath, configfile, test):

        """ Initializing the index object

        Parameters
        ----------
        inpath: str
            Path to the raster bands of the product
        configfile: str
            Path to the confoguration file with information about the data (platform)
        test: boolean
            If testing is performed

        Returns
        -------
        nothing

        """

        super().__init__(inpath,configfile,test)
        #self.quantification_value = self.cfg['quantification_value']
        self.resolution = self.cfg['pixelsize']
        self.supportedindices = ['ndvi', 'rvi','savi','nbr','kndvi', 'ndmi', 'mndwi', 'evi', 'evi2', 'dvi', 'cvi', 'mcari', 'ndi45', 'tctb', 'tctg', 'tctw', 'ndwi']
    
    def mask_array(self, array,maskarray):
        """ creates a masked array from an array and a mask with fill value -99999 for masked out values ; e.g. masking out cloudpixels from indexarray
        
        Parameters
        ----------

        Returns
        -------
        """

        masked = np.ma.array(array, mask = maskarray, fill_value=-99999)

        return masked
    
    def calculate_index(self, index):
        """ runs own class method based on index given """
        default = "Unavailable index"
        return getattr(self, 'calculate_' + index, lambda: default)()


    def norm_diff(self, a, b):
        return np.divide(a-b, a+b)
        
    def calculate_ndvi(self):
        """ Calculates NDVI (Kriegler FJ, Malila WA, Nalepka RF, Richardson W (1969) Preprocessing transformations and their effect on multispectral recognition. Remote Sens Environ VI:97–132)
        from red and nir bands"""

        red = self.get_array('red')
        nir = self.get_array('nir')

        ndviarray = self.norm_diff(nir, red)

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
        
        
        nbrarray = self.norm_diff(nir, swir2)

        return nbrarray

    def calculate_kndvi(self):
        """ Calculates kNDVI (https://github.com/IPL-UV/kNDVI) from red and nir bands with sigma pixelwise calculation """

        red = self.get_array('red')
        nir = self.get_array('nir')
        
        #pixelwise sigma calculation
        sigma = 0.5*(nir + red)
        knr = np.exp(-(nir-red)**2/(2*sigma**2))
        kndviarray = (1-knr)/(1+knr)

        return kndviarray

    def calculate_ndmi(self): # NDMI (moisture) as it is used by Wilson (2002) https://doi.org/10.1016/S0034-4257(01)00318-2
        #similar to the Gao (1996) NDWI, NOT McFeeters NDWI (1996) https://en.wikipedia.org/wiki/Normalized_difference_water_index
        nir = self.get_array('nir') # B8A would be more accurate for NDWI and would fit well w/ NDMI as well?
        swir1 = self.get_array('swir1')

        ndmiarray = self.norm_diff(nir, swir1)

        return ndmiarray

    def calculate_ndwi(self): # McFeeters NDWI https://doi.org/10.1080/01431169608948714
        green = self.get_array('green')
        nir = self.get_array('nir')

        ndwiarray = self.norm_diff(green, nir)
        return ndwiarray

    def calculate_mndwi(self): #https://doi.org/10.1080/01431160600589179
        green = self.get_array('green') # Modified from McFeeters NDWI
        swir1 = self.get_array('swir1') #mir, band11 for Sentinel-2

        mndwiarray = self.norm_diff(green, swir1)
        return mndwiarray

    def calculate_evi(self):                            # https://doi.org/10.3390/s7112636
        nir = self.get_array('nir')    # IDB used different bands, no idea why (B09, B05 and B01 respectively)
        red = self.get_array('red')
        blue = self.get_array('blue')

        L = 1
        C1 = 6
        C2 = 7.5
        G = 2.5

        num = nir - red
        denom = nir + C1 * red - C2 * blue + L
        eviarray = G * np.divide(num, denom)
        return eviarray

    def calculate_evi2(self): # Jiang, Huete, Didan & Miura (2008) https://doi.org/10.1016%2Fj.rse.2008.06.006
        nir = self.get_array('nir')
        red = self.get_array('red')

        L = 1
        C = 2.4
        G = 2.5

        num = nir-red
        denom = np.multiply(C, red) + nir + L
        evi2array = G * np.divide(num, denom)
        return evi2array

    def calculate_dvi(self):   #https://doi.org/10.1088/1742-6596/1003/1/012083
        nir = self.get_array('nir')
        red = self.get_array('red')

        dviarray = nir - red
        return dviarray

    def calculate_cvi(self): #https://doi.org/10.3390/rs9050405
        nir = self.get_array('nir')
        red = self.get_array('red')
        green = self.get_array('green')

        cviarray = np.divide(np.multiply(nir, red), green**2)
        return cviarray

    def calculate_mcari(self):  #https://doi.org/10.1016/S0034-4257(00)00113-9
        red = self.get_array('red')
        green = self.get_array('green')
        r_edge = self.get_array('r_edge')

        mcariarray = np.multiply(r_edge - red - 0.2 * (r_edge - green), np.divide(r_edge, red))
        return mcariarray

    def calculate_ndi45(self): #https://doi.org/10.1007/978-981-16-1086-8_1 
        nir = self.get_array('r_edge')
        red = self.get_array('red')

        ndi45array = self.norm_diff(nir, red)
        return ndi45array

    def calculate_tct(self, coeffs):    #https://doi.org/10.1109/JSTARS.2019.2938388
        blue = self.get_array('blue')
        green = self.get_array('green')
        red = self.get_array('red')
        nir = self.get_array('nir')
        swir1 = self.get_array('swir1')
        swir2 = self.get_array('swir1')
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
   


    