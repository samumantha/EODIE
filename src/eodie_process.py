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
from eodie.tilesplitter import TileSplitter
from eodie.rasterdata import RasterData
from eodie.validator import Validator
import logging
from datetime import datetime
import timeit


userinput = UserInput()
Validator(userinput)

cfg = userinput.config
tiles = None

# create results dir
if not os.path.exists(userinput.outpath):
    os.mkdir(userinput.outpath)

# setup logging for prints in file and stdout

# Extract input file or directory name from input for naming the log file accordingly
if userinput.rasterfile is not None:
    filename = os.path.split(userinput.rasterfile)[1].split(".")[0]
else:
    dirname = os.path.split(userinput.rasterdir)[1] 

# If --verbose was given, logging outputs will be printed to terminal
if userinput.verbose:  
    # If --file was given, filename will be used as basename for logging file.
    if userinput.rasterfile is not None:
        handlers = [logging.FileHandler(os.path.join(userinput.outpath, filename + "_" + datetime.now().strftime("%Y-%m-%d_%H-%M-%S") + '.log')), logging.StreamHandler()]
    # If --dir was given, directory name will be used as basename for logging file.
    else:
        handlers = [logging.FileHandler(os.path.join(userinput.outpath, dirname + "_" + datetime.now().strftime("%Y-%m-%d") + '.log')), logging.StreamHandler()]        
    logging.basicConfig(level = logging.INFO, handlers = handlers)
else:
    # If --file was given, filename will be used as basename for logging file
    if userinput.rasterfile is not None:
        logging.basicConfig(filename = os.path.join(userinput.outpath, filename + "_" + datetime.now().strftime("%Y-%m-%d_%H-%M-%S") + '.log'), level = logging.INFO)
    # If --dir was given, directory name will be used as basename for logging file. 
    else:
        logging.basicConfig(filename = os.path.join(userinput.outpath, dirname + "_" + datetime.now().strftime("%Y-%m-%d") + '.log'), level = logging.INFO)

logging.info(' ALL INPUTS FOR THIS PROCESS:')
# Loop through userinputs and print key: value to log file.
for key in vars(userinput).keys():
    logging.info(" {}: {}".format(key, str(vars(userinput)[key])))

# If data is not in shapefile format, transform it to shapefile:
if userinput.input_type != 'shp': 
    logging.info(" CONVERTING {} TO A SHAPEFILE".format(userinput.vectorbase))
    object_to_shp = VectorData(userinput.vectorbase + "." + userinput.input_type)
    # If input format is csv, run csv_to_shp
    if userinput.input_type == 'csv':
        object_to_shp.csv_to_shp(userinput.vectorbase + ".shp", userinput.epsg_for_csv)
    # If input format is geopackage with a defined layername, run gpkg_to_shp
    elif (userinput.input_type == 'gpkg') & (userinput.gpkg_layer != None):
        object_to_shp.gpkg_to_shp(userinput.vectorbase + ".shp", userinput.gpkg_layer)
    # Otherwise run convert_to_shp
    else:      
        object_to_shp.convert_to_shp(userinput.vectorbase + ".shp")

    logging.info(" SHAPEFILE CONVERSION COMPLETED")

tiles = None
shp_directory, shp_name = os.path.split(userinput.vectorbase)


logging.info(' STARTING TILESPLITTING ')
if not userinput.exclude_splitbytile:
    # Read userinput.vectorbase and worldtiles, do splitshp_world, then splitshp_mp and give new shapefile(s?) to next step. Loop in case of many shapefiles?
    geoobject = VectorData(userinput.vectorbase + ".shp")
    logging.info(" Checking vectorfile validity...")
    small_polygon_shapefile = geoobject.check_validity(userinput.drop_geom)
    world_tiles = cfg["tileshp"] + ".shp"
    fieldname = cfg["fieldname"]
    tilesplit = TileSplitter(
        small_polygon_vectorfile, world_tiles, shp_directory, fieldname
        )
    tic = timeit.default_timer()
    tilesplit.tilesplit()
    toc = timeit.default_timer()
    tilesplit_time = toc - tic
    if tilesplit_time > 60:
        tilesplit_time = round(tilesplit_time / 60)
        logging.info(
            " Tilesplitting completed, process took {} minutes".format(tilesplit_time)
        )
    else:
        tilesplit_time = round(tilesplit_time + 1)
        logging.info(
            " Tilesplitting completed, process took {} seconds".format(tilesplit_time)
        )
    
    # Check if user limited the tiles to be processed
    if userinput.tiles is not None:
        tiles = userinput.tiles
    else:
        tiles = tilesplitter.tiles
    shp_directory = os.path.join(shp_directory, "EODIE_temp_shp")
    baseshapename = tilesplit.basename

