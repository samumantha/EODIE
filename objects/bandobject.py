"""

class for everyhing around the rasterdata

TODO:
    * hardcoded stuff in config
    * take care of 2017 naming and older
    * make S2 independent
"""
import numpy as np
import glob
import os
import rasterio


class BandObject(object):

    def __init__(self, inpath):
        #self.bandfiles = self.get_bandfiles(resolution,band)
        #self.get_array()
        self.inpath = inpath
        self.get_affine()
        self.get_epsg()
        
        
    def get_bandfile(self, band, resolution):
        return glob.glob(os.path.join(self.inpath, 'R'+ str(resolution) + 'm','*'+band+'_' + str(resolution) +'m.jp2'))[0]

    
    def get_array(self,band, resolution):
        
        with rasterio.open(self.get_bandfile(band, resolution)) as f:
            return np.array(f.read(1)).astype(float)
        

    def get_epsg(self):
        band = 'B04'
        resolution = 10
        with rasterio.open(self.get_bandfile(band, resolution)) as src:
            #return str(src.crs).split(':')[-1]
            #epsg = re.search(r'(?<=EPSG:)', str(src.crs)).group(0)
            self.epsg = str(src.crs).split(':')[-1]


    def get_affine(self):
        band = 'B04'
        resolution = 10
        with rasterio.open(self.get_bandfile(band, resolution)) as of:
            #return of.transform
            self.affine = of.transform
       







    
