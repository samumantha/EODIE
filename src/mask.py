"""

Class to create and adapt cloudmask array
    
"""
import numpy as np
import rasterio
from rasterdata import RasterData

class Mask(RasterData):
    """ Retrieving and transforming a cloudmask from Remote Sensing product or external
    Attributes
    -----------
    cloudmask: boolean/int numpy array
        external cloudmask array
    cfg: dict
        dictionary with configuration elements
    """

    def __init__(self,inpath: str, cfg:dict, test, external=None):
        """ Initializing the mask object

        Parameters
        -----------
        inpath: str
            Location and name of the raster bands of the product
        cfg: dict
            dictionary with configuration elements
        test: boolean
            If testing is performed
        external: str , optional
            location and name of the external cloudmask to be used

        """

        super().__init__(inpath,cfg, test)
        if external is not None:
            self.cloudmask = self.load_binary_mask(external)
        self.cfg = cfg
        self.testcount = 0

    def load_binary_mask(self,external):
        """ Loads an external mask that needs to be a rasterfile with one/True is cloud, 0/False no cloud, 
        with pixelsize as given in cfg and overlap exactly with the file to be masked 
        Parameters
        -----------
        external: str
            location and name of external cloudmask to be read
        Returns
        --------
        int numpy array
            array of the cloudmask
        """
        with rasterio.open(external) as f:
            return np.array(f.read(1)).astype(int)

    def binarize_cloudmask(self,sclarray):
        """ takes in an array with different cloud classes and binarizes it according to config file to True being the to be masked pixels (eg clouds) and False for pixels that are ok to use """
        bitmask = self.cfg['bitmask']
        print("bitmask: " + str(bitmask))
        tobemaskedlist = self.cfg['tobemaskedlist']
        print("tobemasked: " + str(tobemaskedlist))
        if not bitmask:
            mask = np.isin(sclarray, tobemaskedlist)
        else:
            print("Creating bitmask")
            print(sclarray.shape)
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
        """ creates a mask from a file with mask information (eg about cloudy pixels), 
        binarizes it, and resamples it to 10m pixel size 
        Returns
        --------
        cloudmask: boolean numpy array 
            array with invalid pixels marked as True/1 and correct 'pixelsize'

        """
        print("getting array")
        cloudarray= self.get_array('cloudfilename', 'nearest')
        print("binarizing cloudmask")
        cloudmask = self.binarize_cloudmask(cloudarray)

        return cloudmask


    def createbitmask(self, maskarr, tobemasked):
        return np.vectorize(lambda somearr: self.checkbits(somearr, tobemasked))(maskarr)
        #return np.array(list(map(lambda row: list(map(lambda pixel: self.checkbits(pixel, tobemasked), row)), maskarr)))
        
    def checkbits(self, data, tobemaskedlist):
        for bit in tobemaskedlist:
            if(bit == 2):
                self.testcount += 1
                #print(self.testcount/1000000)
            if bool(1 << bit & data):
                return 1
        return 0