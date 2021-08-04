"""

class for everyhing around the rasterdata

"""

import glob
import os
import re

import numpy as np
import rasterio
import yaml
from rasterio.enums import Resampling

class RasterData(object):

    def __init__(self, inpath, configfile):
        with open(configfile, "r") as ymlfile:
            self.cfg = yaml.safe_load(ymlfile)
        self.inpath = inpath
        self.get_metadata()
        self.resamplingdict = { 'bilinear': Resampling.bilinear, 
                                'nearest': Resampling.nearest, 
                                'cubic': Resampling.cubic, 
                                'cubic_spline': Resampling.cubic_spline,
                                'lanczos': Resampling.lanczos, 
                                'average': Resampling.average, 
                                'mode': Resampling.mode, 
                                'gauss': Resampling.gauss
        } 

    def get_bandfile(self, bandname):
        """ get bandfile given a band name """

        pathbuildinglist = self.cfg['pathbuildinglist']

        pathbuildinglist = [bandname if item == 'bandname' else item for item in pathbuildinglist]

        possible_pixelsizes = self.cfg[bandname]
        pixelsize = self.cfg['pixelsize']

        if pixelsize in possible_pixelsizes:
            pathbuildinglist = [
                str(pixelsize) if item == 'pixelsize' else item for item in pathbuildinglist]
            resolution = pixelsize
        else:
            resolution = str(min(self.cfg[bandname]))
            pathbuildinglist = [resolution if item == 'pixelsize' else item for item in pathbuildinglist]

        # S2 has extra resolution directories
        if self.cfg['platform'] == 's2':
            path = glob.glob(os.path.join(self.inpath, ''.join(pathbuildinglist)[0:4], ''.join(pathbuildinglist)[4:]))[0]
        else:
            path = glob.glob(os.path.join(self.inpath, ''.join(pathbuildinglist)))[0]

        return path, resolution


    def get_metadata(self):
        """ get affine from red band file as representation for all"""

        bandfile, _ = self.get_bandfile(self.cfg['red'])
        with rasterio.open(bandfile) as src:
            self.crs = src.crs
            self.epsg = str(src.crs).split(':')[-1]
            self.affine = src.transform

    def read_array(self, bandfile):
        """ get array in given datatype according to bandname"""

        with rasterio.open(bandfile) as f:
            array = np.array(f.read(1))

            return array

    def dn_to_reflectance(self, array):
        reflectance = np.divide(array, self.cfg['quantification_value'])
        return reflectance

    def get_array(self, band, resampling_method=None):

        resampling_method = resampling_method if resampling_method is not None else self.cfg['resampling_method']

        if re.match(r'%s' % self.cfg['band_designation'], band):
            bandname = band
        else:
            bandname = self.cfg[band]
        bandfile, resolution = self.get_bandfile(bandname)
        resolution = int(resolution)
        targetresolution = int(self.cfg['pixelsize'])
        scaling_factor = resolution/targetresolution
        if targetresolution == resolution:
            array = self.read_array(bandfile)
        else:
            array = self.resample(bandfile, scaling_factor, resampling_method)

        if band == 'cloudfilename':
            return array
        else:
            return self.dn_to_reflectance(array)

    def resample(self, bandfile, scaling_factor, resampling_method):

        with rasterio.open(bandfile) as dataset:
            data = dataset.read(
                out_shape=(int(dataset.height * scaling_factor),
                           int(dataset.width * scaling_factor)
                           ),
                resampling=self.resamplingdict[resampling_method]
            )
            # above results in 3D data, reshape needed to get 2D data
            data = data.reshape(data.shape[1], data.shape[2])
            
        return data

