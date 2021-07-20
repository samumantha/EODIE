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
from rasterio.enums import Resampling


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
            #return np.array(f.read(1)).astype(float)
            #for float 32
            return np.array(f.read(1)).astype('f4')

    def get_resampled_array(self, band, resolution, targetres):
        upscale_factor = resolution/targetres
        with rasterio.open(self.get_bandfile(band, resolution)) as dataset:
        
            # resample data to target shape
            data = dataset.read(
                out_shape=(int(dataset.height * upscale_factor),
                    int(dataset.width * upscale_factor)
                ),
                resampling=Resampling.lanczos
            )

            data = data.reshape(data.shape[1], data.shape[2])
            return data.astype('f4')

        

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
       







    
