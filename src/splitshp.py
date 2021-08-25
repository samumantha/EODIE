"""

class to split a shapefile with small polygons based on a shapefile with larger polygons to one shapefile per large polygon

authors: Petteri Lehti, Samantha Wittke

"""

import os
import sys
import fiona
import multiprocessing as mp
import shapely
from shapely.geometry import shape, Polygon
from copy import deepcopy
from osgeo import osr
import subprocess
import glob
import logging
import re
import yaml

class SplitshpObject(object):

    """
    Class to take care of preparing a shapefile for use in EODIE
    Attributes
    ----------
    fieldname: str
        name of the field in large polygon shapefile where tile information is stored
    output_driectory: str
        location where the splitted small polygon shapefile should be stored
    tiles: list of str
        list of tiles of large polygon shapefile that overlap with small polygon shapefile
    small_polygon_shapefile: str
        location and name of shapefile with polygons to be processed
    large_polygon_shapefile: str
        location and name of shapefile with polygons that the raster product is split into (tiles)
    """

    def __init__(self, small_polygon_shapefile, large_polygon_shapefile, shp_directory, fieldname test= False):
        """ initialize Spitshp object
        Parameters
        ----------
        small_polygon_shapefile: str
            location and name of shapefile with polygons to be processed
        large_polygon_shapefile: str
            location and name of shapefile with polygons that the raster product is split into (tiles)
        shp_directory: str
            location where the splitted small polygon shapefile should be stored
        fieldname: str
            name of the field in large polygon shapefile where tile information is stored
        test: boolean, default: False
            when testing, number of cpus to use should be 1
        """
        self.fieldname = fieldname
        self.output_directory = os.path.join(shp_directory, 'EODIE_temp_shp')
        self.tiles = []
        self.basename = None
        if not os.path.exists(self.output_directory):
            os.mkdir(self.output_directory)
        #all input shapefiles to EPSG: 4326
        self.small_polygon_shapefile = self.reproject_to_epsg(small_polygon_shapefile,'4326')
        self.large_polygon_shapefile = self.reproject_to_epsg(large_polygon_shapefile,'4326')
        self.test = test



    def reproject_to_epsg(self, myshp,myepsg):
        """ reprojecting a shapefile to another CRS based on EPSG code
        Parameters
        ----------
        myshp: str
            location and name of shapefile to be reprojected
        myepsg: str
            EPSG code to be reprojected to

        Returns
        --------
        reprojectedshape: str
            location and name of the reprojected shapefile
        """
        logging.info('checking the projection of the inputfile now')
        head, tail = os.path.split(myshp)
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
            logging.info('input shapefile has EPSG '  +myepsg + ' that works!')
            return myshp
        else:
            root = re.sub(r'_reprojected_\d*', '', root)
            reprojectedshape = os.path.join(self.output_directory, root + '_reprojected_' + myepsg +  ext)
            if not os.path.exists(reprojectedshape):
                reprojectcommand = 'ogr2ogr -t_srs EPSG:' + myepsg + ' ' +  reprojectedshape + ' ' + myshp
                #print(reprojectcommand)
                subprocess.call(reprojectcommand, shell=True)
                logging.info('input shapefile had other than EPSG ' + myepsg + ' but was reprojected and works now')
            return reprojectedshape



    def make_geometryobject(self, parameter_content):
        """ 
        Parameters
        -----------
        parameter_content:str
            information stored
        Returns
        --------
        geometryobject
            object of parameter_content
        """
        return shape(parameter_content)

    def get_shp_properties(self, shapefile):
        """ 
        Parameters
        -----------
        shapefile: object
            opened shapefile 
        Returns
        --------
        driver: str
            driver of the shapefile
        schema: str
            schema of the shapefile
        crs: str
            CRS of the shapefile
        """
        driver = shapefile.driver
        schema = deepcopy(shapefile.schema)
        crs = shapefile.crs
        return driver,schema,crs

    def get_bounding_box(self, shapefile):
        """ 
        Parameters
        -----------
        shapefile: str
            location and name of shapefile
        Returns
        --------
        polygon: object
            boundingbox for all features in shapefile
        """
        with fiona.open(shapefile,'r') as open_shp:
            bounding_box_coordinates = open_shp.bounds
            #print(bounding_box_coordinates)
        return Polygon.from_bounds(bounding_box_coordinates[0], bounding_box_coordinates[1], bounding_box_coordinates[2], bounding_box_coordinates[3] )


    def write_splitted_shapefiles(self, bounding_box_small_poly_shp,tile,outshpdir, small_poly_shp):
        """ creates and writes the shapefile with small polygons splitted according to large polygons (tiles)
        Parameters
        -----------
        bounding_box_small_poly_shp: object
            boundingbox for all features in shapefile
        tile: str 
            name of the tile
        outshpdir: str
            location where to store the results
        small_poly_shp: str
            location and name of the shapefile to be split 
        """
        one_tile_geometry = self.make_geometryobject(tile['geometry']) #on puhti: TypeError: 'NoneType' object is not subscriptable
        if one_tile_geometry.intersects(bounding_box_small_poly_shp):
            tilename = tile['properties'][self.fieldname]

            originalname = os.path.splitext(os.path.split(small_poly_shp)[-1])[0]
            outshpname = os.path.join(outshpdir,originalname + '_' + str(tilename)+'.shp')

            with fiona.open(small_poly_shp,'r') as smaller_open_shp:
                driver,schema,crs = self.get_shp_properties(smaller_open_shp)

                # open the new shapefile 
                with fiona.open(outshpname, 'w', driver,schema,crs) as outputshp:
                    for small_polygon in smaller_open_shp:
                        small_polygon_geometry = small_polygon['geometry']
                        if not small_polygon_geometry is None:
                            #only if there is the polygon is intersecting the tile in question, it will be written to the new file
                            # this is the point where there may be issues if the polygon is actually a multipolygon
                            # handling multipolygons at this stage is out of scope of the code at this point so not supported
                            #if shape(small_polygon['geometry']).within(one_tile_geometry):
                            if self.make_geometryobject(small_polygon_geometry).intersects(one_tile_geometry):                
                                outputshp.write({                                 
                                    'properties': small_polygon['properties'], 
                                    'geometry': small_polygon['geometry']})
                                    
                # if the shp is only 100 bytes it is empty and can be deleted
                self.remove_empty(outshpname)

    def remove_empty(self,outshpname):
        """ removes shapefiles that are created empty
        Parameters
        -----------
        outshpname: str
            name of the shapefile output
        """
        if os.path.getsize(outshpname) <= 100:
            filename = os.path.splitext(outshpname)[0]
            for ext in ['.shp','.shx','.dbf','.prj','.cpg']:
                if os.path.exists(filename + ext):
                    os.remove(filename + ext)


    def extract_needed_tiles(self, small_poly_shp, large_poly_shp, outshpname):
        """ adds tiles that overlap with small polygons to tiles list
        Parameters
        -----------
        small_poly_shp: str
                location and name of shapefile with polygons to be processed
        large_poly_shp: str
            location and name of shapefile with polygons that the raster product is split into (tiles)
        outshpname: str
            name of the output shapefile
        """

        bounding_box_small_poly_shp = self.get_bounding_box(small_poly_shp)

        with fiona.open(large_poly_shp,'r') as s2shp:
            driver,schema,crs = self.get_shp_properties(s2shp)

            with fiona.open(outshpname, 'w', driver,schema,crs) as outputshp:
                for tile in s2shp:
                    one_tile_geometry = self.make_geometryobject(tile['geometry'])
                    if one_tile_geometry.intersects(bounding_box_small_poly_shp):
                        self.tiles.append(tile['properties'][self.fieldname])
                        outputshp.write({                                 
                            'properties': tile['properties'], 
                            'geometry': tile['geometry']})


    def splitshp(self):
        """ run splithshape operation """
        self.splitshp_world()
        root = os.path.split(os.path.splitext(self.small_polygon_shapefile)[0])[1]
        self.basename = root
        largeroot = os.path.split(os.path.splitext(self.large_polygon_shapefile)[0])[1]
        exists = False
        for tile in self.tiles:
            exists = os.path.exists(os.path.join(self.output_directory, root + '_' + tile + '.shp' ))
            if not exists:
                break         
        if not exists:
            self.splitshp_mp()
            logging.info('splitted shapefiles now exist')
        else:
            logging.info('splitted shapefiles already exist')
        removelist = glob.glob(os.path.join(self.output_directory, largeroot + '_' + root + '.*'))
        for file in removelist:
            os.remove(file)
        logging.info('deleted splitted worldtiles')

    def splitshp_world(self):
        """ extract only tiles from large polygon shapefile that overlap with the boundingbox of small polygon shapefile"""
        #build the output name from both input files
        self.out_shape_name = os.path.join(self.output_directory, os.path.splitext(os.path.split(self.large_polygon_shapefile)[-1])[0] + '_' + os.path.split(self.small_polygon_shapefile)[-1] )

        self.extract_needed_tiles(self.small_polygon_shapefile, self.large_polygon_shapefile, self.out_shape_name)

    def splitshp_mp(self):
        """  run splitshape operation in parallel on available cores -2 cores split by tile"""
        self.large_polygon_shapefile = self.reproject_to_epsg(self.out_shape_name,'4326')

        bounding_box_small_poly_shp = self.get_bounding_box(self.small_polygon_shapefile)

        if self.test:
            usable_number_of_cores = 1
        else:
            usable_number_of_cores = mp.cpu_count()-2
        logging.info('number of usable cores for shapesplitting is ' + str(usable_number_of_cores))

        pool = mp.Pool(usable_number_of_cores)

        with fiona.open(self.large_polygon_shapefile,'r') as s2shp:
            for tile in s2shp:
                pool.apply_async(self.write_splitted_shapefiles, args = (bounding_box_small_poly_shp, tile, self.output_directory, self.small_polygon_shapefile))
            pool.close()
            pool.join()

    def delete_splitted_files(self):
        """ removes all files created by this class"""
        shp_remove_list = glob.glob(os.path.join(self.output_directory, '*'))  
        for file in shp_remove_list:
            os.remove(file)
        os.rmdir(self.output_directory)
        logging.info('deleted splitted shapefiles')



#running this class:
"""
small_polygon_shapefile = '' #shapefile to be split
shp_directory = '' # where to store results
world_tiles = '' #shapefile to split with
fieldname = '' #name of the field where tilename is stored (S2: 'Name', LS: 'PR')
SplitshpObject(small_polygon_shapefile, world_tiles, shp_directory, fieldname).splitshp()
# created shapefiles will be located in  shp_directory/EODIE_temp_shp
"""
