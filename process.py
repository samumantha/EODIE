import glob
import argparse
import re
import sys
import os
sys.path.append("./objects")
from extractor import Extractor
from cloudobject import CloudObject
from indexobject import IndexObject
from geometryobject import GeometryObject
from writerobject import WriterObject

#to test: python plan.py --dir /u/58/wittkes3/unix/Desktop/eodie_example/S2 --shp /u/58/wittkes3/unix/Desktop/eodie_example/shp/example_parcels --out ./results --id PlotID --stat 1

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
    
    cloudobject = CloudObject(imgpath,20,['SCL'])
    cloudmask = cloudobject.create_cloudmask()
    print(cloudmask.shape)
    indexobject = IndexObject(imgpath,10,['B04','B08'])
    ndvi = indexobject.calculate_ndvi()
    print(ndvi.shape)

    tile = re.search(r'(?<=T)[0-9]{2}[A-Z]{3}',imgpath).group(0)
    print(tile)
    date = re.search(r'20[0-2][0-9][0-1][0-9][0-3][0-9]',imgpath).group(0)
    print(date)

    geoobject = GeometryObject(args.shpbase + '_' + tile +'.shp')

    geoobject.reproject_to_epsg(indexobject.epsg)
    shapefile = geoobject.geometries

    affine = indexobject.affine


    if int(args.stat) == 1: 
        print('stat')
        extractorobject = Extractor(cloudmask, ndvi, shapefile, args.idname,affine)
        extractedarray = extractorobject.extract_arrays_stat()
        writerobject = WriterObject(args.outpath, date, tile, extractedarray)
        extractorobject.extract_arrays_stat()
        writerobject.write_csv()

    elif int(args.stat) == 0:
        
        extractorobject = Extractor(cloudmask, ndvi, shapefile, args.idname,affine)
        extractedarray = extractorobject.extract_arrays()
        writerobject = WriterObject(args.outpath, date, tile, extractedarray)
        extractorobject.extract_arrays()
        writerobject.write_csv_arr()
    
