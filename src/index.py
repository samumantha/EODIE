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
            Location and name of the raster bands of the product
        configfile: str
            Location and name of the configuration file with information about the data (platform)
        test: boolean
            If testing is performed

        """

        super().__init__(inpath,configfile,test)
        #self.quantification_value = self.cfg['quantification_value']
        self.resolution = self.cfg['pixelsize']
        self.supportedindices = ['ndvi', 'rvi','savi','nbr','kndvi', 'ndmi', 'mndwi', 'evi', 'evi2', 'dvi', 'cvi', 'mcari', 'ndi45', 'tctb', 'tctg', 'tctw', 'ndwi']
    
    def mask_array(self, array,maskarray):
        """ creates a masked array from an array and a mask with fill value -99999 for masked out values ; e.g. masking out cloudpixels from indexarray
        
        Parameters
        ----------
        array: float numpy array
            array to be masked
        maskarray: boolean/int numpy array
            array to be used as mask

        Returns
        -------
        masked: float masked numpy array
            masked numpy array with nan where mask was 'True'/1

        """

        masked = np.ma.array(array, mask = maskarray, fill_value=-99999)

        return masked
    
    def calculate_index(self, index):
        """ runs own class method based on index given 

        Parameters
        -----------
        index: str
            vegetation index to be calculated

        Returns
        --------
        nothing itself, but runs given index function which returns a numpy array of the calculated index 

        """

        default = "Unavailable index"
        return getattr(self, 'calculate_' + index, lambda: default)()


    def norm_diff(self, a:np.ndarray, b:np.ndarray) -> np.ndarray:
        """ normalized difference calculation
        Parameters
        -----------
        a: float numpy array
            array to be used as a in formula (a-b)/(a+b)
        b: float numpy array
            array to be used as b in formula (a-b)/(a+b)
            
        Returns
        --------
        normdiff: float numpy array
            normalized difference between a and b
         """

        normdiff = np.divide(a-b, a+b)
        return normdiff
        
    def calculate_ndvi(self):
        """ Calculates Normalized Difference Vegetation Index (NDVI) (Kriegler FJ, Malila WA, Nalepka RF, Richardson W (1969) Preprocessing transformations and their effect on multispectral recognition. Remote Sens Environ VI:97–132)
        from red and nir bands"""

        red = self.get_array('red')
        nir = self.get_array('nir')

        ndviarray = self.norm_diff(nir, red)

        return ndviarray

    def calculate_rvi(self):
        """ Calculates Ratio Vegetation Index (RVI) (ref) from red and nir bands """

        red = self.get_array('red')
        nir = self.get_array('nir')

        rviarray = np.divide(nir,red)

        return rviarray

    def calculate_savi(self): 
        """ Calculates Soil Adjusted Vegetation Index (SAVI) (ref) from red and nir bands with factors 1.5 and 0.5 """

        red = self.get_array('red')
        nir = self.get_array('nir')

        saviarray=np.divide(1.5*(nir-red),nir+red+0.5)

        return saviarray

    def calculate_nbr(self):
        """ Calculates Normalized Burnt Ratio (NBR) (ref) from nir and swir2 bands """
    
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

    def calculate_ndmi(self): 
        """ Calculates Normalized Moisture Index (NDMI)  as it is used by Wilson (2002) https://doi.org/10.1016/S0034-4257(01)00318-2
        similar to the Gao (1996) NDWI,  but NOT McFeeters NDWI (1996) https://en.wikipedia.org/wiki/Normalized_difference_water_index
        """

        nir = self.get_array('nir') # B8A would be more accurate for NDWI and would fit well w/ NDMI as well?
        swir1 = self.get_array('swir1')

        ndmiarray = self.norm_diff(nir, swir1)

        return ndmiarray

    def calculate_ndwi(self): 
        """ Calcultaes Normalized Difference Water Index according to McFeeters (1996) https://doi.org/10.1080/01431169608948714
        """

        green = self.get_array('green')
        nir = self.get_array('nir')

        ndwiarray = self.norm_diff(green, nir)
        return ndwiarray

    def calculate_mndwi(self): 
        """ Calculates Modified Normalized Difference Water Index (https://doi.org/10.1080/01431160600589179)
        """

        green = self.get_array('green') # Modified from McFeeters NDWI
        swir1 = self.get_array('swir1') #mir, band11 for Sentinel-2

        mndwiarray = self.norm_diff(green, swir1)
        return mndwiarray

    def calculate_evi(self):  
        """ Calculates Enhanced Vegetation Index (https://doi.org/10.3390/s7112636) 
        with L =1, C1 = 6, C2 = 7.5 and G= 2.5 """

        nir = self.get_array('nir')    
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

    def calculate_evi2(self): 
        """ Calculate Enhanced Vegetation Index 2 (Jiang, Huete, Didan & Miura (2008) https://doi.org/10.1016%2Fj.rse.2008.06.006)
        with L=1, C = 2.4, G=2.5
        """

        nir = self.get_array('nir')
        red = self.get_array('red')

        L = 1
        C = 2.4
        G = 2.5

        num = nir-red
        denom = np.multiply(C, red) + nir + L
        evi2array = G * np.divide(num, denom)
        return evi2array

    def calculate_dvi(self):   
        """ Calculates Difference Vegetation Index (https://doi.org/10.1088/1742-6596/1003/1/012083)
        """

        nir = self.get_array('nir')
        red = self.get_array('red')

        dviarray = nir - red
        return dviarray

    def calculate_cvi(self): 
        """ Calculates CVI (https://doi.org/10.3390/rs9050405)"""

        nir = self.get_array('nir')
        red = self.get_array('red')
        green = self.get_array('green')

        cviarray = np.divide(np.multiply(nir, red), green**2)
        return cviarray

    def calculate_mcari(self):  
        """ Calculates MCARI (https://doi.org/10.1016/S0034-4257(00)00113-9)
        only usable with platforms with bands in the red edge area (eg Sentinel-2) """

        red = self.get_array('red')
        green = self.get_array('green')
        r_edge = self.get_array('r_edge')

        mcariarray = np.multiply(r_edge - red - 0.2 * (r_edge - green), np.divide(r_edge, red))
        return mcariarray

    def calculate_ndi45(self): 
        """ Calculates NDI45 (https://doi.org/10.1007/978-981-16-1086-8_1 )
        only usable with platforms with bands in the red edge area (eg Sentinel-2) 
        """

        nir = self.get_array('r_edge')
        red = self.get_array('red')

        ndi45array = self.norm_diff(nir, red)
        return ndi45array

    def calculate_tct(self, coeffs):    
        """ Calculate general Tasseled Cap Index (https://doi.org/10.1109/JSTARS.2019.2938388)
        Parameters
        ----------
        coeffs: list of float
            coefficients to calculate spcific tasseled cap
        Returns
        -------
        tctarray: numpy array of float
            calculated tasseled cap array from coefficients 
        """

        blue = self.get_array('blue')
        green = self.get_array('green')
        red = self.get_array('red')
        nir = self.get_array('nir')
        swir1 = self.get_array('swir1')
        swir2 = self.get_array('swir2')
        bands = [blue, green, red, nir, swir1, swir2]
        weighted_bands = []
        for i in range(len(bands)):
            weighted_bands.append(np.multiply(coeffs[i], bands[i]))
        tctarray = sum(weighted_bands)
        return tctarray

    def calculate_tctb(self):
        """ Calculates Tasseled Cap Brightness
        coefficients only valid for Sentinel-2"""

        coeffs = [0.3510, 0.3813, 0.3437, 0.7196, 0.2396, 0.1949]

        tctbarray = self.calculate_tct(coeffs)
        return tctbarray

    def calculate_tctg(self):
        """ Calculates Tasseled Cap Greenness
        coefficients only valid for Sentinel-2"""
        coeffs = [-0.3599, -0.3533, -0.4734, 0.6633, 0.0087, -0.2856]
        
        tctgarray = self.calculate_tct(coeffs)
        return tctgarray

    def calculate_tctw(self):
        """ Calculates Tasseled Cap Wetness
        coefficients only valid for Sentinel-2"""
        coeffs = [0.2578, 0.2305, 0.0883, 0.1071, -0.7611, -0.5308]
        
        tctwarray = self.calculate_tct(coeffs)
        return tctwarray
   


    