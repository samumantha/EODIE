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
        self.supportedindices = ['ndvi', 'rvi','savi','nbr','kndvi'] #Add ppi when ready

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

    '''
    def calculate_ppi(self):
        red = self.get_array('B04',self.resolution)
        nir = self.get_array('B08',self.resolution)
        angles = self.get_array('sunZenithAngles', self.resolution) #sun zenith angles in degrees (valus of 15-80)
        G = 0.5 #Valid for needle- and flat leafs when assuming spherical leaf angle distribution
        d_c = 0.0336+ np.divide(0.0477,np.cos(angles))
        Q_e = d_c + np.multiply((1-d_c), np.divide(G,np.cos(angles)))
        #DVI_max =  #??? Estimated individually for each pixel and no default value found
        DVI_soil = 0.09 #Value gotten by estimating 41 major soil types
        DVI = nir-red
        #K = np.multiply(np.divide(1,4*Q_e),np.divide(1+DVI_max,1-DVI_max))
        #PPI = np.multiply(K,np.log(np.divide(DVI_max-DVI,DVI_max-DVI_soil)))
        #return PPI
        #Code does not work because something wrong with angles. Get array probably not designed for this
        '''






        
        



        



