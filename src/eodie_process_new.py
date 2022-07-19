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
from dask import delayed
from dask import compute
import geopandas as gpd

def validate_userinput():
    # Read userinput class
    userinput = UserInput()
    print("Userinput has been read.")
    # Validate the userinput with validator
    Validator(userinput)
    print("Userinput has been validated.")

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
    print("Processing {} for tile {} at {}".format(index, pathfinderobject.tile, pathfinderobject.date))
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


def main():

    # CREATE LOGFILES IN USERINPUT?
    # VALIDATION OF VECTORFILE?

    userinput = validate_userinput()

    ###################
    ### VALIDATION ####
    ###################

    validation = []
    # Read input vectorfile into a VectorData object
    geoobject = VectorData(userinput.vectorbase + "." + userinput.input_type)   
    # Get convex hull of features 
    convex_hull = geoobject.get_convex_hull()        
    # Loop through userinput paths
    for path in userinput.input:
        # Add delayed functions to the list to be computed
        validation.append(delayed(validate_safedir)(path, 95, convex_hull))
    # Begin timer
    tic = timeit.default_timer()
    # Run delayed computation with dask
    print("Validating safedirs...")
    valid = compute(validation, scheduler = 'processes')
    # Filter out None values from list of valid safedirs
    valid_filtered = list(filter(None, valid[0]))
    # End timer
    toc = timeit.default_timer()
    print("Validation of all safedirs took {} seconds".format(toc-tic))

    #####################
    ### CLOUDMASKING ####
    #####################

    # Create empty list for cloudmasks
    cloudmasks = []
    # Loop through valid safedirs
    for validdir in valid_filtered:
        # Add delayed functions to the list to be computed
        cloudmasks.append(delayed(cloudmask_creation)(validdir, userinput.config))
    print("Creating cloudmasks...")
    # Begin timer
    tic = timeit.default_timer()
    # Run delayed computation with dask
    cloudmask_results = compute(cloudmasks, scheduler = 'processes')
    # End timer
    toc = timeit.default_timer()
    print("Creating cloudmasks for all safedirs took {} seconds".format(toc-tic))

    #########################
    ### INDEX CALCULATION ###
    #########################

    # Create empty list for indices to be calculated
    index_calculations = []
    # Read original vectorfile into a geodataframe
    geodataframe = gpd.read_file(geoobject.geometries)
    # Read sentinel2_tiles_world.shp into a geodataframe (PATH NEEDS TO BE FIXED)
    s2tiles = gpd.read_file("/users/akivimak/EODIE/src/sentinel2_tiles_world/sentinel2_tiles_world.shp")
    # Reproject geodataframe to EPSG:4326
    geodataframe.to_crs(s2tiles.crs, inplace = True)
    # Loop through tuples of (safedir, cloudmask):
    for pathfinderobject, cloudmask in cloudmask_results[0]:
        # Initialize class Vegindex
        vegindex = Index(pathfinderobject.imgpath, userinput.config)  
        # Filter s2tiles based on current tile
        s2tiles_tile = s2tiles[s2tiles['Name'] == pathfinderobject.tile]
        # Run overlay analysis with geodataframe and one tile
        overlay_result = geodataframe.overlay(s2tiles_tile, how = 'intersection')
        # List IDs that can be found from overlay_result (based on userinput --id)
        ids = list(overlay_result[userinput.idname])
        # Filter geodataframe to only contain features with those IDs
        geodataframe_filtered = geodataframe[geodataframe[userinput.idname].isin(ids)]
        # Compare geometries between overlay_result and filtered geodataframe to exclude features that are on the tile edges
        overlay_result['equal_geom'] = overlay_result['geometry'].geom_equals(geodataframe_filtered['geometry'], align = False) 
        # Exclude features with changed geometries
        overlay_result = overlay_result[overlay_result['equal_geom'] == True]
        # Drop the equal_geom column after comparison (not necessary though, can be skipped)
        overlay_result = overlay_result.drop(columns = 'equal_geom')       
        # Loop through indices:
        for index in userinput.indexlist:
            # Add delayed function calls to the list of index_calculations
            index_calculations.append(delayed(extract_index)(vegindex, cloudmask, index, overlay_result, userinput, pathfinderobject))
    
    # Begin timer    
    tic = timeit.default_timer()
    print("Calculating indices and extracting results...")
    # Process index calculations with Dask
    compute(index_calculations, scheduler = 'processes')
    # End timer
    toc = timeit.default_timer()
    print("Index calculation and extraction for all safedirs and indices took {} seconds".format(toc-tic))
    print("\n")
    print("PROCESSING COMPLETE.")
    # Done.

if __name__ == '__main__':
    main()
