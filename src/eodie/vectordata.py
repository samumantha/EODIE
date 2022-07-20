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

    def __init__(self, geometries):
        """Initialize vectordata object.

        Parameters
        -----------
        geometries: str
            location and name of a vectorfile
        """
        logging.info(" Reading vectorfile into a geodataframe...")
        self.geometries = gpd.read_file(geometries)
        logging.info(" Geodataframe read!\n")

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
        """Extract epsg code from prj file.

        Returns
        --------
        vectorepsg: str
            EPSG code of the vectorfile
        """
        # Open shapefile
        with fiona.open(self.geometries, "r") as proj:
            # Read spatial reference
            spatialRef = proj.crs
            # Extract epsgcode from the reference
            epsgcode = spatialRef["init"].split(":")[1]

        return epsgcode

    def reproject_to_epsg(self, rasterepsg):
        """Reproject shapefile to given EPSG code, save as new shapefile file.

        Parameters
        -----------
        rasterepsg: str
            EPSG code to reproject the vectorfile to
        """
        # reproject and save shapefiles to given EPSG code
        logging.info('Checking the projection of the inputfile now...')
        vectorepsg = self.get_epsg()
        head,_,root,ext = self._split_path()

        # check if the shapefile is already in right projection
        if vectorepsg == rasterepsg:
            logging.info(' Input shapefile has EPSG {} that works!'.format(vectorepsg))
        else:
            root = re.sub(r'_reprojected_\d*', '', root)
            reprojectedshape = os.path.join(head, root + '_reprojected_' + rasterepsg +  ext)
            if not os.path.exists(reprojectedshape):             

                # Determine the spatial reference systems for input and output
                input_epsg = 'EPSG:' + vectorepsg
                output_epsg = 'EPSG:' + rasterepsg

                # Define options for gdal.VectorTranslate
                gdal_options = gdal.VectorTranslateOptions(format = "ESRI Shapefile", reproject = True, dstSRS=output_epsg, srcSRS=input_epsg)

                # Run gdal.VectorTranslate
                gdal.VectorTranslate(destNameOrDestDS=reprojectedshape, srcDS=self.geometries, options=gdal_options)

                logging.info(' {} had other than EPSG:{} but was reprojected and works now'.format(self.geometries, rasterepsg))
                
            #update the objects shapefile
            self.geometries = reprojectedshape

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
        """Extract convex hull of given shapefile, save to new shapefile; adjusted from https://pcjericks.github.io/py-gdalogr-cookbook/vector_layers.html#save-the-convex-hull-of-all-geometry-from-an-input-layer-to-an-output-layer.

        Returns
        --------
        convexhull: str
            location and name of the created convexhull of vectorfile
        """
        # Get a Layer
        #inDriver = ogr.GetDriverByName("ESRI Shapefile")
        #inDataSource = inDriver.Open(self.geometries, 0)
        #inLayer = inDataSource.GetLayer()
        # Collect all Geometry
        #geomcol = ogr.Geometry(ogr.wkbGeometryCollection)
        #for feature in inLayer:
            #geomcol.AddGeometry(feature.GetGeometryRef())
        # Calculate convex hull
        #convexhull = geomcol.ConvexHull()
        #print(convexhull.GetGeometryType)
        #print("CONVEXHULL IS: {}".format(convexhull))
        #print(type(convexhull))
        #geoseries = gpd.GeoSeries.from_wkb(convexhull, crs = "EPSG:4326")
        #print(geoseries)
    
        #convexhullgdf = gpd.GeoDataFrame(index = [0], crs = "epsg:4326", geometry=[convexhull])
        #print(convexhullgdf)
        #convexhullp = os.path.splitext(self.geometries)[0] + "_convexhull.shp"
        #convexhullgdf.to_file(convexhullp) 
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
        chdf = gpd.GeoDataFrame(crs = geodataframe.crs, geometry=[ch])
        toc = timeit.default_timer()
        logging.info(" Creating convex hull from unary union took {} seconds.\n".format(math.ceil(toc-tic)))
        



       
        # Save extent to a new Shapefile
        #convexhullp = os.path.splitext(self.geometries)[0] + "_convexhull.shp"
        #outDriver = ogr.GetDriverByName("ESRI Shapefile")
        #copyfile(
            #os.path.splitext(self.geometries)[0] + ".prj",
            #os.path.splitext(convexhullp)[0] + ".prj",
        #)
        # Remove output shapefile if it already exists
        #if os.path.exists(convexhullp):
            #outDriver.DeleteDataSource(convexhullp)
        # Create the output shapefile
        #outDataSource = outDriver.CreateDataSource(convexhullp)
        #outLayer = outDataSource.CreateLayer("convexhull", geom_type=ogr.wkbPolygon)
        # Add an ID field
        #idField = ogr.FieldDefn("ID", ogr.OFTInteger)
        #outLayer.CreateField(idField)
        # Create the feature and set values
        #featureDefn = outLayer.GetLayerDefn()
        #feature = ogr.Feature(featureDefn)
        #feature.SetGeometry(convexhull)
        #feature.SetField("ID", 1)
        #outLayer.CreateFeature(feature)
        #feature = None
        # Save and close DataSource
        #inDataSource = None
        #outDataSource = None
        
        return chdf

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
            logging.info(" All features have geometries.")

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
        # Read shapefile into a geopandas data frame
        vectorfile = gpd.read_file(self.geometries)
        # Check empty geometries
        self.check_empty(vectorfile)
        # Check validity of geometries
        vectorfile["validity"] = vectorfile["geometry"].is_valid
        # Extract only rows with existing geometries
        vectorfile_with_geom = vectorfile.loc[vectorfile["geometry"] != None].copy()
        # Filter rows where geometries were invalid
        vectorfile_with_invalid_geom = vectorfile_with_geom.loc[
            vectorfile_with_geom["validity"] == False
        ].copy()
        # If invalid geometries exist, run explain_validity for them
        if len(vectorfile_with_invalid_geom) > 0:
            vectorfile_with_invalid_geom[
                "explanation"
            ] = vectorfile_with_invalid_geom.apply(
                lambda row: explain_validity(row.geometry), axis=1
            )
            logging.info(
                " Following features have invalid geometries:\n\n {}".format(
                    vectorfile_with_invalid_geom
                )
            )
        else:
            logging.info(" All features have valid geometries.")

        # If --delete_invalid_geometries was defined, rewrite a new file without invalid geometries.
        if drop:
            # Extract filepath
            head, _, root, ext = self._split_path()
            # Build output filename and path
            outputfilename = root + "_valid" + ext
            outputpath = os.path.join(head, outputfilename)

            # Filter only valid geometries
            vectorfile_with_valid_geom = vectorfile_with_geom.loc[
                vectorfile_with_geom["validity"] == True
            ].copy()
            # Write a file from the geodataframe
            vectorfile_with_valid_geom.to_file(outputpath, index=False)

            return outputpath

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

        """
        if args.dir is not None:
    # Glob all SAFE files in dir
    safes = glob.glob(os.path.join(args.dir, "*.SAFE"))   
    # Create an empty list for tiles
    tiles = []
    # Loop through safes
    for safedir in safes:
        # Extract SAFE file name
        head, tail = os.path.split(safedir)
        # Read tilecode without beginning T
        tile = tail.split("_")[5][1:6]            
        # If tilecode is not in tiles, add it
        if tile not in tiles:
            tiles.append(tile)  
    
    # Get parent directory
    parent_dir = os.path.abspath(os.path.join(os.getcwd(), os.pardir))
    # Read Sentinel-2 tiles into a geodataframe
    tileframe = gpd.read_file(os.path.join(parent_dir, 'src', 'sentinel2_tiles_world', 'sentinel2_tiles_world.shp'))
    print("Tileframe read to a dataframe")
    # Only select rows where tilename can be found in the list of tiles
    tileframe = tileframe[tileframe['Name'].isin(tiles)]    
    
    # Reproject if necessary
    if not vectorfile.crs == tileframe.crs:
        print("Inputs are in different coordinate reference system, reprojecting...")
        vectorfile.to_crs(crs = tileframe.crs, inplace = True)   
        print("Reprojection completed.")
    
    print("Clipping {} based on data in {}.".format(args.vector, args.dir))
    # Clip
    clipped_vectorfile = gpd.clip(vectorfile, tileframe, keep_geom_type = True)
    # Write output to a file
    clipped_vectorfile.to_file(outputpath)
    print("Clipped vectorfile was written to {}".format(outputpath))
    """