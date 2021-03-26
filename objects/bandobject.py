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


class BandObject(object):

    def __init__(self, inpath):
        #self.bandfiles = self.get_bandfiles(resolution,band)
        #self.get_array()
        self.inpath = inpath
        self.get_affine()
        self.get_epsg()
        
        
    def get_bandfile(self, band, resolution):
        return glob.glob(os.path.join(os.path.join(self.inpath, 'R'+ str(resolution) + 'm'),'*'+band+'_' + str(resolution) +'m.jp2'))[0]

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
       
        
    """
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
    
    
    def get_bands(inpath):

    rpath = os.path.join(inpath, 'R10m')
    ajp2 = [jp2 for jp2 in os.listdir(rpath) if jp2.endswith('jp2')][0]
    #print(jp2)
    
    
    if re.search('2017\d\d\d\dT\d\d\d\d\d\d', ajp2): #its 2017 data
        namelist = ajp2.split('_')[:3]
    else:
        namelist = ajp2.split('_')[:2]
    name = '_'.join(namelist)
    #print(name)
    bands = ['B02','B03','B04','B08']
    banddict = {}

    for band in bands:
        bandname = os.path.join(rpath,name +'_'+ band +'_10m.jp2')
        if os.path.exists(bandname):
            banddict[band] = arrayrize(bandname)
        else:
            print('exit bandfile ' + band)
            sys.exit(0)
    
    return banddict
    """






    
