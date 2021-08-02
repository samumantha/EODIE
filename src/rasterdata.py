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
import yaml


class RasterData(object):

    def __init__(self, inpath, configfile):
        with open(configfile, "r") as ymlfile:
            self.cfg = yaml.safe_load(ymlfile)
        self.inpath = inpath
        self.get_metadata()

    def _resample(self, band, dtype='f4'):
        """ simple resample of input array, replacing one value with 4 times same value (eg for 20 -10 m pixelsize resampling)"""
        return np.kron(band, np.ones((2,2),dtype=dtype))
        
    def get_bandfile(self,bandname):
        """ get bandfile given a band name and config file, returns the inpath for anything that is not Sentinel-2 or Landat8 and ends with tif"""
        print(self.cfg['platform'])
        if self.cfg['platform'] == 's2':
            try:
                return glob.glob(os.path.join(self.inpath, 'R'+ str(self.cfg['pixelsize']) + 'm','*'+self.cfg[bandname]+'_' + str(self.cfg['pixelsize']) +'m.jp2'))[0]
            except:
                #all bands exist in 20m
                return glob.glob(os.path.join(self.inpath, 'R20m','*'+self.cfg[bandname]+'_20m.jp2'))[0]
        elif self.cfg['platform'] == 'ls8':
            return glob.glob(os.path.join(self.inpath, '*'+ self.cfg[bandname]+ '*' + '.tif'))[0]
        elif self.cfg['platform'] is None:
            if self.inpath.endswith('.tif'):
                return self.inpath

    def get_metadata(self):
        """ get affine from red band file as representation for all"""
        with rasterio.open(self.get_bandfile('red')) as src:
            self.epsg = str(src.crs).split(':')[-1]
            self.affine = src.transform

    def get_array(self,bandname, dtype = 'f4'):
        """ get array in given datatype according to bandname and configfile"""
        with rasterio.open(self.get_bandfile(bandname)) as f:
            #return np.array(f.read(1)).astype(float)
            #for float 32
            return np.array(f.read(1)).astype(dtype)
        

       







    
