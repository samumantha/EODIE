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
from writer import WriterObject
from userinput import UserInput
import logging
from datetime import datetime 



#to test: python process.py --dir /u/58/wittkes3/unix/Desktop/eodie_example/S2 --shp /u/58/wittkes3/unix/Desktop/eodie_example/shp/example_parcels --out ./results --id PlotID --stat 1 --index ndvi

userinput = UserInput()

#setup logging 
logging.basicConfig(filename=os.path.join(userinput.outpath, datetime.now().strftime("%Y%m%d-%H%M%S") + '.log'), level=logging.INFO)

for path in glob.glob(os.path.join(userinput.mydir,'*.SAFE')):

    pathfinderobject = pathfinder.Pathfinder(path)
    logging.info('Imagepath is {}'.format(pathfinderobject.imgpath))
    logging.info('Tile is {}'.format(pathfinderobject.tile))
    logging.info('Date is {}'.format(pathfinderobject.date))

    if int(pathfinderobject.date) <= int(userinput.enddate) and int(pathfinderobject.date) >= int(userinput.startdate):
    
        cloudobject = CloudObject(pathfinderobject.imgpath)
        cloudmask = cloudobject.create_cloudmask()
        logging.info('Shape of cloudmask is {}'.format(cloudmask.shape))
        indexobject = IndexObject(pathfinderobject.imgpath,10)

        for index in userinput.indexlist:
            indexarray = indexobject.calculate_index(index)

            #ndvi = indexobject.calculate_ndvi()
            logging.info('Shape of cloudmask is {}'.format(indexarray.shape))

            geoobject = GeometryObject(userinput.shpbase + '_' + pathfinderobject.tile +'.shp')

            geoobject.reproject_to_epsg(indexobject.epsg)
            shapefile = geoobject.geometries

            affine = indexobject.affine


            if int(userinput.stat) == 1: 
                logging.info('Statistics: {}'.format(pathfinderobject.tile))
                extractorobject = Extractor(cloudmask, indexarray, shapefile, userinput.idname,affine, userinput.statistics)
                extractedarray = extractorobject.extract_arrays_stat()
                writerobject = WriterObject(userinput.outpath, pathfinderobject.date, pathfinderobject.tile, extractedarray, index, userinput.statistics)
                extractorobject.extract_arrays_stat()
                writerobject.write_csv()
                

            elif int(userinput.stat) == 0:
                
                extractorobject = Extractor(cloudmask, indexarray, shapefile, userinput.idname,affine,['count'])
                extractedarray = extractorobject.extract_arrays()
                writerobject = WriterObject(userinput.outpath, pathfinderobject.date, pathfinderobject.tile, extractedarray, index, ['array'])
                extractorobject.extract_arrays()
                #writerobject.write_csv_arr()
                writerobject.write_pickle_arr()
        
