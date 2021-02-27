import glob
import argparse
import re
import sys
import os
sys.path.append("./objects")
from resultobject import ResultObject
from cloudobject import CloudObject
from indexobject import IndexObject
from geometryobject import GeometryObject


parser = argparse.ArgumentParser()
parser.add_argument('--dir', dest='mydir', help='directory where S2 data is stored')
parser.add_argument('--shp', dest='shpbase', help='name of the shapefile (without extension)')
parser.add_argument('--out', dest='outpath', help='directory where results shall be saved')
parser.add_argument('--id', dest='idname', help='name of ID field in shapefile')
parser.add_argument('--stat', dest='stat',default='1',help='1 for statistics, 0 for full array')
args = parser.parse_args()

for path in glob.glob(os.path.join(args.mydir,'*.SAFE')):
    patternimg = os.path.join(args.mydir ,'*','*','*','IMG_DATA')
    imgpath = glob.glob(patternimg)[0]
    print(imgpath)
    cloudarray = CloudObject(imgpath, 20, ['SCL']).cloudmask
    print(cloudarray.shape)
    ndviobject = IndexObject(imgpath, 10, ['B04','B08'])
    #ndviarray = ndviobject.indexarray
    #print(ndviarray.shape)

    tile = re.search(r'(?<=T)[0-9]{2}[A-Z]{3}',imgpath).group(0)
    print(tile)
    date = re.search(r'20[0-2][0-9][0-1][0-9][0-3][0-9]',imgpath).group(0)
    print(date)

    shapefile = GeometryObject(args.shpbase + '_' + tile +'.shp').reproject_to_epsg(ndviobject.epsg).geometries

    ResultObject(cloudarray, ndviobject, shapefile, args.outpath, date, tile,args.idname, args.stat)
