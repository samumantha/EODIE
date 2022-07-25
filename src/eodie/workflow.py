"""

Class to run the actual processing based on given data platform.

Author: Arttu Kivimäki (FGI) - July 2022 based on old eodie_process.py by Samantha Wittke et al.

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

    def cloudmask_creation(self, pathfinderobject, config):
        """Create cloudmask from S2 SCL.
        
        Parameters:
        -----------
        pathfinderobject: Pathfinder()
            class Pathfinder
        config: dict
            configuration parameters 
        
        Returns:
        --------
        pathfinderobject: class Pathfinder()
            class Pathfinder initialized with safedir
        cloudmask: array
            Cloudmask array for safedir
        """
        if not self.inputs.nomask:
            # Initialize class Mask 
            mask = Mask(pathfinderobject.imgpath, config)
            # Create cloudmask 
            cloudmask = mask.create_cloudmask()
            # Return both pathfinderobject and the cloudmask as a tuple
            return pathfinderobject, cloudmask
        else:
            logging.info(" Based on userinput, no cloudmasks were created.")
            return pathfinderobject, None
    
    def extract_index(self, vegindex, cloudmask, index, geodataframe, pathfinderobject):
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
        pathfinderobject: class Pathfinder
            object containing information of S2 directory
        
        Returns:
        --------
        None, but writes the results to given output directory in given output formats.
        """
        # Calculate index or extract band values for the whole tile
        if re.match(self.inputs.config["band_designation"], index):
            array = vegindex.get_array(index)
        else:      
            array = vegindex.calculate_index(index)
        # Apply cloudmask to the index array unless decided against by user
        if not self.inputs.nomask:            
            array = vegindex.mask_array(array, cloudmask)
        # Reproject input geodataframe to the same CRS with vegindex
        geodataframe_reprojected = geodataframe.to_crs(vegindex.crs)
        # Initialize class Extractor
        extractorobject = Extractor(
            array,
            geodataframe_reprojected,
            self.inputs.idname,
            vegindex.affine,
            self.inputs.statistics,
            pathfinderobject.orbit,
            self.inputs.exclude_border,
        )
        # Initialize class Writer
        writerobject = Writer(
            self.inputs.outpath,
            pathfinderobject.date,
            pathfinderobject.tile,            
            index,
            self.inputs.platform,
            pathfinderobject.orbit,
            self.inputs.statistics,
            vegindex.crs,
        )
        # Loop through given output formats
        for format in self.inputs.format:
            # Extract arrays in given format
            extractedarray = extractorobject.extract_format(format)
            # Write results in given format
            writerobject.write_format(format, extractedarray)
            if format == "statistics" and "database" in self.inputs.format:
                writerobject.write_format("database", extractedarray) 
                self.inputs.format.remove("database")                
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
        geoobject = VectorData(userinput.vectorbase, userinput.drop_geom, userinput.epsg_for_csv)
        # Read s2tiles into a geodataframe
        s2tiles = geoobject.read_tiles()
        # Clip vectorfile based on data in input directory 
        clipped_geodataframe, tiles = geoobject.clip_vector(userinput.input, s2tiles)
        if userinput.tiles is not None:
            tiles = userinput.tiles
        # Create convex hull of all vector features
        convex_hull = geoobject.get_convex_hull(clipped_geodataframe)
        # Loop through paths in input directory
        for path in userinput.input:
            pathfinderobject = Pathfinder(path, userinput.config)
            if pathfinderobject.tile in tiles:
                # Append the list of delayed functions
                validation.append(delayed(self.validate_safedir)(path, 95, convex_hull))
        logging.info(" Validating safedirs...")
        # Launch delayed computation
        valid = self.execute_delayed(validation)
        # Filter out None returns
        valid_filtered = list(filter(None, valid[0]))
        logging.info(" From original {} safedirs, {} will be processed based on userinput.\n".format(len(userinput.input), len(valid_filtered)))
    
        ####################
        ### CLOUDMASKING ###
        ####################

        # Create empty list for cloudmasks
        cloudmasks = []
        # Loop through valid safedirs
        for validdir in valid_filtered:            
            pathfinderobject = Pathfinder(validdir, userinput.config)
            # Add delayed functions to the list to be computed
            cloudmasks.append(delayed(self.cloudmask_creation)(pathfinderobject, userinput.config))

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
            # Filter geodataframe to only contain features from the area of the Sentinel-2 tile      
            filtered_geodataframe = geoobject.filter_geodataframe(geodataframe, s2tiles, pathfinderobject.tile, userinput.idname)    
            if not filtered_geodataframe.empty:   
                # Loop through indices:
                for index in userinput.indexlist:
                    # Add delayed function calls to the list of index_calculations
                    index_calculations.append(delayed(self.extract_index)(vegindex, cloudmask, index, filtered_geodataframe, pathfinderobject))
    
        logging.info(" Calculating indices and extracting results...")
        # Process index calculations with Dask
        self.execute_delayed(index_calculations) 
        logging.info(" SENTINEL-2 WORKFLOW COMPLETED!")
        logging.info(" Results can be found in {}".format(userinput.outpath))
        # Done.

    def workflow_tif(self):
        """Run workflow for regular GeoTIFFs."""
        userinput = self.inputs      
        tif_extraction = []
        # Read vectorfile into a geoobject
        geoobject = VectorData(userinput.vectorbase)
        # Loop through paths in userinput
        for path in userinput.input:
            # Initialize classes Pathfinder and RasterData
            pathfinderobject = Pathfinder(path, userinput.config)
            raster = RasterData(path, userinput.config)   
            # Reproject vector data to match raster          
            gdf = geoobject.reproject_geodataframe(geoobject.geometries, raster.crs)
            # Loop through tifbands
            for band in userinput.tifbands:
                # Append the list of delayed functions
                tif_extraction.append(delayed(self.extract_from_tif)(path, gdf, raster, band, pathfinderobject))
        logging.info(" Extracting results...")
        self.execute_delayed(tif_extraction)        
        
    def extract_from_tif(self, path, gdf, raster, band, pathfinderobject):
        """Extract zonal statistics from a GeoTIFF and write results accordingly.
        
        Parameters:
        ----------
        path: str
            path to GeoTIFF
        gdf: GeoDataFrame
            vector features to calculate zonal statistics from
        raster: RasterData
            class based on the tif file
        userinput: UserInput
            all userinputs given
        band: str
            band number from multiband tifs
        pathfinderobject: Pathfinder
            object containing tif paths
        
        Returns:
        --------
        None but writes the results in given output formats.
        """
        # Initialize Extractor
        extractorobject = Extractor(
            path,
            gdf,
            self.inputs.idname,
            raster.affine,
            self.inputs.statistics,
            None,
            band,
            self.inputs.exclude_border
        )
        # Initialize Writer
        writerobject = Writer(
            self.inputs.outpath,
            pathfinderobject.date,
            pathfinderobject.tile,
            self.inputs.config["name"] + "_band_" + str(band),
            self.inputs.platform,
            "",
            self.inputs.statistics,
            raster.crs
        )
        # Loop through output formats
        for format in self.inputs.format:
            # Extract given format
            extractedarray = extractorobject.extract_format(format)
            # Write results in given format
            writerobject.write_format(format, extractedarray)

        return None

    def workflow_ls8(self):
        userinput = self.inputs
        logging.info(" LANDSAT8 IS CURRENTLY NOT SUPPORTED.")
        quit("LANDSAT8 IS CURRENTLY NOT SUPPORTED.")