import glob
import argparse
import re
import sys
import os
sys.path.append("./src")
from extractor import Extractor
from mask import Mask
from index import Index
from vectordata import VectorData
from pathfinder import Pathfinder
from rastervalidator_s2 import RasterValidatorS2
from writer import Writer
from userinput import UserInput
from splitshp import SplitshpObject
import logging
from datetime import datetime 
import yaml
import fiona


userinput = UserInput()

test = userinput.test

#loading config file
with open(userinput.configfile, "r") as ymlfile:
    cfg = yaml.safe_load(ymlfile)


#create results dir 
if not os.path.exists(userinput.outpath):
    os.mkdir(userinput.outpath)

#setup logging 
logging.basicConfig(filename=os.path.join(userinput.outpath, datetime.now().strftime("%Y%m%d-%H%M%S") + '.log'), level=logging.INFO)


#Read userinput.shpbase and worldtiles, do splitshp_world, then splitshp_mp and give new shapefile(s?) to next step. Loop in case of many shapefiles?
small_polygon_shapefile = userinput.shpbase + '.shp'
shp_directory, shp_name = os.path.split(userinput.shpbase)
world_tiles = cfg['tileshp']+'.shp'
fieldname = cfg['fieldname']
shapesplitter = SplitshpObject(small_polygon_shapefile, world_tiles, shp_directory, fieldname)
shapesplitter.splitshp()

#running through either one file, if file was given or multiple files if dir was given
for path in userinput.input:

    pathfinderobject = Pathfinder(path, userinput.configfile)
    
    logging.info('Imagepath is {}'.format(pathfinderobject.imgpath))
    logging.info('Tile is {}'.format(pathfinderobject.tile))
    logging.info('Date is {}'.format(pathfinderobject.date))

    if int(pathfinderobject.date) <= int(userinput.enddate) and int(pathfinderobject.date) >= int(userinput.startdate) and pathfinderobject.tile in shapesplitter.tiles:
    
        mask = Mask(pathfinderobject.imgpath, userinput.configfile, test)
        cloudmask = mask.create_cloudmask()
        logging.info('Shape of cloudmask is {}'.format(cloudmask.shape))

        vegindex = Index(pathfinderobject.imgpath,userinput.configfile, test)
        try:
            shp_str = os.path.join(shapesplitter.output_directory, shp_name  + '_' + pathfinderobject.tile + '.shp')
            geoobject = VectorData(shp_str)
            geoobject.reproject_to_epsg(vegindex.epsg)
        except FileNotFoundError:
            try:
                shp_str = os.path.join(shapesplitter.output_directory, shp_name + '_reprojected_4326_' + pathfinderobject.tile + '.shp')
                geoobject = VectorData(shp_str)
                geoobject.reproject_to_epsg(vegindex.epsg)
            except FileNotFoundError:
                continue

        shapefile = geoobject.geometries

        maxcloudcover = cfg['maxcloudcover']
        if userinput.platform == 's2':
            rastervalidatorobject = RasterValidatorS2(path, maxcloudcover, geoobject)
            logging.info('Cloudcover below {}: {}'.format(maxcloudcover, rastervalidatorobject.cloudcovered))
            logging.info('Data withing area of interest: {}'.format(rastervalidatorobject.datacovered))
        
        if rastervalidatorobject.cloudcovered and rastervalidatorobject.datacovered:

            for index in userinput.indexlist:
                if index in vegindex.supportedindices:
                    array = vegindex.calculate_index(index)
                elif re.match(cfg['band_designation'], index):
                    array = vegindex.get_array(index)
                else:
                    logging.warning('Chosen index {} not available, continuing with next index.'.format(index))

                
                masked_array= vegindex.mask_array(array,cloudmask)
                    
                affine = vegindex.affine

                if int(userinput.stat) == 1: 
                    logging.info('Statistics: {}'.format(pathfinderobject.tile))
                    extractorobject = Extractor(masked_array, shapefile, userinput.idname,affine, userinput.statistics)
                    extractedarray = extractorobject.extract_arrays_stat()
                    writerobject = Writer(userinput.outpath, pathfinderobject.date, pathfinderobject.tile, extractedarray, index, userinput.statistics)
                    writerobject.write_csv()
                    

                elif int(userinput.stat) == 0:
                    
                    extractorobject = Extractor(masked_array, shapefile, userinput.idname,affine,['count'])
                    if userinput.geotiff:
                        extractedarray = extractorobject.extract_array_geotiff()
                    else:
                        extractedarray = extractorobject.extract_arrays()

                    writerobject = Writer(userinput.outpath, pathfinderobject.date, pathfinderobject.tile, extractedarray, index, ['array'])

                    if userinput.geotiff:
                        writerobject.write_geotiff(geoobject.get_properties()[2]['init'])
                    else:
                        writerobject.write_pickle_arr()

            
        else:
            logging.warning('Cloudcovered or no data in Area of interest!')

if not userinput.keep_shp: 
    shapesplitter.delete_splitted_files()
