"""

class to handle everything regarding the vectordata, atm only ESRI shapefile
    
"""
import os
from osgeo import osr, ogr
import fiona
import subprocess
from copy import deepcopy
from shapely.geometry import Polygon
import logging
from shutil import copyfile
import re

class Geometry(object):

    def __init__(self, geometries):
        self.geometries = geometries 
    
    def split_path(self):
        #split shapefile path into parts for later use
        head, tail = os.path.split(self.geometries)
        root, ext = os.path.splitext(tail)
        return head,tail,root,ext

    def get_projectionfile(self):
        head,tail,root,ext = self.split_path()
        rootprj = root + '.prj'
        projectionfile = os.path.join(head, rootprj)
        return projectionfile

    def get_epsg(self):
        #ectract epsg code from prj file
        #open and read prj file
        projectionfile = self.get_projectionfile()
        prj_file = open(projectionfile , 'r')
        prj_text = prj_file.read()
        #extract spatial reference system information
        srs = osr.SpatialReference()
        srs.ImportFromESRI([prj_text])
        #translate to EPSG code
        srs.AutoIdentifyEPSG()
        epsgcode = srs.GetAuthorityCode(None)
    
        return epsgcode

    def reproject_to_epsg(self, myepsg):
        # reproject and save shapefiles to given EPSG code
        logging.info('Checking the projection of the inputfile now')
        epsgcode = self.get_epsg()
        head,tail,root,ext = self.split_path()

        # check if the shapefile is already in right projection
        if epsgcode == myepsg:
            logging.info('Input shapefile has EPSG {} that works!'.format(epsgcode))
        else:
            root = re.sub('_reprojected_\d*', '', root)
            reprojectedshape = os.path.join(head, root + '_reprojected_' + myepsg +  ext)
            if not os.path.exists(reprojectedshape):
                # use ogr commandline utility to reproject and save shapefile
                reprojectcommand = 'ogr2ogr -t_srs EPSG:' + myepsg + ' ' +  reprojectedshape + ' ' + self.geometries
                logging.info('Reprojectcommand: {}'.format(reprojectcommand))
                subprocess.call(reprojectcommand, shell=True)
                logging.info('input shapefile had other than EPSG {} but was reprojected and works now'.format(myepsg))
            #update the objects shapefile
            self.geometries = reprojectedshape

    def get_properties(self):
        # extract driver, schema and crs from shapefile
        with fiona.open(self.geometries,'r') as opengeom:
            driver = opengeom.driver
            schema = deepcopy(opengeom.schema)
            crs = opengeom.crs
            return driver,schema,crs
    
    def get_boundingbox(self):
        # extract bounding box Polygon object from shapefile 
        with fiona.open(self.geometries,'r') as open_shp:
            bounding_box_coordinates = open_shp.bounds
            logging.info(bounding_box_coordinates)
        return Polygon.from_bounds(bounding_box_coordinates[0], bounding_box_coordinates[1], bounding_box_coordinates[2], bounding_box_coordinates[3] )
        
    def get_convex_hull(self):
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
