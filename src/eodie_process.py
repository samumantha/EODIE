#!/usr/bin/env python

import glob
import argparse
import re
import sys
import os
from eodie.extractor import Extractor
from eodie.mask import Mask
from eodie.index import Index
from eodie.vectordata import VectorData
from eodie.pathfinder import Pathfinder
from eodie.rastervalidator_s2 import RasterValidatorS2
from eodie.writer import Writer
from eodie.userinput import UserInput
from eodie.splitshp import SplitshpObject
from eodie.rasterdata import RasterData
from eodie.validator import Validator
import logging
from datetime import datetime 


userinput = UserInput()
Validator(userinput)

cfg = userinput.config

#create results dir 
if not os.path.exists(userinput.outpath):
    os.mkdir(userinput.outpath)

shp_directory, shp_name = os.path.split(userinput.shpbase)

#setup logging for prints in file and stdout
if userinput.verbose:
    handlers= [logging.FileHandler(os.path.join(userinput.outpath, datetime.now().strftime("%Y%m%d-%H%M%S") + '.log')), logging.StreamHandler()]
    logging.basicConfig(level=logging.INFO, handlers = handlers)
else:
    logging.basicConfig(filename= os.path.join(userinput.outpath, datetime.now().strftime("%Y%m%d-%H%M%S") + '.log'),level=logging.INFO)

logging.info('All inputs for this process: '+ str(vars(userinput).items()))

if not userinput.exclude_splitshp:
    #Read userinput.shpbase and worldtiles, do splitshp_world, then splitshp_mp and give new shapefile(s?) to next step. Loop in case of many shapefiles?
    geoobject = VectorData(userinput.shpbase + '.shp')
    logging.info(' Checking vectorfile validity...')
    small_polygon_shapefile = geoobject.check_validity(userinput.drop_geom)      
    world_tiles = cfg['tileshp']+'.shp'
    fieldname = cfg['fieldname']
    shapesplitter = SplitshpObject(small_polygon_shapefile, world_tiles, shp_directory, fieldname)
    shapesplitter.splitshp()
    # Check if user limited the tiles to be processed
    if userinput.tiles is not None:
        tiles = userinput.tiles
    else:
        tiles = shapesplitter.tiles
    shp_directory = os.path.join(shp_directory, 'EODIE_temp_shp')
    baseshapename = shapesplitter.basename       
else:
    baseshapename = userinput.shpbase

#running through either one file, if file was given or multiple files if dir was given
for path in userinput.input:

    pathfinderobject = Pathfinder(path, cfg)
    if tiles is None:
        tiles = pathfinderobject.tile

    if userinput.platform == 'tif':
        logging.info('File to be processed {}'.format(path))
        raster = RasterData(path,cfg)
        geoobject = VectorData(baseshapename + '.shp')
        geoobject.reproject_to_epsg(raster.epsg)
        extractorobject = Extractor(path, geoobject.geometries, userinput.idname, raster.affine, userinput.statistics ,userinput.exclude_border)
        
        for format in userinput.format:
            extractedarray = extractorobject.extract_format(format)
            writerobject = Writer(userinput.outpath, pathfinderobject.date, pathfinderobject.tile, extractedarray, cfg['name'], userinput.statistics, raster.crs)
            writerobject.write_format(format)
    else:
        if pathfinderobject.tile in tiles:
            logging.info('Imagepath is {}'.format(pathfinderobject.imgpath))
            logging.info('Tile is {}'.format(pathfinderobject.tile))
            logging.info('Date is {}'.format(pathfinderobject.date))

        if int(pathfinderobject.date) <= int(userinput.enddate) and int(pathfinderobject.date) >= int(userinput.startdate) and pathfinderobject.tile in tiles:

            if not userinput.nomask:
        
                if userinput.extmask is None:
                    mask = Mask(pathfinderobject.imgpath, cfg, userinput.test)
                    cloudmask = mask.create_cloudmask()
                
                else:
                    cname = userinput.extmask + '_'+ pathfinderobject.date +'_'+ pathfinderobject.tile+ '.*'
                    extmask = glob.glob(cname)[0]
                    cloudmask = Mask(pathfinderobject.imgpath, cfg, userinput.test, extmask).cloudmask
                    logging.info('Using external cloudmask {}'.format(extmask))
                    
                logging.info('Shape of cloudmask is {}'.format(cloudmask.shape))

            vegindex = Index(pathfinderobject.imgpath,cfg)

            shpname = baseshapename + '_' + pathfinderobject.tile + '.shp'

            geoobject = VectorData(os.path.join(shp_directory,shpname))
            geoobject.reproject_to_epsg(vegindex.epsg)

            shapefile = geoobject.geometries

            maxcloudcover = cfg['maxcloudcover']
            if userinput.platform == 's2':
                rastervalidatorobject = RasterValidatorS2(path, maxcloudcover, geoobject)
                logging.info('Cloudcover below {}: {}'.format(maxcloudcover, rastervalidatorobject.not_cloudcovered))
                logging.info('Data withing area of interest: {}'.format(rastervalidatorobject.datacovered))
                not_cloudcovered = rastervalidatorobject.not_cloudcovered
                datacovered = rastervalidatorobject.datacovered
            else:
                not_cloudcovered = True
                datacovered = True
            
            if not_cloudcovered and datacovered:
                logging.info(' LOOPING THROUGH GIVEN INDICES')
                for index in userinput.indexlist:

                    if re.match(cfg['band_designation'], index):
                        array = vegindex.get_array(index)
                    else:
                        array = vegindex.calculate_index(index)
                    
                    # If user input --no_cloudmask was used, do not apply cloudmask:
                    if userinput.nomask: 
                        logging.info(" Cloudmask will not be applied as input --no_cloudmask was entered.")
                        affine = vegindex.affine
                        extractorobject = Extractor(array, shapefile, userinput.idname, affine, userinput.statistics, userinput.exclude_border)                    
                    else:
                        logging.info(' Applying cloudmask...')
                        masked_array = vegindex.mask_array(array,cloudmask)
                        affine = vegindex.affine
                        extractorobject = Extractor(masked_array, shapefile, userinput.idname,affine, userinput.statistics,userinput.exclude_border)
                    
                    logging.info(' Writing results...')
                    for format in userinput.format:
                        extractedarray = extractorobject.extract_format(format)
                        writerobject = Writer(userinput.outpath, pathfinderobject.date, pathfinderobject.tile, extractedarray, index, userinput.statistics, vegindex.crs)
                        writerobject.write_format(format)
                        
                if 'array' in userinput.format:
                    lookup_file = cfg['lookup']
                    writerobject.write_lookup(lookup_file, shapefile, userinput.idname)
                   
            else:
                logging.warning('Cloudcovered or no data in Area of interest!')


if not userinput.exclude_splitshp:
    if not userinput.keep_shp: 
        shapesplitter.delete_splitted_files()
