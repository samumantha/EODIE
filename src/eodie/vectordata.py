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

class VectorData(object):
    """Vector data related information and transformations.

    Attributes
    -----------
    geometries: str
        location and name of a vectorfile
    """

    def __init__(self, geometries, drop=True):
        """Initialize vectordata object.

        Parameters
        -----------
        geometries: str
            location and name of a vectorfile
        """
        self.geometries = self.read_geodataframe(geometries)
        self.geometries = self.check_validity(drop)
        

    def read_geodataframe(self, geometries):
        logging.info(" Reading vectorfile into a geodataframe...")
        geodataframe = gpd.read_file(geometries)
        logging.info(" Geodataframe read!\n")
        
        return geodataframe

    def _split_path(self):
        """Split shapefile path into parts.

        Returns
        --------
        head: str
            location (path) of the vectorfile without name
        tail: str
            name and extension of the vectorfile
        root: str
            name of the vectorfile
        ext: str
            exension of the vectorfile
        """
        head, tail = os.path.split(self.geometries)
        root, ext = os.path.splitext(tail)
        return head, tail, root, ext

    def get_projectionfile(self):
        """Get path to the projectionfile that is associated with the shapefile.

        Returns
        --------
        projectionfile: str
            the projectionfile belonging to the vectorfile
        """
        head, _, root, _ = self._split_path()
        rootprj = root + ".prj"
        projectionfile = os.path.join(head, rootprj)
        return projectionfile

    def get_epsg(self):
        """Extract epsg code from geodataframe.

        Returns
        --------
        vectorepsg: str
            EPSG code of the vectorfile
        """
        epsgcode = self.geometries.crs.to_epsg()

        return str(epsgcode)

    def get_properties(self):
        """ extract driver, schema and crs from vectorfile
        
        Returns
        --------
        driver: str
            driver of the vectorfile
        schema: str
            schema of the vectorfile
        crs: str
            CRS of the vectorfile
        """
        with fiona.open(self.geometries, "r") as opengeom:
            driver = opengeom.driver
            schema = deepcopy(opengeom.schema)
            crs = opengeom.crs
            return driver, schema, crs

    def get_boundingbox(self):
        """Extract bounding box Polygon object from shapefile.
        
        Returns
        --------
        boundingbox: object
            polygon object of the boundingbox for the whole vectorfile
        """
        with fiona.open(self.geometries,'r') as open_vectordata:
            bounding_box_coordinates = open_vectordata.bounds
            logging.info(bounding_box_coordinates)
        return Polygon.from_bounds(
            bounding_box_coordinates[0],
            bounding_box_coordinates[1],
            bounding_box_coordinates[2],
            bounding_box_coordinates[3],
        )

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
        gdf_envelope = geodataframe.envelope
        toc = timeit.default_timer()
        logging.info(" Creating envelopes took {} seconds".format(math.ceil(toc-tic)))
        tic = timeit.default_timer()
        gdf_unary_union = gdf_envelope.unary_union    
        toc = timeit.default_timer()
        logging.info(" Creating unary union from envelopes took {} seconds".format(math.ceil(toc-tic)))
        tic = timeit.default_timer() 
        ch = gdf_unary_union.convex_hull
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
            logging.info(" All features have geometries.\n")

    def check_validity(self, drop):
        """Check the validity of each polygon in the vectorfile. Invalid geometries will be excluded from the calculations; saves a new shapefile without the invalid polygons, if any exist.
        
        Parameters:
        -----------
            drop: Flag to indicate if invalid geometries should be dropped.
        Returns:
        --------
        vectorfilepath: str
            Path to either the original vectorfile or a filtered one, from which features with empty or invalid geometries have been removed.
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
            logging.info(" All features have valid geometries.")

        # If --delete_invalid_geometries was defined, rewrite a new file without invalid geometries.
        if drop:
            # Filter only valid geometries
            valid_geom = with_geom.loc[
                with_geom["validity"] == True
            ].copy()
            return valid_geom

        else:
            return self.geometries      


    def convert_to_shp(self, output):
        """ converts the input vector file into shapefile for processing. This function is used with geojson, single-layer geopackages and flatgeobufs.
        Parameters
        ----------
        output: str
            the name of the output file (basename.shp)
        """
        logging.info('Converting vector input to a shapefile...')
        # Open input file with gdal
        input_file = gdal.OpenEx(self.geometries)              
        # Define gdal.VectorTranslateOptions        
        gdal_options = gdal.VectorTranslateOptions(format = "ESRI Shapefile")
        # Run gdal.VectorTranslate
        gdal.VectorTranslate(destNameOrDestDS=output, srcDS=input_file, options=gdal_options)
        logging.info('Shapefile conversion completed!')
        

        # Empty the file from memory
        input_file = None
        
    def csv_to_shp(self, output, epsg):
        """ converts the input csv file into shapefile for processing. 
        Parameters
        ----------
        output: str
            the name of the output file (basename.shp)
        epsg: str
            the EPSG code for the csv file input       
        """
        logging.info('Converting csv input to a shapefile...')
        # Open file with gdal
        input_file = gdal.OpenEx(self.geometries)
        # Define format EPSG:epsg 
        srs = 'EPSG:' + epsg
        # Define gdal.VectorTranslateOptions
        gdal_options = gdal.VectorTranslateOptions(format = "ESRI Shapefile", srcSRS=srs, dstSRS=srs)
        # Run gdal.VectorTranslate
        gdal.VectorTranslate(destNameOrDestDS=output, srcDS=input_file, options=gdal_options)
        # Empty input file from memory
        input_file = None
        logging.info('Shapefile conversion completed!')

    def gpkg_to_shp(self, output, layer):
        """ converts the layer from input gpkg file into shapefile for processing. This function is used with geopackages with more than one layer.
        Parameters
        ----------
        output: str
            the name of the output file (basename.shp)
        layer: str
            the name of the layer in geopackage to convert
        """
        logging.info('Converting geopackage layer to a shapefile...')
        # Open the layer with Fiona
        with fiona.open(self.geometries, layer = layer) as input:          
            # Create and open another file with shapefile driver, inheriting schema and crs from input geometries
            with fiona.open(output, "w", driver = "ESRI Shapefile", schema = input.schema, crs = input.crs) as output_shp:
                # Write input contents into a shapefile 
                output_shp.writerecords(input)
        logging.info('Shapefile conversion completed!')

    def clip_vector(self, safes, tileframe):
        logging.info(" Clipping input vector based on data in raster directory...")
        tic = timeit.default_timer()
        tiles = []
        for safedir in safes:
            head, tail = os.path.split(safedir)
            tile = tail.split("_")[5][1:6]
            if tile not in tiles:
                tiles.append(tile)
        tileframe = tileframe[tileframe['Name'].isin(tiles)]

        gdf = self.geometries.to_crs(tileframe.crs)

        clipped_geodataframe = gpd.clip(gdf, tileframe) 
        toc = timeit.default_timer()
        logging.info(" Clipping took {} seconds.\n".format(math.ceil(toc-tic)))

        return clipped_geodataframe

 

    def read_tiles(self):
        tilepath = os.path.join(os.getcwd(), "sentinel2_tiles_world", "sentinel2_tiles_world.shp")
        tileframe = gpd.read_file(tilepath)
        return tileframe

    def reproject_geodataframe(self, geodataframe, crs):
        logging.info(" Reprojecting geodataframe...")
        reprojected = geodataframe.to_crs(crs)
        logging.info(" Reprojectiong completed.\n")
        return reprojected
    
    def filter_geodataframe(self, vectorframe, tileframe, tile, idname):
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