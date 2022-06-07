"""

class to handle everything regarding the vectordata, atm only ESRI shapefile
    
authors: Samantha Wittke

"""
import os
from osgeo import osr, ogr
import fiona
import subprocess
from copy import deepcopy
from shapely.geometry import Polygon
import shapely
import geopandas as gpd
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

    def get_projectionfile(self):
        """ get path to the projectionfile that is associated with the shapefile
        Returns
        --------
        projectionfile: str
            the projectionfile belonging to the vectorfile
        """
        head,_ ,root,_ = self._split_path()
        rootprj = root + '.prj'
        projectionfile = os.path.join(head, rootprj)
        return projectionfile

    def get_epsg(self):
        """ extract epsg code from prj file
        Returns
        --------
        epsgcode: str
            EPSG code of the vectorfile
        """
        # Open shapefile
        with fiona.open(self.geometries,'r') as proj:
            # Read spatial reference 
            spatialRef = proj.crs
            # Extract epsgcode from the reference
            epsgcode = spatialRef['init'].split(":")[1]           
    
        return epsgcode

    def reproject_to_epsg(self, myepsg):
        """ reproject shapefile to given EPSG code, save as new shapefile file
        Parameters
        -----------
        myepsg: str
            EPSG code to reproject the vectorfile to
        """
        # reproject and save shapefiles to given EPSG code
        logging.info(' Checking the projection of the inputfile now')
        epsgcode = self.get_epsg()
        head,_,root,ext = self._split_path()

        # check if the shapefile is already in right projection
        if epsgcode == myepsg:
            logging.info('Input shapefile has EPSG {} that works!'.format(epsgcode))
        else:
            root = re.sub(r'_reprojected_\d*', '', root)
            reprojectedshape = os.path.join(head, root + '_reprojected_' + myepsg +  ext)
            if not os.path.exists(reprojectedshape):
                # use ogr commandline utility to reproject and save shapefile
                reprojectcommand = 'ogr2ogr -t_srs EPSG:' + myepsg + ' ' +  reprojectedshape + ' ' + self.geometries
                logging.info('Reprojectcommand: {}'.format(reprojectcommand))
                subprocess.call(reprojectcommand, shell=True)
                logging.info(' Input shapefile had other than EPSG {} but was reprojected and works now'.format(myepsg))
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
        with fiona.open(self.geometries,'r') as open_shp:
            bounding_box_coordinates = open_shp.bounds
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

    def check_validity(self):
        """ Check the validity of each polygon in the vectorfile. Invalid geometries will be excluded from the calculations; saves a new shapefile without the invalid polygons, if any exist.
        Returns:
            path to the shapefile to continue processing with (either original or filtered one)
        """
        # Read shapefile into a geopandas data frame
        vectorfile = gpd.read_file(self.geometries)         
        # Filter out rows where 'geometry' is None     
        vectorfile_geometries = vectorfile.loc[vectorfile['geometry'] != None].copy()  
        # Check if there are erroneus features without geometries:
        if (len(vectorfile.loc[vectorfile['geometry'] == None]) > 0):
            logging.info(" Number of objects with no geometry: {}".format(len(vectorfile.loc[vectorfile['geometry'] == None])))
        # For existing geometries, create a boolean column 'validity' 
        vectorfile_geometries['validity'] = vectorfile_geometries['geometry'].is_valid        
        # Filter valid geometries into a new dataframe copy.   
        valid = vectorfile_geometries.loc[vectorfile_geometries['validity'] == True].copy()    
        # Compare the row numbers of original file and filtered file and save files accordingly
        if (len(valid) < len(vectorfile)):        
            logging.info(" Number of objects with invalid geometry: {}".format(len(vectorfile) - len(valid)))
            # Extract filepath
            head,_ ,root,_ = self._split_path()
            # Build output filename
            outputfilename = root + "_valid.shp"
            # Save the valid file and proceed with that
            valid.to_file(os.path.join(head, outputfilename), index = False)   
            logging.info(" A vectorfile with only valid geometries has been written.")
            # Return the new filename to continue processing.         
            return os.path.join(head, outputfilename)
        else:
            # If nothing was changed, continue with the original file. 
            logging.info(" All geometries of {} are valid.".format(self.geometries))
            return self.geometries