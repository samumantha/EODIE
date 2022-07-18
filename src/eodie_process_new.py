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

    userinput = UserInput()
    print("Userinput has been read.")
    Validator(userinput)
    print("Userinput has been validated.")

    return userinput



def main():
    userinput = validate_userinput()
    # Do tilesplitting

    # TILESPLITTING CHUNK GOES HERE

    # Do rastervalidation
    # Create empty list for validation
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
    valid = compute(validation, scheduler = 'processes')
    # Filter out None values from list of valid safedirs
    valid_filtered = list(filter(None, valid[0]))
    # End timer
    toc = timeit.default_timer()
    print("Validation of all safedirs took {} seconds".format(toc-tic))

    # Do cloudmasking for valid safedirs

    # CLOUDMASKING CHUNK GOES HERE 

    
    # Do index calculation

    # INDEX CALCULATION CHUNK GOES HERE



    # Done.


def validate_safedir(safedir, cloudcover, convex_hull):
    print("VALIDATING {}".format(safedir))
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

if __name__ == '__main__':
    main()