else:
    baseshapename = userinput.vectorbase



logging.info(' STARTING TO PROCESS IMAGERY')
#running through either one file, if file was given or multiple files if dir was given
for path in userinput.input:

    pathfinderobject = Pathfinder(path, cfg)
    if tiles is None:
        tiles = pathfinderobject.tile

    if userinput.platform == "tif":
        for band in userinput.tifbands:
            band = int(band)
            logging.info("File and band to be processed {}, band {}".format(path, band))
            raster = RasterData(path, cfg)
            geoobject = VectorData(baseshapename + ".shp")
            geoobject.reproject_to_epsg(raster.epsg)
            extractorobject = Extractor(
                path,
                geoobject.geometries,
                userinput.idname,
                raster.affine,
                userinput.statistics,
                None,
                band,
                userinput.exclude_border,
            )

            for format in userinput.format:
                extractedarray = extractorobject.extract_format(format)
                writerobject = Writer(
                    userinput.outpath,
                    pathfinderobject.date,
                    pathfinderobject.tile,
                    extractedarray,
                    cfg["name"] + "_band_" + str(band),
                    userinput.platform,
                    "",
                    userinput.statistics,
                    raster.crs,
                )
                writerobject.write_format(format)
                if format == "statistics" and userinput.database_out:
                    writerobject.write_format("database")

    else:
        if pathfinderobject.tile in tiles:
            logging.info(' Imagepath is {}'.format(pathfinderobject.imgpath))
            logging.info(' Tile is {}'.format(pathfinderobject.tile))
            logging.info(' Date is {}'.format(pathfinderobject.date))
        else:
            logging.info(
                " Data from tile {} was found within input folder but was not processed.".format(
                    pathfinderobject.tile
                )
            )

        if (
            int(pathfinderobject.date) <= int(userinput.enddate)
            and int(pathfinderobject.date) >= int(userinput.startdate)
            and pathfinderobject.tile in tiles
        ):                      
            
            if not userinput.exclude_splitbytile:
                shpname = baseshapename + "_" + pathfinderobject.tile + ".shp"
            else:
                shpname = baseshapename + ".shp"
        
            if userinput.extmask is None:
                logging.info(' Creating cloudmask...')
                mask = Mask(pathfinderobject.imgpath, cfg, userinput.test)
                cloudmask = mask.create_cloudmask()
                
            else:
                cname = userinput.extmask + '_' + pathfinderobject.date + '_' + pathfinderobject.tile + '.*'
                extmask = glob.glob(cname)[0]
                cloudmask = Mask(pathfinderobject.imgpath, cfg, userinput.test, extmask).cloudmask
                logging.info(' Using external cloudmask {}'.format(extmask))
            logging.info(' Shape of cloudmask is {}'.format(cloudmask.shape))

            vegindex = Index(pathfinderobject.imgpath, cfg)

            maxcloudcover = cfg["maxcloudcover"]
            if userinput.platform == "s2":
                rastervalidatorobject = RasterValidatorS2(
                    path, maxcloudcover
                )

                if not rastervalidatorobject.check_integrity():
                    logging.info(
                        " The input SAFE {} is missing crucial files and will be skipped.".format(
                            path
                        )
                    ) 
                    logging.info(
                        " "
                    )
                    continue
                else:

                    vegindex = Index(pathfinderobject.imgpath, cfg)
                    geoobject = VectorData(os.path.join(shp_directory, shpname))
                    geoobject.reproject_to_epsg(vegindex.epsg)

                    shapefile = geoobject.geometries

                    not_cloudcovered = rastervalidatorobject.check_cloudcover()
                    datacovered = rastervalidatorobject.check_datacover(geoobject)

                    logging.info(
                        "Cloudcover below {}: {}".format(
                            maxcloudcover, not_cloudcovered
                        )
                    )
                    logging.info(
                        "Data withing area of interest: {}".format(
                            datacovered
                        )
                    )
                    
                    orbit = rastervalidatorobject.get_orbit_number()
            else:
                not_cloudcovered = True
                datacovered = True
            
            if not userinput.nomask:

                if userinput.extmask is None:
                    mask = Mask(pathfinderobject.imgpath, cfg, userinput.test)
                    cloudmask = mask.create_cloudmask()

                else:
                    cname = (
                        userinput.extmask
                        + "_"
                        + pathfinderobject.date
                        + "_"
                        + pathfinderobject.tile
                        + ".*"
                    )
                    extmask = glob.glob(cname)[0]
                    cloudmask = Mask(
                        pathfinderobject.imgpath, cfg, userinput.test, extmask
                    ).cloudmask
                    logging.info("Using external cloudmask {}".format(extmask))

                logging.info("Shape of cloudmask is {}".format(cloudmask.shape))
                
            if not_cloudcovered and datacovered:
                logging.info(" LOOPING THROUGH GIVEN INDICES")
                for index in userinput.indexlist:
                    logging.info(" Calculating {}".format(index))
                    if re.match(cfg["band_designation"], index):
                        array = vegindex.get_array(index)
                    else:
                        array = vegindex.calculate_index(index)

                    # If user input --no_cloudmask was used, do not apply cloudmask:
                    if userinput.nomask:
                        logging.info(
                            " Cloudmask will not be applied as input --no_cloudmask was entered."
                        )
                        affine = vegindex.affine
                        extractorobject = Extractor(
                            array,
                            shapefile,
                            userinput.idname,
                            affine,
                            userinput.statistics,
                            orbit,
                            userinput.exclude_border,
                        )
                    else:
                        logging.info(" Applying cloudmask...")
                        masked_array = vegindex.mask_array(array, cloudmask)
                        affine = vegindex.affine
                        extractorobject = Extractor(
                            masked_array,
                            shapefile,
                            userinput.idname,
                            affine,
                            userinput.statistics,
                            orbit,
                            userinput.exclude_border,
                        )

                    logging.info(" Extracting results...")

                    for format in userinput.format:
                        tic = timeit.default_timer()
                        extractedarray = extractorobject.extract_format(format)
                        toc = timeit.default_timer()
                        extracting_time = toc - tic
                        if extracting_time > 60:
                            extracting_time = round(extracting_time / 60)
                            logging.info(
                                " Extracting {} for {} took {} minutes".format(
                                    format, index, extracting_time
                                )
                            )
                        else:
                            logging.info(
                                " Extracting {} for {} took {} seconds".format(
                                    format, index, round(extracting_time + 1)
                                )
                            )
                        writerobject = Writer(
                            userinput.outpath,
                            pathfinderobject.date,
                            pathfinderobject.tile,
                            extractedarray,
                            index,
                            userinput.platform,
                            orbit,
                            userinput.statistics,
                            vegindex.crs,
                        )
                        writerobject.write_format(format)
                        if format == "statistics" and userinput.database_out:
                            writerobject.write_format("database")
                        
                if 'array' in userinput.format:
                    lookup_file = cfg['lookup']
                    writerobject.write_lookup(lookup_file, shapefile, userinput.idname)
                   
            else:
                logging.warning(' Cloudcovered or no data in Area of interest in {}'.format(path))

    logging.info(" ")

if not userinput.exclude_splitbytile:
    if not userinput.keep_splitted: 
        tilesplit.delete_splitted_files()
logging.info(' Processing complete!')
