"""

Class to create and adapt cloudmask array.
    
Authors: Samantha Wittke, Petteri Lehti

"""
import numpy as np
import rasterio
from eodie.rasterdata import RasterData


class Mask(RasterData):
    """Retrieve and transform a cloudmask from Remote Sensing product or external source.

    Attributes
    -----------
    cloudmask: boolean/int numpy array
        external cloudmask array
    cfg: dict
        dictionary with configuration elements
    """

    def __init__(
        self, inpath: str, cfg: dict = "test_config.yml", test=False, external=None
    ):
        """Initialize the mask object.

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
        super().__init__(inpath, cfg, test)
        if external is not None:
            self.cloudmask = self.load_binary_mask(external)
        self.cfg = cfg

    def load_binary_mask(self, external):
        """Load an external mask that needs to be a rasterfile with one/True is cloud, 0/False no cloud, with pixelsize as given in cfg and overlap exactly with the file to be masked.
        
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

    def binarize_cloudmask(self, sclarray):
        """Take in an array with different cloud classes and binarizes it according to config file to True being the to be masked pixels (eg clouds) and False for pixels that are ok to use.
        
        Parameters
        -----------
        sclarray: numpy array
            array of cloudmask from remote sensing product
        Returns
        -------
        mask: boolean numpy array
            binarized cloudmask using to be masked values or bits from config
        """
        bitmask = self.cfg["bitmask"]
        tobemaskedlist = self.cfg["tobemaskedlist"]
        if not bitmask:
            mask = np.isin(sclarray, tobemaskedlist)
        else:
            mask = self.createbitmask(sclarray, tobemaskedlist)                 
        return mask

    def create_cloudmask(self):
        """Create a mask from a file with mask information (eg about cloudy pixels), binarizes it, and resamples it to 10m pixel size.

        Returns
        --------
        cloudmask: boolean numpy array
            array with invalid pixels marked as True/1 and correct 'pixelsize'

        """
        cloudarray = self.get_array("cloudfilename", "nearest")        
        cloudmask = self.binarize_cloudmask(cloudarray)

        return cloudmask

    def createbitmask(self, maskarr, tobemasked):
        """Create a bitmask.

        Parameters
        -----------
        maskarr: numpy array
            array of cloudmask from remote sensing product
        tobemasked: list
            list of bits to be masked
        Returns
        -------
        binary mask with clouds/invalid pixels true/1, others 0
        """
        return np.vectorize(lambda somearr: self.checkbits(somearr, tobemasked))(
            maskarr
        )

    def checkbits(self, data, tobemaskedlist):
        """Check bits if they should be masked.
        
        Parameters
        ----------
        data: numpy array or int
            data point
        tobemaskedlist: list
            bits that should be masked
        Returns
        --------
        boolean (1 for masked, 0 for not masked)
        """
        for bit in tobemaskedlist:
            if bool(1 << bit & data):
                return 1
        return 0
