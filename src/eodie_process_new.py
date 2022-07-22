#!/usr/bin/env python

import glob
import math
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
from dask import delayed
from dask import compute
import geopandas as gpd

def read_userinput():
    userinput = UserInput()      
    Validator(userinput)
    return userinput

def validate_safedir(safedir, cloudcover, convex_hull):    
    # Initialize RasterValidatorS2
    rastervalidatorobject = RasterValidatorS2(safedir, cloudcover)
    # First check if the safedir is complete with no missing files:
    if not rastervalidatorobject.check_integrity():
        return None
    else:
        # Check cloudcoverage and datacoverage 
        not_cloudcovered = rastervalidatorobject.check_cloudcover()
        datacovered = rastervalidatorobject.check_datacover(convex_hull)
        # If requirements are met, return safedir, else return None
        if not_cloudcovered and datacovered:
            return safedir
        else:
            return None


def cloudmask_creation(safedir, config):
    # Define pathfinderobject based on safedir and configuration file
    pathfinderobject = Pathfinder(safedir, config)
    # Initialize class Mask 
    mask = Mask(pathfinderobject.imgpath, config)
    # Create cloudmask 
    cloudmask = mask.create_cloudmask()

    # Return both pathfinderobject and the cloudmask as a tuple
    return pathfinderobject, cloudmask


def extract_index(vegindex, cloudmask, index, geodataframe, userinput, pathfinderobject):
    # Calculate index for the whole tile
    array = vegindex.calculate_index(index)
    # Apply cloudmask to the index array
    masked_array = vegindex.mask_array(array, cloudmask)
    # Extract affine (could be put directly to the extractor call...)
    affine = vegindex.affine
    # Reproject input geodataframe to the same CRS with vegindex
    geodataframe_reprojected = geodataframe.to_crs(vegindex.crs)
    # Initialize class Extractor
    extractorobject = Extractor(
        masked_array,
        geodataframe_reprojected,
        userinput.idname,
        affine,
        userinput.statistics,
        pathfinderobject.orbit,
        userinput.exclude_border,
    )
    # Initialize class Writer
    writerobject = Writer(
        userinput.outpath,
        pathfinderobject.date,
        pathfinderobject.tile,            
        index,
        userinput.platform,
        pathfinderobject.orbit,
        userinput.statistics,
        vegindex.crs,
    )
    # Loop through given output formats
    for format in userinput.format:
        # Extract arrays in given format
        extractedarray = extractorobject.extract_format(format)
        # Write results in given format
        writerobject.write_format(format, extractedarray)
    return None    

def execute_delayed(input_list):
    tic = timeit.default_timer()
    results = compute(input_list, scheduler = 'processes')
    toc = timeit.default_timer()
    logging.info(" Delayed processing took {} seconds.\n".format(math.ceil(toc-tic)))
    return results

def s2_workflow(userinput):
    validation = []
    geoobject = VectorData(userinput.vectorbase)
    s2tiles = geoobject.read_tiles()
    clipped_geodataframe = geoobject.clip_vector(userinput.input, s2tiles)
    convex_hull = geoobject.get_convex_hull(clipped_geodataframe)
    for path in userinput.input:
            validation.append(delayed(validate_safedir)(path, 95, convex_hull))
    logging.info(" Validating safedirs...")
    valid = execute_delayed(validation)
    valid_filtered = list(filter(None, valid[0]))
    logging.info(" From original {} safedirs, {} are valid for processing.\n".format(len(userinput.input), len(valid_filtered)))
    
    ####################
    ### CLOUDMASKING ###
    ####################

    # Create empty list for cloudmasks
    cloudmasks = []
    # Loop through valid safedirs
    for validdir in valid_filtered:
        # Add delayed functions to the list to be computed
        cloudmasks.append(delayed(cloudmask_creation)(validdir, userinput.config))

    logging.info(" Creating cloudmasks...") 
    # Run delayed computation with dask
    cloudmask_results = execute_delayed(cloudmasks)    
    
    #########################
    ### INDEX CALCULATION ###
    #########################

    # Create empty list for indices to be calculated
    index_calculations = []    
    # Reproject geodataframe to EPSG:4326
    geodataframe = geoobject.reproject_geodataframe(clipped_geodataframe, s2tiles.crs)    
    # Loop through tuples of (safedir, cloudmask):
    for pathfinderobject, cloudmask in cloudmask_results[0]:
        # Initialize class Vegindex
        vegindex = Index(pathfinderobject.imgpath, userinput.config)         
        filtered_geodataframe = geoobject.filter_geodataframe(geodataframe, s2tiles, pathfinderobject.tile, userinput.idname)     
        if not filtered_geodataframe.empty:   
            # Loop through indices:
            for index in userinput.indexlist:
                # Add delayed function calls to the list of index_calculations
                index_calculations.append(delayed(extract_index)(vegindex, cloudmask, index, filtered_geodataframe, userinput, pathfinderobject))
    
    logging.info(" Calculating indices and extracting results...")
    # Process index calculations with Dask
    execute_delayed(index_calculations) 
    logging.info(" EODIE WORKFLOW COMPLETED!")
    logging.info(" Results can be found in {}".format(userinput.outpath))
    # Done.


def main():    
    
    userinput = read_userinput()  
    if userinput.platform == "s2":
        s2_workflow(userinput)
    
if __name__ == '__main__':
    main()
