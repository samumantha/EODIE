"""
TODO:
    * no fileoutput from reprojection
"""
import os
from osgeo import gdal,osr
import fiona

class GeometryObject(object):

    def __init__(self, geometries):
        self.geometries = geometries 

    def reproject_to_epsg(self, myepsg):
        print('INFO: checking the projection of the inputfile now')
        head, tail = os.path.split(self.geometries)
        root, ext = os.path.splitext(tail)
        rootprj = root + '.prj'
        projectionfile = os.path.join(head, rootprj)
        prj_file = open(projectionfile , 'r')
        prj_text = prj_file.read()
        srs = osr.SpatialReference()
        srs.ImportFromESRI([prj_text])
        srs.AutoIdentifyEPSG()
        epsgcode = srs.GetAuthorityCode(None)
        if epsgcode == myepsg:
            print('INFO: input shapefile has EPSG ' + epsgcode + ' that works!')
            return self.geometries
        else:
            reprojectedshape = os.path.join(head, root + '_reprojected_' + myepsg +  ext)
            if not os.path.exists(reprojectedshape):
                reprojectcommand = 'ogr2ogr -t_srs EPSG:' + myepsg + ' ' +  reprojectedshape + ' ' + myshp
                print(reprojectcommand)
                subprocess.call(reprojectcommand, shell=True)
                print('INFO: input shapefile had other than EPSG ' + myepsg + ' but was reprojected and works now')
            return GeometryObject(reprojectedshape)

    def get_properties(self):
        driver = self.geometries.driver
        schema = deepcopy(self.geometries.schema)
        crs = self.geometries.crs
        return driver,schema,crs

    def get_boundingbox(self):
        with fiona.open(self.geometries,'r') as open_shp:
            bounding_box_coordinates = open_shp.bounds
            print(bounding_box_coordinates)
        return Polygon.from_bounds(bounding_box_coordinates[0], bounding_box_coordinates[1], bounding_box_coordinates[2], bounding_box_coordinates[3] )