"""

class to handle everything regarding the vectordata, atm only ESRI shapefile

TODO:
    
"""
import os
from osgeo import osr
import fiona
import subprocess
from copy import deepcopy
from shapely.geometry import Polygon
import logging

class GeometryObject(object):

    def __init__(self, geometries):
        self.geometries = geometries 
    
    def split_path(self):
        head, tail = os.path.split(self.geometries)
        root, ext = os.path.splitext(tail)
        return head,tail,root,ext

    def get_projectionfile(self):
        head,tail,root,ext = self.split_path()
        rootprj = root + '.prj'
        projectionfile = os.path.join(head, rootprj)
        return projectionfile

    def get_epsg(self):

        projectionfile = self.get_projectionfile()
        prj_file = open(projectionfile , 'r')
        prj_text = prj_file.read()
        srs = osr.SpatialReference()
        srs.ImportFromESRI([prj_text])
        srs.AutoIdentifyEPSG()
        epsgcode = srs.GetAuthorityCode(None)
    
        return epsgcode

    def reproject_to_epsg(self, myepsg):
        logging.info('Checking the projection of the inputfile now')
        epsgcode = self.get_epsg()
        head,tail,root,ext = self.split_path()

        if epsgcode == myepsg:
            logging.info('Input shapefile has EPSG {} that works!'.format(epsgcode))
        else:
            reprojectedshape = os.path.join(head, root + '_reprojected_' + myepsg +  ext)
            if not os.path.exists(reprojectedshape):
                reprojectcommand = 'ogr2ogr -t_srs EPSG:' + myepsg + ' ' +  reprojectedshape + ' ' + self.geometries
                logging.info('Reprojectcommand: {}'.format(reprojectcommand))
                subprocess.call(reprojectcommand, shell=True)
                logging.info('input shapefile had other than EPSG {} but was reprojected and works now'.format(myepsg))
            self.geometries = reprojectedshape

    def get_properties(self):
        with fiona.open(self.geometries,'r') as opengeom:
            driver = opengeom.driver
            schema = deepcopy(opengeom.schema)
            crs = opengeom.crs
            return driver,schema,crs
    
    def get_boundingbox(self):
        with fiona.open(self.geometries,'r') as open_shp:
            bounding_box_coordinates = open_shp.bounds
            logging.info(bounding_box_coordinates)
        return Polygon.from_bounds(bounding_box_coordinates[0], bounding_box_coordinates[1], bounding_box_coordinates[2], bounding_box_coordinates[3] )
    