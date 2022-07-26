"""

Class to handle everything regarding the vectordata, atm only ESRI shapefile.
    
Authors: Samantha Wittke

"""
import os
import math
from osgeo import osr, ogr, gdal
import fiona
from copy import deepcopy
from shapely.geometry import Polygon
from shapely.validation import explain_validity
import shapely
import geopandas as gpd
import logging
from shutil import copyfile
import re
import glob
import timeit
import warnings

warnings.simplefilter(action = 'ignore', category=UserWarning)

class VectorData(object):
    """Vector data related information and transformations.

    Attributes
    -----------
    geometries: str
        location and name of a vectorfile
    """

    def __init__(self, geometries, drop=False, epsg_for_csv=None):
        """Initialize vectordata object.

        Parameters
        -----------
        geometries: str
            location and name of a vectorfile
        drop: boolean
            whether missing or invalid geometries should be excluded from further processing
        """
        self.geometries = self.read_geodataframe(geometries)
        if epsg_for_csv is not None:            
            self.geometries.crs = "EPSG:" + epsg_for_csv
        self.geometries = self.check_validity(drop)
        

    def read_geodataframe(self, geometries):
        """Read input vectorfile into a geopandas GeoDataframe.
        
        Parameters:
        -----------
        geometries: str
            path to input vectorfile
        
        Returns:
        --------
        geodataframe: GeoDataframe
            input vector read into a geodataframe
        """
        logging.info(" Reading vectorfile into a geodataframe...")
        geodataframe = gpd.read_file(geometries)
        logging.info(" Geodataframe read!\n")
        
        return geodataframe

    def get_epsg(self):
        """Extract epsg code from geodataframe.

        Returns
        --------
        vectorepsg: str
            EPSG code of the vectorfile
        """
        epsgcode = self.geometries.crs.to_epsg()

        return str(epsgcode)

    def get_convex_hull(self, geodataframe):
        """Extract convex hull of all features of geodataframe that are located in the area of input data.

        Parameters:
        -----------
        geodataframe: GeoDataframe
            geodataframe for the features to extract convex hull from

        Returns:
        --------
        convexhull: GeoDataframe
            GeoDataframe consisting of one feature, the convex hull
        """          
        logging.info(" Extracting convex hull...")
        tic = timeit.default_timer()
        # Create envelopes for all features
        gdf_envelope = geodataframe.envelope
        toc = timeit.default_timer()
        logging.info(" Creating envelopes took {} seconds.".format(math.ceil(toc-tic)))
        tic = timeit.default_timer()
        # Execute unary_union for envelopes
        gdf_unary_union = gdf_envelope.unary_union    
        toc = timeit.default_timer()
        logging.info(" Creating unary union from envelopes took {} seconds.".format(math.ceil(toc-tic)))
        tic = timeit.default_timer() 
        # Extract convex_hull based on results of unary_union
        ch = gdf_unary_union.convex_hull
        # Turn convexhull into a geodataframe
        convexhull = gpd.GeoDataFrame(crs = geodataframe.crs, geometry=[ch])
        toc = timeit.default_timer()
        logging.info(" Creating convex hull from unary union took {} seconds.\n".format(math.ceil(toc-tic)))        
        return convexhull

    def check_empty(self, vectorfile):
        """Check for empty geometries in vectorfile.

        Parameters:
        -----------
            vectorfile: geodataframe the user-defined vectorfile
        Returns:
        --------
            None; prints the rows with non-existent geometries.
        """
        logging.info(" Checking for empty geometries...")
        # Filter rows where geometry is None
        vectorfile_nogeom = vectorfile[vectorfile["geometry"] == None]
        # Log accordingly
        if len(vectorfile_nogeom) > 0:
            logging.info(
                " Following features have no geometry:\n\n {}".format(vectorfile_nogeom)
            )
        else:
            logging.info(" All features have geometries!\n")

    def check_validity(self, drop):
        """Check the validity of each polygon in the vectorfile. Invalid geometries will be excluded from the calculations; saves a new shapefile without the invalid polygons, if any exist.
        
        Parameters:
        -----------
        drop: boolean
            flag to indicate if invalid geometries should be dropped.

        Returns:
        --------
        valid_geom: GeoDataframe
            geodataframe with only valid geometries - if all geometries are valid, returns original geodataframe
        """
        geodataframe = self.geometries
        # Check empty geometries
        self.check_empty(geodataframe)
        logging.info(" Checking geometry validity...")
        # Check validity of geometries
        geodataframe["validity"] = geodataframe["geometry"].is_valid
        # Extract only rows with existing geometries
        with_geom = geodataframe.loc[geodataframe["geometry"] != None].copy()
        # Filter rows where geometries were invalid
        invalid_geom = with_geom.loc[
            with_geom["validity"] == False
        ].copy()
        # If invalid geometries exist, run explain_validity for them
        if len(invalid_geom) > 0:
            invalid_geom[
                "explanation"
            ] = invalid_geom.apply(
                lambda row: explain_validity(row.geometry), axis=1
            )
            logging.info(
                " Following features have invalid geometries:\n\n {}".format(
                    invalid_geom
                )
            )
        else:
            logging.info(" All features have valid geometries!\n")

        # If --delete_invalid_geometries was defined, rewrite a new file without invalid geometries.
        if drop:
            # Filter only valid geometries
            valid_geom = with_geom.loc[
                with_geom["validity"] == True
            ].copy()
            return valid_geom

        else:
            return self.geometries            

    def clip_vector(self, safes, tileframe, idname):
        """Clip vector based on data in input directory.

        Parameters:
        -----------
        safes: list
            list of input files
        tileframe: GeoDataframe
            a geodataframe containing the Sentinel-2 tiles

        Returns:
        --------
        clipped_geodataframe: GeoDataframe
            original geodataframe clipped by tiles found in raster input directory
        """
        logging.info(" Clipping input vector based on data in raster directory...\n")
        tic = timeit.default_timer()
        tiles = []
        # Loop through safes
        for safedir in safes:
            head, tail = os.path.split(safedir)
            tile = tail.split("_")[5][1:6]
            # If tilename noet yet in list of tiles, add it
            if tile not in tiles:
                tiles.append(tile)
        # Select only tiles that are found in input directory
        tileframe = tileframe[tileframe['Name'].isin(tiles)]
        # Reproject vector geodataframe to EPSG:4326
        gdf = self.reproject_geodataframe(self.geometries, "EPSG:4326")
        # Clip
        clipped_geodataframe = gpd.clip(gdf, tileframe)         
        ids = list(clipped_geodataframe[idname])
        gdf = gdf[gdf[idname].isin(ids)] 
        clipped_geodataframe['equal_geom'] = clipped_geodataframe.sort_values(by=idname)['geometry'].geom_equals(gdf.sort_values(by=idname)['geometry'], align = False)            
        # Exclude features with changed geometries
        clipped_geodataframe = clipped_geodataframe[clipped_geodataframe['equal_geom'] == True]       
        # Drop the equal_geom column as it is not needed anymore
        clipped_geodataframe = clipped_geodataframe.drop(columns = 'equal_geom')
        toc = timeit.default_timer()
        logging.info(" Clipping took {} seconds.\n".format(math.ceil(toc-tic)))

        return clipped_geodataframe, tiles

    def read_tiles(self):
        """Read Sentinel-2 tiles into a Geodataframe.

        Returns:
        --------
        tileframe: GeoDataframe
            geodataframe containing the Sentinel-2 tiles
        """
        # Build tilepath
        tilepath = os.path.join(os.getcwd(), "sentinel2_tiles_world", "sentinel2_tiles_world.shp")
        # Read into a geodataframe
        tileframe = gpd.read_file(tilepath)
        return tileframe

    def reproject_geodataframe(self, geodataframe, crs):
        """Reproject GeoDataframe to another crs.

        Parameters:
        ----------
        geodataframe: GeoDataframe
            geodataframe to reproject
        crs: crs
            crs to reproject the geodataframe into
        
        Returns:
        -------
        reprojected: GeoDataframe
            the original geodataframe reprojected to crs
        """
        logging.info(" Reprojecting geodataframe...")
        reprojected = geodataframe.to_crs(crs)
        logging.info(" Reprojection completed.\n")
        return reprojected
    
    def filter_geodataframe(self, vectorframe, tileframe, tile, idname):
        """ Filter features of geodataframe that can be found in the area of one Sentinel-2 tile.

        Parameters:
        ----------
        vectorframe: GeoDataframe
            geodataframe containing the polygon features
        tileframe: GeoDataframe
            geodataframe containing the Sentinel-2 tiles
        tile: str
            Sentinel-2 tilecode
        idname: str
            identifier of features in vectorframe
        
        Returns:
        --------
        overlay_result: GeoDataframe
            geodataframe containing the features that are completely in area of given tile - features crossing the tile edges are excluded
        """
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