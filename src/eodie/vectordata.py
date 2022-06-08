"""

class to handle everything regarding the vectordata, atm only ESRI shapefile
    
authors: Samantha Wittke

"""
import os
from osgeo import osr, ogr, gdal
import fiona
from copy import deepcopy
from shapely.geometry import Polygon
import logging
from shutil import copyfile
import re

class VectorData(object):
    """ Vector data related information and transformations
    Attributes
    -----------
    geometries: str
        location and name of a vectorfile
    """

    def __init__(self, geometries):
        """ initialize vectordata object
        Parameters
        -----------
        geometries: str
            location and name of a vectorfile
        """
        self.geometries = geometries 
    
    def _split_path(self):
        """ split shapefile path into parts
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
        return head,tail,root,ext

    def get_epsg(self):
        """ extract epsg code from prj file
        Returns
        --------
        vectorepsg: str
            EPSG code of the vectorfile
        """

        # Open shapefile
        with fiona.open(self.geometries,'r') as proj:
            # Read spatial reference 
            spatialRef = proj.crs
            # Extract epsgcode from the reference
            vectorepsg = spatialRef['init'].split(":")[1]           

        return vectorepsg

    def reproject_to_epsg(self, rasterepsg):
        """ reproject shapefile to given EPSG code, save as new shapefile file
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
            logging.info('Input shapefile has EPSG {} that works!'.format(vectorepsg))
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

                logging.info('Input shapefile had other than EPSG {} but was reprojected and works now'.format(rasterepsg))

                
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
        with fiona.open(self.geometries,'r') as opengeom:
            driver = opengeom.driver
            schema = deepcopy(opengeom.schema)
            crs = opengeom.crs
            return driver,schema,crs
    
    def get_boundingbox(self):
        """ extract bounding box Polygon object from shapefile 
        Returns
        --------
        boundingbox: object
            polygon object of the boundingbox for the whole vectorfile
        """
        with fiona.open(self.geometries,'r') as open_vectordata:
            bounding_box_coordinates = open_vectordata.bounds
            logging.info(bounding_box_coordinates)
        return Polygon.from_bounds(bounding_box_coordinates[0], bounding_box_coordinates[1], bounding_box_coordinates[2], bounding_box_coordinates[3] )
        
    def get_convex_hull(self):
        """ extract convex hull of given shapefile, save to new shapefile; adjusted from https://pcjericks.github.io/py-gdalogr-cookbook/vector_layers.html#save-the-convex-hull-of-all-geometry-from-an-input-layer-to-an-output-layer
        Returns
        --------
        convexhull: str
            location and name of the created convexhull of vectorfile
        """
        # Get a Layer
        inDriver = ogr.GetDriverByName("ESRI Shapefile")
        inDataSource = inDriver.Open(self.geometries, 0)
        inLayer = inDataSource.GetLayer()
        # Collect all Geometry
        geomcol = ogr.Geometry(ogr.wkbGeometryCollection)
        for feature in inLayer:
            geomcol.AddGeometry(feature.GetGeometryRef())
        # Calculate convex hull
        convexhull = geomcol.ConvexHull()
        # Save extent to a new Shapefile
        convexhullp = os.path.splitext(self.geometries)[0] + '_convexhull.shp'
        outDriver = ogr.GetDriverByName("ESRI Shapefile")
        copyfile(os.path.splitext(self.geometries)[0] + '.prj', os.path.splitext(convexhullp)[0] + '.prj' )
        # Remove output shapefile if it already exists
        if os.path.exists(convexhullp):
            outDriver.DeleteDataSource(convexhullp)
        # Create the output shapefile
        outDataSource = outDriver.CreateDataSource(convexhullp)
        outLayer = outDataSource.CreateLayer("convexhull", geom_type=ogr.wkbPolygon)
        # Add an ID field
        idField = ogr.FieldDefn("ID", ogr.OFTInteger)
        outLayer.CreateField(idField)
        # Create the feature and set values
        featureDefn = outLayer.GetLayerDefn()
        feature = ogr.Feature(featureDefn)
        feature.SetGeometry(convexhull)
        feature.SetField("ID", 1)
        outLayer.CreateFeature(feature)
        feature = None
        # Save and close DataSource
        inDataSource = None
        outDataSource = None

        return convexhullp


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
