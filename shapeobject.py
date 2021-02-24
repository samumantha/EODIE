#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
object for shapefile

input: shapefile with path

- getAreaCode : returns Sentinel-2 tiles the shapefile intersects with
- polygonizeShape : if initial shapefile was points/lines, it returns polygonized features (buffered) 
- checkProjection : checks projection against a dependable and returns reprojected shapefile if necessary
- makeConvexHull : returns convex hull of the whole shapefile
- getBB : returns boundinxbox of whole shapefile
- getWKT : returns well known text format of shapefiles bounding box

written by: Samantha Wittke, FGI

last updated: 15.10.2020
"""


import os
import fiona
from fiona import collection
from osgeo import gdal, osr, ogr
from shapely.geometry import mapping, shape
#import myconfig as cfg
from shutil import copyfile
import subprocess


class ShapeObject(object):

    def __init__(self, theshape):
        self.theshape = theshape 
        self.shpname = os.path.splitext(os.path.split(self.theshape)[1])[0]
        

    def getAreaCode(self,s2tiles):
        #acodes = ['53SQV']
        #s2 tiles can be downloaded from here: http://ftpearth.bu.edu/public/emelaas/sentinel2_tiles_world/
        #s2tiles = '/u/58/wittkes3/unix/Documents/sentinel2_tiles_world/sentinel2_tiles_world.shp'
        if acodes == [] or acodes == ['']:
            print('getting acodes')
            acodes = []
            myshape = self.checkProjection('footprint')
            oshape = myshape.makeConvexHull().theshape
            records = fiona.open(oshape)
            geom1 = shape(records[0]['geometry'])
            for granules in fiona.open(s2tiles):
                #check intersection of input with granule
                if geom1.intersects(shape(granules['geometry'])):
                    intersecting = str(granules['properties']['Name'])
                    if intersecting not in acodes:
                        print('INFO: adding '+ intersecting +' to areacodes')
                        acodes.append(intersecting)
        return acodes

    #returns the path to theshape as is if its polygons, or path to newly created poligonized lines/points 
    def poligonizeShape(self):

        outputname = os.path.splitext(self.theshape)[0] + '_buffer.shp'
        openshape = fiona.open(self.theshape)
        geometrytype = openshape[0]['geometry']['type']

        if  geometrytype == 'Point' or geometrytype == 'LineString':
            copyfile(os.path.splitext(self.theshape)[0] + '.prj', os.path.splitext(outputname)[0] +'.prj' )
            schema = { 'geometry': 'Polygon', 'properties': { 'ID': 'str' } }
            with collection(outputname, "w", "ESRI Shapefile", schema) as output:
                for point in openshape:
                    output.write({
                        'properties': {'ID': point['properties']['ID']},
                        'geometry': mapping(shape(point['geometry']).buffer(cfg.buffer))})
            print('INFO: theshape was points or linestrings, now its polygon')
            return ShapeObject(output)
        else:
            return ShapeObject(output)
        print('INFO: theshape is polygons, that works')



    #checks the projection and if necessary reprojects the theshape based on a dependable
    def checkProjection(self, dependable):
        print('INFO: checking the projection dependent on '+ dependable +' of the inputfile now')
        head, tail = os.path.split(self.theshape)
        root, ext = os.path.splitext(tail)
        print(self.theshape)
        print(dependable)
        if dependable == 'footprint':
            rootprj = root + '.prj'
            projectionfile = os.path.join(head, rootprj)
            prj_file = open(projectionfile , 'r')
            prj_text = prj_file.read()
            srs = osr.SpatialReference()
            srs.ImportFromESRI([prj_text])
            srs.AutoIdentifyEPSG()
            epsgcode = srs.GetAuthorityCode(None)
            if epsgcode == '4326':
                print('INFO: input shapefile has EPSG 4326, that works!')
                return self
            else:
                reprojectedshape = os.path.join(head, root + '_reprojected_4326'+ ext)
                reprojectcommand = 'ogr2ogr -t_srs EPSG:4326 ' + reprojectedshape + ' ' + self.theshape
                subprocess.call(reprojectcommand, shell=True)
                print('INFO: input shapefile had other than EPSG 4326, but was reprojected and works now')
                return ShapeObject(reprojectedshape)
        else:
            dtail = os.path.split(dependable)[1]
            beg = os.path.split(dependable)[0]
            droot, dext =  os.path.splitext(dtail)
            if dext == '.shp':
                projectionfile = droot + '.prj'
                projectionfile = os.path.join(beg, projectionfile)
                prj_file = open(projectionfile , 'r')
                prj_text = prj_file.read()
                srs = osr.SpatialReference()
                srs.ImportFromESRI([prj_text])
                srs.AutoIdentifyEPSG()
                epsgcode = srs.GetAuthorityCode(None)
                reprojectedshape = os.path.join(head, root + '_reprojected_'+epsgcode+ ext)
                reprojectcommand = 'ogr2ogr -t_srs EPSG: '+epsgcode + reprojectedshape + ' ' + self.theshape
                subprocess.call(reprojectcommand, shell=True)
                copyfile(os.path.splitext(self.theshape)[0] + '.prj', os.path.splitext(reprojectedshape)[0] +'.prj' )
                print('INFO: ' + self.theshape + ' was reprojected to EPSG code: ' + epsgcode + ' based on the projection of ' + dependable)
                return ShapeObject(reprojectedshape)
            else: # we assume its a raster file
                rasterfile = gdal.Open(dependable)
                rasterprojection = rasterfile.GetProjection()
                rasterrs = osr.SpatialReference(wkt=rasterprojection)
                rasterepsg = rasterrs.GetAttrValue('AUTHORITY',1)
                ##reproject the shapefile according to projection of Sentinel2/raster image
                reprojectedshape = os.path.join(head, root + '_reprojected_'+ rasterepsg+ ext)
                reprojectcommand = 'ogr2ogr -t_srs EPSG:'+rasterepsg+' ' + reprojectedshape + ' ' + self.theshape
                subprocess.call(reprojectcommand, shell=True)
                print('INFO: ' + self.theshape + ' was reprojected to EPSG code: ' + rasterepsg + ' based on the projection of ' + dependable)
                return ShapeObject(reprojectedshape)
    
    def makeConvexHull(self):
        # based on https://pcjericks.github.io/py-gdalogr-cookbook/vector_layers.html
        # Get a Layer
        #print(self.theshape)
        inDriver = ogr.GetDriverByName("ESRI Shapefile")
        inDataSource = inDriver.Open(self.theshape, 0)
        inLayer = inDataSource.GetLayer()

        # Collect all Geometries
        geomcol = ogr.Geometry(ogr.wkbGeometryCollection)
        #print(geomcol)
        for feature in inLayer:
            print(feature)
            geomcol.AddGeometry(feature.GetGeometryRef())
            #print(geomcol)

        # Calculate convex hull
        convexhull = geomcol.ConvexHull()

        # Save extent to a new Shapefile
        convexhullp = os.path.splitext(self.theshape)[0] + '_convexhull.shp'
        outDriver = ogr.GetDriverByName("ESRI Shapefile")
        copyfile(os.path.splitext(self.theshape)[0] + '.prj', os.path.splitext(convexhullp)[0] + '.prj' )

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

        return ShapeObject(convexhullp)

    def getBB(self):
        with fiona.open(self.theshape) as openshape:
            bb = openshape.bounds
            bbstring = str(bb[0])+","+str(bb[1])+":"+str(bb[2])+","+str(bb[3])
            print('INFO: created boundingbox for '+ self.theshape + ': '+ bbstring)
        return bbstring

    def getWKT(self):
        with fiona.open(self.theshape) as openshape:
            bb = openshape.bounds
            bbstring = str(bb[0])+" "+str(bb[1])+"," +str(bb[2]) +' ' + str(bb[1]) +','  +str(bb[2])+" "+str(bb[3]) + ',' +str(bb[0])+" "+str(bb[3]) +','+str(bb[0])+" "+str(bb[1])
            print('INFO: created wkt for boundingbox for '+ self.theshape + ': '+ bbstring)
        return bbstring
