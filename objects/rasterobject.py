"""

class for everyhing around the rasterdata

TODO:
    * hardcoded stuff in config
    * take care of 2017 naming and older
"""
import numpy as np
import glob
import os
import rasterio


class RasterObject(object):

    def __init__(self, inpath, resolution, band):
        self.inpath = inpath # to IMG
        self.bandfiles = self.get_bandfiles(resolution,band)
        self.affine = self.get_affine()
        self.epsg = self.get_epsg()

    def get_epsg(self):
        with rasterio.open(self.bandfiles[0]) as src:
            epsg = str(src.crs).split(':')[-1]
            #epsg = re.search(r'(?<=EPSG:)', str(src.crs)).group(0)
        return epsg

    def get_arrays(self):
        arrays= []
        for bandfile in self.bandfiles:
            with rasterio.open(bandfile) as f:
                myarray = np.array(f.read(1)).astype(float)
            arrays.append(myarray)
        return arrays

    def get_bandfiles(self, resolution, band):
        bandfiles = []
        for oneband in band:
            #print(os.path.join(os.path.join(self.inpath, 'R'+ str(resolution) + 'm'),'*'+oneband+'_' + str(resolution) +'m.jp2'))
            bandfile = glob.glob(os.path.join(os.path.join(self.inpath, 'R'+ str(resolution) + 'm'),'*'+oneband+'_' + str(resolution) +'m.jp2'))[0]
            bandfiles.append(bandfile)
        return bandfiles

    def get_affine(self):

        with rasterio.open(self.bandfiles[0]) as of:
            affine = of.transform
        return affine
        




    
