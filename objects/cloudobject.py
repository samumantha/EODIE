"""

Class to create and adapt cloudmask array

TODO:
    * hardcoded stuff in config
"""
import numpy as np

from bandobject import BandObject

class CloudObject(BandObject):

    def __init__(self,inpath):
        super().__init__(inpath)

    def binarize_cloudmask(self,sclarray):
        # one is cloud, 0 no cloud
        # this also includes no data (scl=0) for eg half filled tiles and saturated and defective (scl=1)
        mask = (sclarray == 9) | (sclarray == 8) | (sclarray == 3) | (sclarray == 10) | (sclarray == 0) | (sclarray == 1)
        newmask = np.logical_not(mask)
        cloudarray = np.full(sclarray.shape,1)
        cloudarray[newmask] = 0
        return cloudarray

    def test_binarize(self):
        inarray = np.array([[1,3,3,7,6,6,5,8,9][10,6,5,5,3,0,1,10,10]])
        binarray = self.binarize_cloudmask(inarray)
        rightarray = np.array([[1,1,1,1,0,0,0,0,1,1][1,0,0,0,1,1,1,1,1]])
        assert (binarray == rightarray).all(), 'Binarizing fails'


    def resample_cloudmask(self,cloudarray):     
        #from 20m to 10m, one pixel becomes 4 with same value
        return np.kron(cloudarray, np.ones((2,2),dtype=float))

    def test_resample(self):
        inarray = np.array([[0,1][1,0]])
        rightarray = np.array([[[0,0,1,1][0,0,1,1]][[1,1,0,0][1,1,0,0]]])
        resarray = self.resample_cloudmask(inarray)
        assert (resarray == rightarray).all(), 'Resampling fails'

    def create_cloudmask(self):
        cloudmask = self.resample_cloudmask(self.binarize_cloudmask(self.get_array('SCL', 20)))
        return cloudmask

