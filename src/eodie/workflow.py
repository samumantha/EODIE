"""

Class to run the actual processing based on given data platform.

Author: Arttu Kivimäki (FGI) - July 2022

"""

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
from eodie.rasterdata import RasterData
from eodie.validator import Validator
import logging
from datetime import datetime
import timeit
from dask import delayed
from dask import compute
import geopandas as gpd


class Workflow(object):
    """ Class responsible for EODIE processing workflow.

    Attributes:
    inputs: Userinput object
        all inputs given by user
    platform: str
        platform given by user {s2, ls8, tif}    
    """

    def __init__(self, userinput):
        """ Initialize Workflow object.

        Parameters:
        -----------
        userinput: Userinput object
            All processing inputs given by user.
        """
        self.inputs = userinput
        self.platform = userinput.platform
        self.launch_workflow(self.platform)

    def execute_delayed(self, input_list):
        """Execute given processes with dask.delayed.

        Parameters:
        -----------
        input_list: list
            list of delayed functions to be executed

        Returns:
        --------
        results: tuple
            outputs of executed functions
        """
        tic = timeit.default_timer()
        results = compute(input_list, scheduler = 'processes')
        toc = timeit.default_timer()
        logging.info(" Delayed processing took {} seconds.\n".format(math.ceil(toc-tic)))
        return results

    def validate_safedir(self, safedir, cloudcover, convex_hull): 
        """Validate .SAFE directories with RasterValidatorS2.

        Parameters:
        -----------
        safedir: str
            path to SAFE directory to validate
        cloudcover: int
            maximum cloudcover percentage, imagery above this will be excluded
        convex_hull: GeoDataframe
            combined convex hull of all vectorfile features 

        Returns:
        --------
        safedir: str
            if safedir is valid for further processing; else None
        """
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

    def cloudmask_creation(self, safedir, config):
        """Create cloudmask from S2 SCL.
        
        Parameters:
        -----------
        safedir: str
            path to SAFE directory 
        config: dict
            configuration parameters 
        
        Returns:
        --------
        pathfinderobject: class Pathfinder()
            class Pathfinder initialized with safedir
        cloudmask: array
            Cloudmask array for safedir
        """
        # Define pathfinderobject based on safedir and configuration file
        pathfinderobject = Pathfinder(safedir, config)
        # Initialize class Mask 
        mask = Mask(pathfinderobject.imgpath, config)
        # Create cloudmask 
        cloudmask = mask.create_cloudmask()
        # Return both pathfinderobject and the cloudmask as a tuple
        return pathfinderobject, cloudmask
    
    def extract_index(self, vegindex, cloudmask, index, geodataframe, userinput, pathfinderobject):
        """Calculate given index, extract zonal statistics and write results.

        Parameters:
        -----------
        vegindex: class Index()
            Class for calculating the indices or extracting arrays
        cloudmask: array
            cloudmask created from S2 SCL
        index: str
            index or band name to calculate zonal statistics from
        geodataframe: GeoDataframe
            Polygon features to calculate zonal statistics from
        userinput: class Userinput
            Class containing all userinputs
        pathfinderobject: class Pathfinder
            object containing information of S2 directory
        
        Returns:
        --------
        None, but writes the results to given output directory in given output formats.
        """
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

    def launch_workflow(self, platform):
        """Launch workflow depending on given platform."""
        default = "Unknown platform"
        return getattr(self, "workflow_" + platform, lambda: default)()

    def workflow_s2(self):
        """Run workflow for Sentinel-2 imagery."""
        userinput = self.inputs

        ##################
        ### VALIDATION ###
        ##################

        validation = []
        # Read vectorfile into a geoobject
        geoobject = VectorData(userinput.vectorbase)
        # Read s2tiles into a geodataframe
        s2tiles = geoobject.read_tiles()
        # Clip vectorfile based on data in input directory 
        clipped_geodataframe = geoobject.clip_vector(userinput.input, s2tiles)
        # Create convex hull of all vector features
        convex_hull = geoobject.get_convex_hull(clipped_geodataframe)
        # Loop through paths in input directory
        for path in userinput.input:
            # Append the list of delayed functions
            validation.append(delayed(self.validate_safedir)(path, 95, convex_hull))
        logging.info(" Validating safedirs...")
        # Launch delayed computation
        valid = self.execute_delayed(validation)
        # Filter out None returns
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
            cloudmasks.append(delayed(self.cloudmask_creation)(validdir, userinput.config))

        logging.info(" Creating cloudmasks...") 
        # Run delayed computation with dask
        cloudmask_results = self.execute_delayed(cloudmasks)    
    
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
                    index_calculations.append(delayed(self.extract_index)(vegindex, cloudmask, index, filtered_geodataframe, userinput, pathfinderobject))
    
        logging.info(" Calculating indices and extracting results...")
        # Process index calculations with Dask
        self.execute_delayed(index_calculations) 
        logging.info(" SENTINEL-2 WORKFLOW COMPLETED!")
        logging.info(" Results can be found in {}".format(userinput.outpath))
        # Done.

    def workflow_tif(self):
        userinput = self.inputs
        logging.info(" GEOTIFFS ARE CURRENTLY NOT SUPPORTED.")
        
        tif_extraction = []

        geoobject = VectorData(userinput.vectorbase)

        for path in userinput.input:
            pathfinderobject = Pathfinder(path, userinput.config)
            raster = RasterData(path, userinput.config)            
            gdf = geoobject.reproject_geodataframe(geoobject.geometries, raster.crs)
            
            for band in userinput.tifbands:
                tif_extraction.append(delayed(self.extract_from_tif)(path, gdf, raster, userinput, band, pathfinderobject))
        
        self.execute_delayed(tif_extraction)        
        
    def extract_from_tif(self, path, gdf, raster, userinput, band, pathfinderobject):
            extractorobject = Extractor(
                path,
                gdf,
                userinput.idname,
                raster.affine,
                userinput.statistics,
                None,
                band,
                userinput.exclude_border
            )
            writerobject = Writer(
                userinput.outpath,
                pathfinderobject.date,
                pathfinderobject.tile,
                userinput.config["name"] + "_band_" + str(band),
                userinput.platform,
                "",
                userinput.statistics,
                raster.crs
            )
            for format in userinput.format:
                extractedarray = extractorobject.extract_format(format)
                writerobject.write_format(format, extractedarray)












    def workflow_ls8(self):
        userinput = self.inputs
        logging.info(" LANDSAT8 IS CURRENTLY NOT SUPPORTED.")
        quit("LANDSAT8 IS CURRENTLY NOT SUPPORTED.")