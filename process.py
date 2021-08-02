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
import logging
from datetime import datetime 
import yaml

userinput = UserInput()

#loading config file
with open(userinput.configfile, "r") as ymlfile:
    cfg = yaml.safe_load(ymlfile)

#create results dir 
if not os.path.exists(userinput.outpath):
    os.mkdir(userinput.outpath)

#setup logging 
logging.basicConfig(filename=os.path.join(userinput.outpath, datetime.now().strftime("%Y%m%d-%H%M%S") + '.log'), level=logging.INFO)

#running through either one file, if file was given or multiple files if dir was given
for path in userinput.input:

    pathfinderobject = Pathfinder(path, userinput.configfile)
    
    logging.info('Imagepath is {}'.format(pathfinderobject.imgpath))
    logging.info('Tile is {}'.format(pathfinderobject.tile))
    logging.info('Date is {}'.format(pathfinderobject.date))
    

    if int(pathfinderobject.date) <= int(userinput.enddate) and int(pathfinderobject.date) >= int(userinput.startdate):
    
        mask = Mask(pathfinderobject.imgpath, userinput.configfile)
        cloudmask = mask.create_cloudmask()
        logging.info('Shape of cloudmask is {}'.format(cloudmask.shape))
        vegindex = Index(pathfinderobject.imgpath,cfg['resolution'], cfg['quantification_value'])
        geoobject = VectorData(userinput.shpbase + '_' + pathfinderobject.tile +'.shp')
        geoobject.reproject_to_epsg(vegindex.epsg)
        shapefile = geoobject.geometries

        maxcloudcover = cfg['maxcloudcover']
        if userinput.platform == 's2':
            rastervalidatorobject = RasterValidatorS2(path, maxcloudcover, geoobject)
            logging.info('Cloudcover below {}: {}'.format(maxcloudcover, rastervalidatorobject.cloudcovered))
            logging.info('Data withing area of interest: {}'.format(rastervalidatorobject.datacovered))
        
        if rastervalidatorobject.cloudcovered and rastervalidatorobject.datacovered:

            for index in userinput.indexlist:
                # check if bands are re
                if index in vegindex.supportedindices:
                    array = vegindex.calculate_index(index)
                elif re.match(cfg['band_designation'], index):
                    array = vegindex.get_band(index)
                else:
                    logging.warning('Chosen index {} not available, continuing with next index.'.format(index))

                masked_array= vegindex.mask_array(array,cloudmask)
                    
                affine = vegindex.affine

                if int(userinput.stat) == 1: 
                    logging.info('Statistics: {}'.format(pathfinderobject.tile))
                    extractorobject = Extractor(masked_array, shapefile, userinput.idname,affine, userinput.statistics)
                    extractedarray = extractorobject.extract_arrays_stat()
                    writerobject = Writer(userinput.outpath, pathfinderobject.date, pathfinderobject.tile, extractedarray, index, userinput.statistics)
                    extractorobject.extract_arrays_stat()
                    writerobject.write_csv()
                    

                elif int(userinput.stat) == 0:
                    
                    extractorobject = Extractor(masked_array, shapefile, userinput.idname,affine,['count'])
                    extractedarray = extractorobject.extract_arrays()
                    writerobject = Writer(userinput.outpath, pathfinderobject.date, pathfinderobject.tile, extractedarray, index, ['array'])
                    extractorobject.extract_arrays()
                    writerobject.write_pickle_arr()
            
        else:
            logging.warning('Cloudcovered or no data in Area of interest!')
            
