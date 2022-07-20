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
from dask.diagnostics import ProgressBar

def validate_userinput():
    # Read userinput class
    userinput = UserInput()
    #print("Userinput has been read.")
    # Validate the userinput with validator
    Validator(userinput)
    #print("Userinput has been validated.")

    return userinput

def init_logs(userinput):
    userinput.create_logfile(userinput.outpath, userinput.input, userinput.verbose)    
    userinput.list_inputs(userinput)


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

def filter_vectordataframe(vectorframe, tileframe, tile, idname):
    # Select only one tile based on colum Name
    tileframe_tile = tileframe[tileframe['Name'] == tile]
    # Run overlay analysis for vectorframe and one tile
    overlay_result = vectorframe.overlay(tileframe_tile, how = 'intersection')
    # List IDs in the overlay_result based on userinput --id
    ids = list(overlay_result[idname])
    # Filter original vectorframe to only contain listed IDs
    vectorframe_filtered = vectorframe[vectorframe[idname].isin(ids)]
    # Compare geometries between geodataframes to exclude features that were cut during intersection
    overlay_result['equal_geom'] = overlay_result['geometry'].geom_equals(vectorframe_filtered['geometry'], align = False)
    # Exclude features with changed geometries
    overlay_result = overlay_result[overlay_result['equal_geom'] == True]
    # Drop the equal_geom column as it is not needed anymore
    overlay_result = overlay_result.drop(columns = 'equal_geom')
    
    return overlay_result

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

def main():
    
    # CREATE LOGFILES IN USERINPUT?
    # VALIDATION OF VECTORFILE?

    userinput = validate_userinput()
    init_logs(userinput)
    
    ##################
    ### VALIDATION ###
    ##################

    validation = []
    # Read input vectorfile into a VectorData object
    geoobject = VectorData(userinput.vectorbase)
    s2tiles = gpd.read_file("/users/akivimak/EODIE/src/sentinel2_tiles_world/sentinel2_tiles_world.shp")      
    #print("Geoobject has been initialized.")         
    clipped_geodataframe = geoobject.clip_vector(userinput.input, s2tiles)       
    # Get convex hull of features     
    convex_hull = geoobject.get_convex_hull(clipped_geodataframe)         
    # Loop through userinput paths
    for path in userinput.input:
        # Add delayed functions to the list to be computed
        validation.append(delayed(validate_safedir)(path, 95, convex_hull))
    
          
    logging.info(" Validating safedirs...")
    valid = execute_delayed(validation)    
    # Filter out None values from list of valid safedirs
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
    # Read sentinel2_tiles_world.shp into a geodataframe (PATH NEEDS TO BE FIXED)
    s2tiles = gpd.read_file("/users/akivimak/EODIE/src/sentinel2_tiles_world/sentinel2_tiles_world.shp")
    # Reproject geodataframe to EPSG:4326
    clipped_geodataframe.to_crs(s2tiles.crs, inplace = True)
    # Loop through tuples of (safedir, cloudmask):
    for pathfinderobject, cloudmask in cloudmask_results[0]:
        # Initialize class Vegindex
        vegindex = Index(pathfinderobject.imgpath, userinput.config)         
        filtered_geodataframe = filter_vectordataframe(clipped_geodataframe, s2tiles, pathfinderobject.tile, userinput.idname)     
        if not filtered_geodataframe.empty:   
            # Loop through indices:
            for index in userinput.indexlist:
                # Add delayed function calls to the list of index_calculations
                index_calculations.append(delayed(extract_index)(vegindex, cloudmask, index, filtered_geodataframe, userinput, pathfinderobject))
    
    # Begin timer    
    
    logging.info(" Calculating indices and extracting results...")
    # Process index calculations with Dask
    execute_delayed(index_calculations) 
    logging.info(" EODIE WORKFLOW COMPLETED!")
    logging.info(" Results can be found in {}".format(userinput.outpath))
    # Done.



if __name__ == '__main__':
    main()
