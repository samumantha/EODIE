"""

Class to create and adapt cloudmask array
    
"""
import numpy as np
import rasterio
from rasterdata import RasterData
import yaml

class Mask(RasterData):

    def __init__(self,inpath, configfile, test, external=None):
        super().__init__(inpath,configfile, test)
        if external is not None:
            self.load_cloudmask(external)
        #loading config file
        with open(configfile, "r") as ymlfile:
            self.cfg = yaml.safe_load(ymlfile)

    def load_binary_mask(self,external):
        """ Loads an external mask that needs to be a rasterfile with pixelsize and overlap exactly with the file to be masked """
        with rasterio.open(external) as f:
            return np.array(f.read(1)).astype(int)

    def binarize_cloudmask(self,sclarray):
        """ takes in an array with different cloud classes and binarizes it according to config file to True being the to be masked pixels (eg clouds) and False for pixels that are ok to use """
        bitmask = self.cfg['bitmask']
        tobemaskedlist = self.cfg['tobemaskedlist']
        if not bitmask:
            mask = np.isin(sclarray, tobemaskedlist)
        else:
            mask = self.createbitmask(sclarray, tobemaskedlist)

        """
        # one is cloud, 0 no cloud
        newmask = np.logical_not(mask)
        cloudarray = np.full(sclarray.shape,1)
        cloudarray[newmask] = 0
        return cloudarray
        """
        return mask
        

    def create_cloudmask(self):
        """ creates a mask from a file with mask information (eg about cloudy pixels), binarizes it, and resamples it to 10m pixel size """

        cloudarray= self.get_array('cloudfilename', 'nearest')
        cloudmask = self.binarize_cloudmask(cloudarray)

        return cloudmask


    def createbitmask(self, maskarr, tobemasked):
        return np.array(list(map(lambda row: list(map(lambda pixel: self.checkbits(pixel, tobemasked), row)), maskarr)))
        
    def checkbits(data, tobemaskedlist):
        for bit in tobemaskedlist:
            if bool(1 << bit & data):
                return True
        return False