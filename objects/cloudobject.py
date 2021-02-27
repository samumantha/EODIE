"""
TODO:
    * hardcoded stuff in config
"""
import numpy as np

from rasterobject import RasterObject

class CloudObject(RasterObject):

    def __init__(self,inpath, resolution, band):
        super().__init__(inpath,resolution, band)
        print(self.get_array()[0])
        self.cloudmask = self.resample_cloudmask(self.binarize_cloudmask(self.get_array()[0]))

    def binarize_cloudmask(self,sclarray):
        # one is cloud, 0 no cloud
        # this also includes no data (scl=0) for eg half filled tiles and saturated and defective (scl=1)
        mask = (sclarray == 9) | (sclarray == 8) | (sclarray == 3) | (sclarray == 10) | (sclarray == 0) | (sclarray == 1)
        newmask = np.logical_not(mask)
        cloudarray = np.full(sclarray.shape,1)
        cloudarray[newmask] = 0
        return cloudarray

    def resample_cloudmask(self,cloudarray):     
        #from 20m to 10m, one pixel becomes 4 with same value
        return np.kron(cloudarray, np.ones((2,2),dtype=float))
