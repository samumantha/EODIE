import glob
import argparse
import re
import sys
import os
import fiona
sys.path.append("./objects")
from extractor import Extractor
from cloudobject import CloudObject
from indexobject import IndexObject
from geometry import Geometry
from pathfinder import Pathfinder
from raster_validator import RasterValidator
from writer import WriterObject
from userinput import UserInput
from splitshp import SplitshpObject
import logging
from datetime import datetime 
import yaml
import fiona

#loading config file
with open("config.yml", "r") as ymlfile:
    cfg = yaml.safe_load(ymlfile)

userinput = UserInput()

#create results dir 
if not os.path.exists('./results'):
    os.mkdir('./results')

#setup logging 
logging.basicConfig(filename=os.path.join(userinput.outpath, datetime.now().strftime("%Y%m%d-%H%M%S") + '.log'), level=logging.INFO)


#Read userinput.shpbase and worldtiles, do splitshp_world, then splitshp_mp and give new shapefile(s?) to next step. Loop in case of many shapefiles?
small_polygon_shapefile = userinput.shpbase + '.shp'
shp_directory, shp_name = os.path.split(userinput.shpbase)
world_tiles = 'shp_preparation/sentinel2_tiles_world/sentinel2_tiles_world.shp'
shapesplitter = SplitshpObject(small_polygon_shapefile, world_tiles, shp_directory)
shapesplitter.splitshp()

#running through either one file, if file was given or multiple files if dir was given
for path in userinput.input:

    pathfinderobject = Pathfinder(path)
    
    logging.info('Imagepath is {}'.format(pathfinderobject.imgpath))
    logging.info('Tile is {}'.format(pathfinderobject.tile))
    logging.info('Date is {}'.format(pathfinderobject.date))

    if int(pathfinderobject.date) <= int(userinput.enddate) and int(pathfinderobject.date) >= int(userinput.startdate) and pathfinderobject.tile in shapesplitter.tiles:
    
        cloudobject = CloudObject(pathfinderobject.imgpath)
        cloudmask = cloudobject.create_cloudmask()
        logging.info('Shape of cloudmask is {}'.format(cloudmask.shape))
        indexobject = IndexObject(pathfinderobject.imgpath,cfg['resolution'])
<<<<<<< HEAD
        shpname = userinput.shpbase + '_' + pathfinderobject.tile +'.shp'
        geoobject = Geometry(shpname)
        geoobject.reproject_to_epsg(indexobject.epsg)
=======
        try:
            shpname = os.path.join(shapesplitter.output_directory, shp_name  + '_' + pathfinderobject.tile + '.shp')
            geoobject = Geometry(shpname)
            geoobject.reproject_to_epsg(indexobject.epsg)
        except FileNotFoundError:
            try:
                shpname = os.path.join(shapesplitter.output_directory, shp_name + '_reprojected_4326_' + pathfinderobject.tile + '.shp')
                geoobject = Geometry(shpname)
                geoobject.reproject_to_epsg(indexobject.epsg)
            except FileNotFoundError:
                continue
>>>>>>> c0cc517723357fbc6b3e53ec33401b5980eb8096
        shapefile = geoobject.geometries

        maxcloudcover = cfg['maxcloudcover']
        rastervalidatorobject = RasterValidator(path, maxcloudcover, geoobject)
        logging.info('Cloudcover below {}: {}'.format(maxcloudcover, rastervalidatorobject.cloudcovered))
        logging.info('Data withing area of interest: {}'.format(rastervalidatorobject.datacovered))
        
        if rastervalidatorobject.cloudcovered and rastervalidatorobject.datacovered:

            for index in userinput.indexlist:
                # check if bands are re
                if index in indexobject.supportedindices:
                    array = indexobject.calculate_index(index)
                elif re.match('B[0-1]\d', index) or index == 'B8A':
                    array = indexobject.get_band(index)
                else:
                    logging.warning('Chosen index {} not available, continuing with next index.'.format(index))
                    
                affine = indexobject.affine

                if int(userinput.stat) == 1: 
                    logging.info('Statistics: {}'.format(pathfinderobject.tile))
                    extractorobject = Extractor(cloudmask, array, shapefile, userinput.idname,affine, userinput.statistics)
                    extractedarray = extractorobject.extract_arrays_stat()
                    writerobject = WriterObject(userinput.outpath, pathfinderobject.date, pathfinderobject.tile, extractedarray, index, userinput.statistics)
                    extractorobject.extract_arrays_stat()
                    writerobject.write_csv()
                    

                elif int(userinput.stat) == 0:
                    
                    extractorobject = Extractor(cloudmask, array, shapefile, userinput.idname,affine,['count'])
                    extractedarray = extractorobject.extract_arrays()
                    writerobject = WriterObject(userinput.outpath, pathfinderobject.date, pathfinderobject.tile, extractedarray, index, ['array'])
                    extractorobject.extract_arrays()
                    writerobject.write_pickle_arr()

                    lookup_file = cfg['lookup']
                    writerobject.write_lookup(lookup_file, shpname, userinput.idname)
            
        else:
            logging.warning('Cloudcovered or no data in Area of interest!')

keep_shapes = cfg['keep_shapes'] 
if not keep_shapes: 
    shapesplitter.delete_splitted_files()
