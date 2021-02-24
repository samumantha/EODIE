"""
functions to create vi index, apply cloudmask to it and extract per polygon array

*called from process.py

author: Samantha Wittke, FGI

October 2020

"""
import os
import sys
import numpy as np
import glob
import rasterio
from rasterstats import zonal_stats
#np.set_printoptions(threshold=sys.maxsize)
import csv
#import constants as c
import re
#avoid error because of nan in index division
np.seterr(divide='ignore', invalid='ignore')


def arrayrize(inputpath):
    with rasterio.open(inputpath) as f:
        myarray = np.array(f.read(1))
    return myarray

def get_scl(inpath):
    
    #inpath is sth like: ~/Sentinel-2/S2A_MSIL2A_20171015T095031_N0205_R079_T34VFN_20171015T095028.SAFE/GRANULE/L2A_T34VFN_A012088_20171015T095028/IMG_DATA
    rpath = os.path.join(inpath, 'R20m')
    sclpath = glob.glob(os.path.join(rpath,'*SCL*'))[0]
    sclarray = arrayrize(sclpath)
    
    return sclarray

# one is cloud, 0 no cloud
    
def binarize_cloudmask(sclarray):
    # this also includes no data (scl=0) for eg half filled tiles and saturated and defective (scl=1)
    #cloudarray = np.where(sclarray == 9, 1,0 )
    mask = (sclarray == 9) | (sclarray == 8) | (sclarray == 3) | (sclarray == 10) | (sclarray == 0) | (sclarray == 1)
    newmask = np.logical_not(mask)
    cloudarray = np.full(sclarray.shape,1)
    cloudarray[newmask] = 0
    return cloudarray
    
#get bands needed for vi generation in native resolution (?)
    # get all bands or just needed?
    # all bands for now

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
    
#calculate ndvi

def calc_NDVI(banddict):


    #original dtype is uint16 (no negative values!)
    red = banddict['B04'].astype(float)
    nir = banddict['B08'].astype(float)

    up = nir -red
    down = nir + red

    #TODO: avoid div by 0!
    ndviarray = np.divide(up,down)
    
    return ndviarray
    
#resample cloudmask to index resolution

def resample_cloudmask(cloudarray):    
    
    #from 20m to 10m, one pixel becomes 4 with same value, overestimation better than under

    #print(cloudarray.size)
    #print(cloudarray.shape)
    rescloudarray = np.kron(cloudarray, np.ones((2,2),dtype=float))

    #print(rescloudarray.size)
    #print(rescloudarray.shape)

    return rescloudarray

#mask index

def mask_index(indexarray, cloudarray):

    
    maskedarray= np.ma.array(indexarray, mask = cloudarray, fill_value=-9999)    

    return maskedarray

#get georeference (from profile) from original file (in right resolution)

def get_affine(originalfile):

    with rasterio.open(originalfile) as of:
        affine = of.transform

    return affine

#extract array per field (zonal stats)

def extract_arrays(maskedarray, shapefile, affine,idname, stat):

    maskedarray = maskedarray.filled(-9999)
    a=zonal_stats(shapefile, maskedarray, stats=['mean', 'std', 'median'], band=1, geojson_out=True, all_touched=True, raster_out=True, affine=affine, nodata=-9999)
    extractedarrays = {}
    myarrays = []
    if stat == 0:
        for x in a:
            myarray = x['properties']['mini_raster_array']
            #x['properties']['mini_raster_nodata']
            #print(myarray)
            #myarray = myarray.filled(-9999)
            #print(myarray)
            #print(type(myarray))
            myid = [x['properties'][idname]]

            arr = myarray.tolist()
            #print(len(arr))
            #print(myid)
            myid.extend(arr)
            arr = myid
            #print(len(arr))
            myarrays.append(arr)
            #print(len(myarrays))
    
    
        return myarrays


    elif stat ==1:
    
        for x in a:
            #print(x['properties']['mini_raster_array'])
            mymean = x['properties']['mean']
            mystd = x['properties']['std']
            mymedian = x['properties']['median']
            #x['properties']['mini_raster_nodata']
            #print(myarray)
            #myarray = myarray.filled(-9999)
            #print(myarray)
            #print(type(myarray))

            myid = x['properties'][idname]

            mystats = [str(mymean), str(mystd),str(mymedian)]
            
            extractedarrays[myid] = mystats
    

        return extractedarrays
    
#save arrays into csv

def write_csv_arr(arrays,outpath):

    with open(outpath, "w") as f:
        writer = csv.writer(f)
        writer.writerows(arrays)

def write_csv(extractedarrays, outpath):
# this is writing the array in short rows, multiple lines? -> solve!

    with open(outpath, mode='a') as csv_file:
        csv_writer = csv.writer(csv_file, delimiter=',')
        for key in extractedarrays.keys():
            onerow = [key] + extractedarrays[key]
            csv_writer.writerow(onerow)

    """
    with open(outpath, 'a') as opencsv:
        for key in extractedarrays.keys():
            opencsv.write("%s,%s\n"%(key,','.join(extractedarrays[key])))
            #print(extractedarrays[key])
    """
    """
    with open(outpath, 'w') as fp:
        for key in extractedarrays.keys():
            writer = csv.writer(fp)
            writer.writerow(extractedarrays[key])
    """

def get_inputpaths(mydir):
    pattern = mydir + '/*/*/*/IMG_DATA'
    inputpaths = glob.glob(pattern,recursive=True)
    return inputpaths
