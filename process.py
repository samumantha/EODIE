"""

script to extract NDVI timeseries from S2 images (all in a directory are processed)
cmdline arguments
1. mydir :directory with data
2. shpbase: so path to shapefile and general name without tilename and '.shp' extension
3. outpath: path to dir where output products will be stored
4. idname: Name of the ID field in shapefile

author: Samantha Wittke, FGI

Oct 2020
"""

import os
import sys
import glob
#import myfuncs
import myfuncs_10m as myfuncs
# sincce shapeobject is in parent dir
#sys.path.insert(0,'..')
import shapeobject
import csv
import argparse
import re

"""
mydir = '/home/ubuntu/data/l2a'
shpbase = '/home/ubuntu/data/seedling_pertile_9m/SeedlingPlots_2017_2018_ID_9m_'
outpath = '/home/ubuntu/data/seedling_missing'
idname = 'LOHKO'
"""

parser = argparse.ArgumentParser()
parser.add_argument('--dir', dest='mydir', help='directory where S2 data is stored')
parser.add_argument('--shp', dest='shpbase', help='name of the shapefile (without extension)')
parser.add_argument('--out', dest='outpath', help='directory where results shall be saved')
parser.add_argument('--id', dest='idname', help='name of ID field in shapefile')
parser.add_argument('--stat', dest='stat',default='1',help='1 for statistics, 0 for full array')
args = parser.parse_args()

patternimg = args.mydir + '/*/*/*/IMG_DATA/'

print('INFO: Process start of directory ' + args.mydir + ' and shapefile ' + args.shpbase)

for myfile in glob.glob(patternimg):
    # pattern to find one 10m band as reference
    pattern= myfile + '/*10*/*B04*.jp2'

    if len(glob.glob(pattern)) > 0: 

        one10mfile = glob.glob(pattern)[0]
        #print(one10mfile)

        affine10m = myfuncs.get_affine(one10mfile)
        print('INFO: Got geoinfo')

        if re.search('2017\d\d\d\dT\d\d\d\d\d\d', one10mfile):
            tile = os.path.split(one10mfile)[-1].split('_')[1][1:]
            date = os.path.split(one10mfile)[-1].split('_')[2][0:8]
        elif re.search('2016\d\d\d\dT\d\d\d\d\d\d', one10mfile) or re.search('2015\d\d\d\dT\d\d\d\d\d\d', one10mfile):
            print('ERROR: only data starting from 2017 can be handled at the moment')
            sys.exit(0)
        else:
            tile = os.path.split(one10mfile)[-1].split('_')[0][1:]
            date = os.path.split(one10mfile)[-1].split('_')[1][0:8]
        

        outnamendvi = os.path.join(args.outpath ,'ndvi_statistics_' + date +'_'+ tile + '.csv')

        
        #print(myfile)
        scl = myfuncs.get_scl(myfile)
        print('INFO: Got cloudmask')
        binscl = myfuncs.binarize_cloudmask(scl)
        resbinscl = myfuncs.resample_cloudmask(binscl)
        print('INFO: Cloudmask now binary and resampled')

        bands10m = myfuncs.get_bands(myfile)

        print('INFO: Got bands')

        ndvi = myfuncs.calc_NDVI(bands10m)

        print('INFO: NDVI done')

        maskedndvi = myfuncs.mask_index(ndvi,resbinscl)

        resbincl = None
        binscl = None
        ndvi = None
        print('INFO: Masking done')

        inputshp = args.shpbase +'_' +  tile + '.shp'
        if not os.path.isfile(inputshp):
            print('ERROR: ' + inputshp + ' does not exist, check spelling!')
            sys.exit(0)
        inputshp = shapeobject.ShapeObject(inputshp).checkProjection(one10mfile).theshape
        #print(inputshp)

        #extrarrndvi = myfuncs.extract_arrays(ndvi, inputshp,affine10m)
        extrarrndvi = myfuncs.extract_arrays(maskedndvi, inputshp, affine10m, args.idname, int(args.stat))
        print(extrarrndvi)
        maskedndvi = None
        
        if int(args.stat) == 1:
            with open(outnamendvi, 'w', newline='') as opencsv:
                writer = csv.writer(opencsv)
                writer.writerow([args.idname, "mean", "std","median"])

            myfuncs.write_csv(extrarrndvi,outnamendvi)
        elif int(args.stat) == 0:
            myfuncs.write_csv_arr(extrarrndvi,outnamendvi)

        print('INFO: DONE, you can find the files here: ' + args.outpath)


#L2A/S2A_MSIL2A_20170528T095031_N0205_R079_T34VEQ_20170528T095032.SAFE/GRANULE/L2A_T34VEQ_A010086_20170528T095032/IMG_DATA/R10m/L2A_T34VEQ_20170528T095031_B04_10m.jp2
#S2A_MSIL2A_20180601T102021_N0208_R065_T34VEQ_20180601T132906.SAFE/GRANULE/L2A_T34VEQ_A015363_20180601T102024/IMG_DATA/R10m/T34VEQ_20180601T102021_B04_10m.jp2



