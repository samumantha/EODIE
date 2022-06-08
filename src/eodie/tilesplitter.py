"""

class to split a vectorfile with small polygons based on a vectorfile with larger polygons to one vectorfile per large polygon

authors: Petteri Lehti, Samantha Wittke

"""

import os
import sys
import fiona
import multiprocessing as mp
from shapely.geometry import shape, Polygon
from copy import deepcopy
from osgeo import osr, gdal
import glob
import logging
import re
import yaml

class TileSplitter(object):

    """
    Class to take care of preparing a vectorfile for use in EODIE
    Attributes
    ----------
    fieldname: str
        name of the field in large polygon vectorfile where tile information is stored
    output_driectory: str
        location where the splitted small polygon vectorfile should be stored
    tiles: list of str
        list of tiles of large polygon vectorfile that overlap with small polygon vectorfile
    small_polygon_vectorfile: str
        location and name of vectorfile with polygons to be processed
    large_polygon_vectorfile: str
        location and name of vectorfile with polygons that the raster product is split into (tiles)
    """

    def __init__(self, small_polygon_vectorfile, large_polygon_vectorfile, vector_directory, fieldname, test= False):
        """ initialize TileSplitter object
        Parameters
        ----------
        small_polygon_vectorfile: str
            location and name of vectorfile with polygons to be processed
        large_polygon_vectorfile: str
            location and name of vectorfile with polygons that the raster product is split into (tiles)
        vector_directory: str
            location where the splitted small polygon vectorfile should be stored
        fieldname: str
            name of the field in large polygon vectorfile where tile information is stored
        test: boolean, default: False
            when testing, number of cpus to use should be 1
        """
        self.fieldname = fieldname
        self.output_directory = os.path.join(vector_directory, 'EODIE_temp')
        self.tiles = []
        self.basename = None
        if not os.path.exists(self.output_directory):
            os.mkdir(self.output_directory)
        #all input vectorfiles to EPSG: 4326
        self.small_polygon_vectorfile = self.reproject_to_epsg(small_polygon_vectorfile,'4326')
        self.large_polygon_vectorfile = self.reproject_to_epsg(large_polygon_vectorfile,'4326')
        self.test = test



    def reproject_to_epsg(self, vectorfile, myepsg):
        """ reprojecting a vectorfile to another CRS based on EPSG code
        Parameters
        ----------
        vectorfile : str
            location and name of vectorfile to be reprojected
        myepsg: str
            EPSG code to be reprojected to

        Returns
        --------
        reprojectedvectorfile: str
            location and name of the reprojected vectorfile
        """
        logging.info('Checking the projection of the inputfile now...')
        with fiona.open(vectorfile,'r') as proj:
            # Read spatial reference 
            spatialRef = proj.crs
            # Extract epsgcode from the reference
            vectorepsg = spatialRef['init'].split(":")[1]   

        # If vector EPSG matches input EPSG, no conversion needed
        if vectorepsg == myepsg:
            logging.info('Input vector has EPSG '  +myepsg + ' that works!')
            return vectorfile
        else:
            logging.info('Input vector has EPSG {} that will be reprojected to EPSG {}'.format(vectorepsg, myepsg))
            # Extract filename and extension from vectorfile
            tail = os.path.split(vectorfile)[1]
            # Separate basename and extension
            root, ext = os.path.splitext(tail)
            root = re.sub(r'_reprojected_\d*', '', root)
            reprojectedvectorfile = os.path.join(self.output_directory, root + '_reprojected_' + myepsg +  ext)
            if not os.path.exists(reprojectedvectorfile):             

                # Determine the spatial reference systems for input and output
                input_epsg = 'EPSG:' + vectorepsg
                output_epsg = 'EPSG:' + myepsg

                # Define options for gdal.VectorTranslate
                gdal_options = gdal.VectorTranslateOptions(format = "ESRI Shapefile", reproject = True, dstSRS=output_epsg, srcSRS=input_epsg)

                # Run gdal.VectorTranslate
                gdal.VectorTranslate(destNameOrDestDS=reprojectedvectorfile, srcDS=vectorfile, options=gdal_options)

                logging.info('Input vectorfile had other than EPSG {} but was reprojected and works now'.format(myepsg))

            return reprojectedvectorfile


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

    def get_vector_properties(self, vectorfile):
        """ 
        Parameters
        -----------
        vectorfile: object
            opened vectorfile 
        Returns
        --------
        driver: str
            driver of the vectorfile
        schema: str
            schema of the vectorfile
        crs: str
            CRS of the vectorfile
        """
        driver = vectorfile.driver
        schema = deepcopy(vectorfile.schema)
        crs = vectorfile.crs
        return driver,schema,crs

    def get_bounding_box(self, vectorfile):
        """ 
        Parameters
        -----------
        vectorfile: str
            location and name of vectorfile
        Returns
        --------
        polygon: object
            boundingbox for all features in vectorfile
        """
        with fiona.open(vectorfile,'r') as open_vectordata:
            bounding_box_coordinates = open_vectordata.bounds
            #print(bounding_box_coordinates)
        return Polygon.from_bounds(bounding_box_coordinates[0], bounding_box_coordinates[1], bounding_box_coordinates[2], bounding_box_coordinates[3] )


    def write_splitted_tiles(self, bounding_box_small_poly,tile,out_vector_dir, small_poly_vectorfile):
        """ creates and writes the vectorfile with small polygons splitted according to large polygons (tiles)
        Parameters
        -----------
        bounding_box_small_poly: object
            boundingbox for all features in vectorfile
        tile: str 
            name of the tile
        out_vector_dir: str
            location where to store the results
        small_poly_vectorfile: str
            location and name of the vectorfile to be split 
        """
        one_tile_geometry = self.make_geometryobject(tile['geometry']) 
        if one_tile_geometry.intersects(bounding_box_small_poly):
            tilename = tile['properties'][self.fieldname]

            originalname = os.path.splitext(os.path.split(small_poly_vectorfile)[-1])[0]
            out_vector_name = os.path.join(out_vector_dir,originalname + '_' + str(tilename)+'.shp')

            with fiona.open(small_poly_vectorfile,'r') as smaller_open_vectordata:
                driver,schema,crs = self.get_vector_properties(smaller_open_vectordata)

                # open the new vectorfile 
                with fiona.open(out_vector_name, 'w', driver,schema,crs) as output_vectordata:
                    for small_polygon in smaller_open_vectordata:
                        small_polygon_geometry = small_polygon['geometry']
                        if not small_polygon_geometry is None:
                            #only if there is the polygon is intersecting the tile in question, it will be written to the new file
                            # this is the point where there may be issues if the polygon is actually a multipolygon
                            # handling multipolygons at this stage is out of scope of the code at this point so not supported
                            #if shape(small_polygon['geometry']).within(one_tile_geometry):
                            if self.make_geometryobject(small_polygon_geometry).intersects(one_tile_geometry):                
                                output_vectordata.write({                                 
                                    'properties': small_polygon['properties'], 
                                    'geometry': small_polygon['geometry']})
                                    
                # if the vectorfile is only 100 bytes it is empty and can be deleted
                self.remove_empty(out_vector_name)

    def remove_empty(self,out_vector_name):
        """ removes vectorfiles that are created empty
        Parameters
        -----------
        out_vector_name: str
            name of the vectorfile output
        """
        if os.path.getsize(out_vector_name) <= 100:
            filename = os.path.splitext(out_vector_name)[0]
            for ext in ['.shp','.shx','.dbf','.prj','.cpg']:
                if os.path.exists(filename + ext):
                    os.remove(filename + ext)


    def extract_needed_tiles(self, small_poly_vectorfile, large_poly_vectorfile, out_vector_name):
        """ adds tiles that overlap with small polygons to tiles list
        Parameters
        -----------
        small_poly_vectorfile: str
                location and name of vectorfile with polygons to be processed
        large_poly_vectorfile: str
            location and name of vectorfile with polygons that the raster product is split into (tiles)
        out_vector_name: str
            name of the output vectorfile
        """

        bounding_box_small_poly = self.get_bounding_box(small_poly_vectorfile)

        with fiona.open(large_poly_vectorfile,'r') as large_poly_vector_open:
            driver,schema,crs = self.get_vector_properties(large_poly_vector_open)

            with fiona.open(out_vector_name, 'w', driver,schema,crs) as output_vectordata:
                for tile in large_poly_vector_open:
                    one_tile_geometry = self.make_geometryobject(tile['geometry'])
                    if one_tile_geometry.intersects(bounding_box_small_poly):
                        self.tiles.append(tile['properties'][self.fieldname])
                        output_vectordata.write({                                 
                            'properties': tile['properties'], 
                            'geometry': tile['geometry']})


    def tilesplit(self):
        """ run splithshape operation """
        self.tilesplit_world()
        root = os.path.split(os.path.splitext(self.small_polygon_vectorfile)[0])[1]
        self.basename = root
        largeroot = os.path.split(os.path.splitext(self.large_polygon_vectorfile)[0])[1]
        exists = False
        for tile in self.tiles:
            exists = os.path.exists(os.path.join(self.output_directory, root + '_' + tile + '.shp' ))
            if not exists:
                break         
        if not exists:
            self.tilesplit_mp()
            logging.info('splitted vectordata by tile now exist')
        else:
            logging.info('splitted vectordata by tile already exist')
        removelist = glob.glob(os.path.join(self.output_directory, largeroot + '_' + root + '.*'))
        for file in removelist:
            os.remove(file)
        logging.info('deleted splitted worldtiles')

    def tilesplit_world(self):
        """ extract only tiles from large polygon vectorfile that overlap with the boundingbox of small polygon vectorfile"""
        #build the output name from both input files
        self.out_shape_name = os.path.join(self.output_directory, os.path.splitext(os.path.split(self.large_polygon_vectorfile)[-1])[0] + '_' + os.path.split(self.small_polygon_vectorfile)[-1] )

        self.extract_needed_tiles(self.small_polygon_vectorfile, self.large_polygon_vectorfile, self.out_shape_name)

    def tilesplit_mp(self):
        """  run splitshape operation in parallel on available cores -2 cores split by tile"""
        self.large_polygon_vectorfile = self.reproject_to_epsg(self.out_shape_name,'4326')

        bounding_box_small_poly = self.get_bounding_box(self.small_polygon_vectorfile)

        if self.test:
            usable_number_of_cores = 1
        else:
            if mp.cpu_count() <= 2:
                usable_number_of_cores = 1
            else:
                usable_number_of_cores = mp.cpu_count()-2
        logging.info('number of usable cores for shapesplitting is ' + str(usable_number_of_cores))

        pool = mp.Pool(usable_number_of_cores)

        with fiona.open(self.large_polygon_vectorfile,'r') as large_poly_vector_open:
            for tile in large_poly_vector_open:
                pool.apply_async(self.write_splitted_tiles, args = (bounding_box_small_poly, tile, self.output_directory, self.small_polygon_vectorfile))
            pool.close()
            pool.join()

    def delete_splitted_files(self):
        """ removes all files created by this class"""
        remove_list = glob.glob(os.path.join(self.output_directory, '*'))  
        for file in remove_list:
            os.remove(file)
        os.rmdir(self.output_directory)
        logging.info('deleted splitted vectorfiles')



#running this class:
"""
small_polygon_vectorfile = '' #vectorfile to be split
vector_directory = '' # where to store results
world_tiles = '' #vectorfile to split with
fieldname = '' #name of the field where tilename is stored (S2: 'Name', LS: 'PR')
TileSplitter(small_polygon_vectorfile, world_tiles, vector_directory, fieldname).tilesplit()
# created vectorfiles will be located in  vector_directory/EODIE_temp
"""
