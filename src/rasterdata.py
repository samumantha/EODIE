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
import re
from rasterio.enums import Resampling

class RasterData(object):

    def __init__(self, inpath, configfile):
        with open(configfile, "r") as ymlfile:
            self.cfg = yaml.safe_load(ymlfile)
        self.inpath = inpath
        self.get_metadata()
        self.resamplingdict = {'bilinear': Resampling.bilinear, 'nearest': Resampling.nearest}

    def _resample(self, band, dtype='f4'):
        """ simple resample of input array, replacing one value with 4 times same value (eg for 20 -10 m pixelsize resampling)"""
        return np.kron(band, np.ones((2,2),dtype=dtype))
        
    def get_bandfile(self,bandname):
        """ get bandfile given a band name and config file, returns the inpath for anything that is not Sentinel-2 or Landat8 and ends with tif"""
        #print(self.cfg['platform'])
        print(bandname)
        
        pathbuildinglist = self.cfg['pathbuildinglist']

        pathbuildinglist = [bandname if item =='bandname' else item for item in pathbuildinglist ]
        # here we need to get either fitting or smallest
        print('bandname')
        print(bandname)
        #print(self.cfg[bandname])
        possible_pixelsizes = self.cfg[bandname]
        pixelsize = self.cfg['pixelsize']
        print(possible_pixelsizes)
        print(pixelsize)
        if pixelsize in possible_pixelsizes:
            pathbuildinglist = [str(pixelsize) if item =='pixelsize' else item for item in pathbuildinglist ]
            resolution = pixelsize
        else:
            resolution = str(min(self.cfg[bandname]))
            pathbuildinglist = [resolution if item =='pixelsize' else item for item in pathbuildinglist ]
            
        #S2 has extra resolution directories
        if self.cfg['platform'] == 's2':
            path = glob.glob(os.path.join(self.inpath, ''.join(pathbuildinglist)[0:4], ''.join(pathbuildinglist)[4:]))[0]
        else:
            path = glob.glob(os.path.join(self.inpath, ''.join(pathbuildinglist)))[0]

        print('done')
        return path, resolution
        
        """
        if self.cfg['platform'] == 's2':
            try:
                return glob.glob(os.path.join(self.inpath, 'R'+ str(self.cfg['pixelsize']) + 'm','*'+bandname+'_' + str(self.cfg['pixelsize']) +'m.jp2'))[0]
            except:
                #all bands exist in 20m (except for B08)
                if bandname == 'B08':
                    return glob.glob(os.path.join(self.inpath, 'R10m','*'+bandname+'_10m.jp2'))[0]
                else:
                    return glob.glob(os.path.join(self.inpath, 'R20m','*'+bandname+'_20m.jp2'))[0]
        elif self.cfg['platform'] == 'ls8':
            return glob.glob(os.path.join(self.inpath, '*'+ bandname+ '*' + '.tif'))[0]
        elif self.cfg['platform'] is None:
            if self.inpath.endswith('.tif'):
                return self.inpath
        """

    def get_metadata(self):
        """ get affine from red band file as representation for all"""
        bandfile, _ = self.get_bandfile(self.cfg['red'])
        with rasterio.open(bandfile) as src:
            self.crs = src.crs
            self.epsg = str(src.crs).split(':')[-1]
            self.affine = src.transform

    def read_array(self,bandfile, dtype = 'f4'):
        """ get array in given datatype according to bandname and configfile"""
        
        print('read array')
        print(bandfile)
        with rasterio.open(bandfile) as f:
            #return np.array(f.read(1)).astype(float)
            #for float 32
            return np.array(f.read(1)).astype(dtype)

    def ref_to_dn(self,array):
        return np.divide(array, self.cfg['quantification_value'])

    def get_array(self,band, resampling_method=None):
        print('band in array')
        print(band)
        if re.match(r'%s' % self.cfg['band_designation'], band):
            bandname = band
        else:
            bandname = self.cfg[band]
        bandfile, resolution = self.get_bandfile(bandname)
        resolution = int(resolution)
        resampling_method = resampling_method if resampling_method is not None else self.cfg['resampling_method']
        targetresolution = int(self.cfg['pixelsize'])
        scaling_factor = resolution/targetresolution
        if targetresolution > resolution:
            #downsampling
            array = self.resample(bandfile, scaling_factor, resampling_method)
        elif targetresolution < resolution:
            #upsampling
            array = self.resample(bandfile, scaling_factor, resampling_method)
        elif targetresolution == resolution:
            array = self.read_array(bandfile)
        return self.ref_to_dn(array)

    def resample(self, bandfile, scaling_factor, resampling_method):
        
        with rasterio.open(bandfile) as dataset:
            # resample data to target shape
            data = dataset.read(
                out_shape=(int(dataset.height * scaling_factor),
                    int(dataset.width * scaling_factor)
                ),
                resampling=self.resamplingdict[resampling_method]
            ).astype('f4')
            data = data.reshape(data.shape[1], data.shape[2])
        return data

"""
    def get_resampled_array(self, band, resolution, targetres, resampling_method=None):
        resampling_method = resampling_method if resampling_method is not None else self.cfg['resampling_method']
        upscale_factor = resolution/targetres
        band = self.get_bandfile(band)
        with rasterio.open(band) as dataset:
            # resample data to target shape
            data = dataset.read(
                out_shape=(int(dataset.height * upscale_factor),
                    int(dataset.width * upscale_factor)
                ),
                resampling=self.resamplingdict[resampling_method]
            ).astype('f4')
            data = data.reshape(data.shape[1], data.shape[2])
        return data
"""


       







    
