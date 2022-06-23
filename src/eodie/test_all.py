"""
Class for testing functionality of many methods used in EODIE automatically run by gitlab on push.
Can also be run with ```pytest test_all.py```.

Authors: Samantha Wittke


"""


import os
from collections import OrderedDict
from affine import Affine
import glob
import sys
import numpy as np
from eodie.mask import Mask
from eodie.extractor import Extractor
from eodie.vectordata import VectorData
from eodie.index import Index
from eodie.rasterdata import RasterData
from eodie.writer import Writer
from eodie.splitshp import SplitshpObject
import yaml
import fiona


class TestAll(object):

    def test_cloud(self):
        with open('test_config.yml', "r") as ymlfile:
            cfg = yaml.safe_load(ymlfile)
        inpath = 'testfiles/S2/S2B_MSIL2A_20200626T095029_N0214_R079_T34VFN_20200626T123234.SAFE/GRANULE/L2A_T34VFN_A017265_20200626T095032/IMG_DATA'
        # for os independence in these mixed paths
        inpath = inpath.replace('/', os.sep)
        cloudobject = Mask(inpath, cfg , True)
        cloudmask = cloudobject.create_cloudmask()
        cloudmaskshape = cloudmask.shape
        rightcloudmaskshape = (10980, 10980)
        assert (cloudmaskshape == rightcloudmaskshape), 'Cloudmask fails'

   
        inarray = np.array([[1,3,3,7,6,6,5,8,9],[10,6,5,5,3,0,1,10,10]])
        binarray = cloudobject.binarize_cloudmask(inarray)
        rightarray = np.array([[1,1,1,0,0,0,0,1,1],[1,0,0,0,1,1,1,1,1]])
        assert (binarray == rightarray).all(), 'Binarizing fails'
        print("Cloudtest done")
        

        del cloudobject
        del cloudmask


    def test_index(self):
        with open('test_config.yml', "r") as ymlfile:
            cfg = yaml.safe_load(ymlfile)
        inpath = 'testfiles/S2/S2B_MSIL2A_20200626T095029_N0214_R079_T34VFN_20200626T123234.SAFE/GRANULE/L2A_T34VFN_A017265_20200626T095032/IMG_DATA'
        # for os independence in these mixed paths
        inpath = inpath.replace('/', os.sep)
        indexobject = Index(inpath,cfg, True)
        supportedindices = Index.supportedindices
        #testing capacity is limited on gitlab, so all tasseled cap indices are excluded from testing (too much memory used)
        testingindices = [index for index in supportedindices if not index.startswith('tct')]
        for index in testingindices:
            indexarray = indexobject.calculate_index(index)
            indexarrayshape = indexarray.shape
            rightindexarrayshape = (10980, 10980)
            assert (indexarrayshape == rightindexarrayshape), 'Index fails'
            del indexarray
            del indexarrayshape

        inarray = np.array([[0.1,0.2,0.4],[0.4,0.1,0.2]])
        cloudarray  = np.array([[1,0,0],[0,1,0]])
        rightarray = np.ma.array([[0,0.2,0.4],[0.4,0,0.2]], mask = [[True,False,False],[False,True,False]], fill_value=-99999).filled()
        maskedarray = indexobject.mask_array(inarray,cloudarray).filled()
        assert (maskedarray == rightarray).all(), 'Masking fails'

        del indexobject
        

    def test_band(self):
        with open('test_config.yml', "r") as ymlfile:
            cfg = yaml.safe_load(ymlfile)
        inpath = 'testfiles/S2/S2B_MSIL2A_20200626T095029_N0214_R079_T34VFN_20200626T123234.SAFE/GRANULE/L2A_T34VFN_A017265_20200626T095032/IMG_DATA'
        # for os independence in these mixed paths
        inpath = inpath.replace('/', os.sep)
        rasterdata = RasterData(inpath, cfg , True)

        bandfile,_ = rasterdata.get_bandfile('B04')
        rightbandfile = 'testfiles/S2/S2B_MSIL2A_20200626T095029_N0214_R079_T34VFN_20200626T123234.SAFE/GRANULE/L2A_T34VFN_A017265_20200626T095032/IMG_DATA/R10m/T34VFN_20200626T095029_B04_10m.jp2'
        # for os independence in these mixed paths
        rightbandfile = rightbandfile.replace('/', os.sep)
        assert (bandfile == rightbandfile), 'Bandfile fails'

        array = rasterdata.get_array('B04')
        rightarrayshape = (10980, 10980)
        assert (array.shape == rightarrayshape), 'Bandarray fails'

        epsg = rasterdata.epsg 
        rightepsg = '32634'
        assert (epsg == rightepsg), 'Raster EPSG fails'

        affine = rasterdata.affine 
        rightaffine = Affine(10.0, 0.0, 600000.0, 0.0, -10.0, 6800040.0)
        assert (affine == rightaffine), 'Affine fails'
 
        del rasterdata
        del bandfile
        del array


    def test_geometry(self):
        geometries = 'testfiles/shp/test_parcels_32635.shp'
        geometries = geometries.replace('/',os.sep)
        geometryobject = VectorData(geometries)

        head,tail,root,ext = geometryobject._split_path() 
        splitpathlist = [head,tail,root,ext]
        rightsplitpathlist = ['testfiles' + os.sep + 'shp', 'test_parcels_32635.shp','test_parcels_32635', '.shp']
        assert (splitpathlist == rightsplitpathlist), 'Splitpath fails'

        projectionfile = geometryobject.get_projectionfile()
        rightprojectionfile = 'testfiles/shp/test_parcels_32635.prj'
        rightprojectionfile = rightprojectionfile.replace('/', os.sep)

        assert (projectionfile == rightprojectionfile), 'Projectionfile fails'

        epsg = geometryobject.get_epsg()
        rightepsg = '32635'
        assert (epsg == rightepsg), 'Geometry EPSG fails'

        geometryobject.reproject_to_epsg('4326')
        reprojectedgeometry = geometryobject.geometries
        assert os.path.exists(reprojectedgeometry), 'Reprojection fails'

        driver,schema,crs = geometryobject.get_properties()
        propertieslist = [driver,schema,crs]
        rightpropertieslist = ['ESRI Shapefile',{'properties': OrderedDict([('ID', 'str:80')]), 'geometry': 'Polygon'},{'init': 'epsg:4326'}]
        assert (propertieslist == rightpropertieslist), 'Geometry properties fail'
        """
        boundingbox = geometryobject.get_boundingbox()
        rightboundingbox = (348640.62425182585, 6786396.860003678, 349315.8119208717, 6787458.534407418)
        assert (boundingbox == rightboundingbox), 'Boundingbox fails'
        """

        del geometryobject

    def test_extractor(self):
        with open('test_config.yml', "r") as ymlfile:
            cfg = yaml.safe_load(ymlfile)
        geometries = 'testfiles/shp/test_parcels_32635.shp'
        inpath = 'testfiles/S2/S2B_MSIL2A_20200626T095029_N0214_R079_T34VFN_20200626T123234.SAFE/GRANULE/L2A_T34VFN_A017265_20200626T095032/IMG_DATA'
        # for os independence in these mixed paths
        inpath = inpath.replace('/', os.sep)
        idname = 'ID'
        cloudobject = Mask(inpath, cfg , True)
        cloudmask = cloudobject.create_cloudmask()
        indexobject = Index(inpath, cfg , True)
        indexarray = indexobject.calculate_ndvi()
        maskedarray = indexobject.mask_array(indexarray,cloudmask)
        rasterdata = RasterData(inpath, cfg , True)
        affine = rasterdata.affine 
        extractorobject = Extractor(maskedarray, geometries, idname, affine, ['mean','median','std'])
        statarrays = extractorobject.extract_statistics()
        statarrayslen = len(statarrays)
        rightstatarrayslen = 3
        assert (statarrayslen == rightstatarrayslen), 'Exract Statarrays fails'

        arrayslen = len(extractorobject.extract_array())
        rightarrayslen = 3
        assert (arrayslen == rightarrayslen), 'Extract arrays fails'

        del extractorobject
        del cloudobject
        del indexobject
        del indexarray
        del cloudmask
        del maskedarray


    def test_writer(self):
        with open('test_config.yml', "r") as ymlfile:
            cfg = yaml.safe_load(ymlfile)
        tmpdir = 'testfiles/temp'
        # for os independence in these mixed paths
        tmpdir = tmpdir.replace('/', os.sep)
        if not os.path.exists(tmpdir):
            os.mkdir(tmpdir)
        geometries = 'testfiles/shp/test_parcels_32635.shp'
        geometries = geometries.replace('/', os.sep)
        inpath = 'testfiles/S2/S2B_MSIL2A_20200626T095029_N0214_R079_T34VFN_20200626T123234.SAFE/GRANULE/L2A_T34VFN_A017265_20200626T095032/IMG_DATA'
        inpath = inpath.replace('/', os.sep)
        idname = 'ID'
        cloudobject = Mask(inpath, cfg , True)
        cloudmask = cloudobject.create_cloudmask()
        indexobject = Index(inpath, cfg , True)
        indexarray = indexobject.calculate_ndvi()
        maskedarray = indexobject.mask_array(indexarray,cloudmask)
        rasterdata = RasterData(inpath,cfg , True)
        affine = rasterdata.affine 
        extractorobject = Extractor(maskedarray, geometries, idname, affine,['mean','median','std'])
        statistics = extractorobject.extract_statistics()
        date = '20200626'
        tile = '34VFN'
        writerobject = Writer(tmpdir, date, tile, statistics, 'ndvi', 's2', 79, ['mean','median','std'])
        writerobject.write_statistics()
        
        assert os.path.exists(writerobject.outpath), 'Statistics writer fails' 

        array = extractorobject.extract_array()
        writerobject = Writer(tmpdir,date,tile,array,'ndvi', 's2', 79, ['count'])
        writerobject.write_array()

        assert os.path.exists(writerobject.outpath), 'Array writer fails'

        geoarray = extractorobject.extract_geotiff()
        writerobject = Writer(tmpdir,date,tile,geoarray,'ndvi', 's2', 79, ['count'])
        writerobject.write_geotiff()

        assert os.path.exists(writerobject.outpath + '_id_0.tif'), 'Geotiff writer fails'
        assert os.path.exists(writerobject.outpath + '_id_1.tif'), 'Geotiff writer fails'
        assert os.path.exists(writerobject.outpath + '_id_2.tif'), 'Geotiff writer fails'


        del extractorobject
        del cloudobject
        del indexobject
        del indexarray
        del cloudmask
        del maskedarray

        del writerobject
    
    def test_splitshp(self):
        tmpdir = 'testfiles/temp'
        tmpdir = tmpdir.replace('/', os.sep)
        if not os.path.exists(tmpdir):
            os.mkdir(tmpdir)
        smallparcels = 'testfiles/shp/test_parcels_32635.shp'
        largetiles = 'testfiles/shp/sentinel2_tiles_test.shp'
        smallparcels = smallparcels.replace('/', os.sep)
        largetiles = largetiles.replace('/', os.sep)
        shapesplitter = SplitshpObject(smallparcels, largetiles, tmpdir, 'Name', True)
        tmpshpdir = shapesplitter.output_directory
        assert os.path.exists(os.path.join(tmpshpdir, 'test_parcels_32635_reprojected_4326.shp')), 'Reprojection of shapefile failed'
        shapesplitter.splitshp()
        #assert not glob.glob(os.path.join(tmpshpdir,  'test_parcels_32635_reprojected_4326.*')), 'Failed to delete splitted testtiles'
        assert len(glob.glob(os.path.join(tmpshpdir, 'test_parcels_32635_reprojected_4326_*.shp'))) == 2, 'Wrong amount of splitted shapefiles'
        for tile in ['34VFN', '35VLH']:
            with fiona.open(os.path.join(tmpshpdir, 'test_parcels_32635_reprojected_4326_' + tile + '.shp' ), 'r' ) as shp:
                assert len(shp) == 3, 'Wrong amount of polygons in splitted shapefile'
        shapesplitter.delete_splitted_files()
        assert not os.path.exists(tmpshpdir)

        del tmpdir
        del tmpshpdir
        del shapesplitter


TestAll()
