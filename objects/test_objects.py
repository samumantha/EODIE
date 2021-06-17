"""

class for testing functionality of all methods

TODO: test content of files/arrays?, remove reprojected

"""


import os
import shutil
from collections import OrderedDict
from affine import Affine
import glob
import sys
print(os.getcwd())
sys.path.append("./objects")
from cloudobject import CloudObject
from extractor import Extractor
from geometry import Geometry
from indexobject import IndexObject
from bandobject import BandObject
from writer import WriterObject

class TestObjects(object):

    def test_cloud(self):
        inpath = 'testfiles/S2/S2B_MSIL2A_20200626T095029_N0214_R079_T34VFN_20200626T123234.SAFE/GRANULE/L2A_T34VFN_A017265_20200626T095032/IMG_DATA'
        cloudobject = CloudObject(inpath)
        cloudmask = cloudobject.create_cloudmask()
        cloudmaskshape = cloudmask.shape
        rightcloudmaskshape = (10980, 10980)
        assert (cloudmaskshape == rightcloudmaskshape), 'Cloudmask fails'

        cloudobject.test_binarize()
        cloudobject.test_resample()

        del cloudobject
        del cloudmask

    def test_index(self):
        inpath = 'testfiles/S2/S2B_MSIL2A_20200626T095029_N0214_R079_T34VFN_20200626T123234.SAFE/GRANULE/L2A_T34VFN_A017265_20200626T095032/IMG_DATA'
        indexobject = IndexObject(inpath, 10)
        indexarray = indexobject.calculate_ndvi()
        indexarrayshape = indexarray.shape
        rightindexarrayshape = (10980, 10980)
        assert (indexarrayshape == rightindexarrayshape), 'Index fails'

        del indexobject
        del indexarray


    def test_band(self):
        inpath = 'testfiles/S2/S2B_MSIL2A_20200626T095029_N0214_R079_T34VFN_20200626T123234.SAFE/GRANULE/L2A_T34VFN_A017265_20200626T095032/IMG_DATA'
        bandobject = BandObject(inpath)

        bandfile = bandobject.get_bandfile('B04', 10) 
        rightbandfile = 'testfiles/S2/S2B_MSIL2A_20200626T095029_N0214_R079_T34VFN_20200626T123234.SAFE/GRANULE/L2A_T34VFN_A017265_20200626T095032/IMG_DATA/R10m/T34VFN_20200626T095029_B04_10m.jp2'
        assert (bandfile == rightbandfile), 'Bandfile fails'

        array = bandobject.get_array('B04', 10)
        rightarrayshape = (10980, 10980)
        assert (array.shape == rightarrayshape), 'Bandarray fails'

        epsg = bandobject.epsg 
        rightepsg = '32634'
        assert (epsg == rightepsg), 'Raster EPSG fails'

        affine = bandobject.affine 
        rightaffine = Affine(10.0, 0.0, 600000.0, 0.0, -10.0, 6800040.0)
        assert (affine == rightaffine), 'Affine fails'
 
        del bandobject


    def test_geometry(self):
        geometries = 'testfiles/shp/test_parcels_32635_34VFN.shp'
        geometryobject = Geometry(geometries)

        head,tail,root,ext = geometryobject.split_path() 
        splitpathlist = [head,tail,root,ext]
        rightsplitpathlist = ['testfiles/shp', 'test_parcels_32635_34VFN.shp','test_parcels_32635_34VFN', '.shp']
        assert (splitpathlist == rightsplitpathlist), 'Splitpath fails'

        projectionfile = geometryobject.get_projectionfile()
        rightprojectionfile = 'testfiles/shp/test_parcels_32635_34VFN.prj'

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
        geometries = 'testfiles/shp/test_parcels_32635_34VFN.shp'
        inpath = 'testfiles/S2/S2B_MSIL2A_20200626T095029_N0214_R079_T34VFN_20200626T123234.SAFE/GRANULE/L2A_T34VFN_A017265_20200626T095032/IMG_DATA'
        idname = 'ID'
        cloudobject = CloudObject(inpath)
        cloudmask = cloudobject.create_cloudmask()
        indexobject = IndexObject(inpath, 10)
        indexarray = indexobject.calculate_ndvi()
        bandobject = BandObject(inpath)
        affine = bandobject.affine 
        extractorobject = Extractor(cloudmask, indexarray, geometries, idname, affine, ['median'])
        statarrays = extractorobject.extract_arrays_stat()
        statarrayslen = len(statarrays)
        rightstatarrayslen = 3
        assert (statarrayslen == rightstatarrayslen), 'Exract Statarrays fails'

        arrayslen = len(extractorobject.extract_arrays())
        rightarrayslen = 3
        assert (arrayslen == rightarrayslen), 'Extract arrays fails'

        extractorobject.test_masking()

        del extractorobject

    def test_writer(self):
        tmpdir = 'testfiles/temp'
        if not os.path.exists(tmpdir):
            os.mkdir(tmpdir)
        geometries = 'testfiles/shp/test_parcels_32635_34VFN.shp'
        inpath = 'testfiles/S2/S2B_MSIL2A_20200626T095029_N0214_R079_T34VFN_20200626T123234.SAFE/GRANULE/L2A_T34VFN_A017265_20200626T095032/IMG_DATA'
        idname = 'ID'
        cloudobject = CloudObject(inpath)
        cloudmask = cloudobject.create_cloudmask()
        indexobject = IndexObject(inpath, 10)
        indexarray = indexobject.calculate_ndvi()
        bandobject = BandObject(inpath)
        affine = bandobject.affine 
        extractorobject = Extractor(cloudmask, indexarray, geometries, idname, affine, ['median'])
        statarrays = extractorobject.extract_arrays_stat()
        date = '20200626'
        tile = '34VFN'
        writerobject = WriterObject(tmpdir, date, tile, statarrays, 'ndvi', ['mean','median','std'])
        writerobject.write_csv()
        
        assert os.path.exists(writerobject.outpath), 'Writer fails' 

        del writerobject


TestObjects()
