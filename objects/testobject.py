"""

TODO: test content of files/arrays?, remove reprojected

"""


import os
import shutil
from collections import OrderedDict
from affine import Affine
import glob

from cloudobject import CloudObject
from extractor import Extractor
from geometryobject import GeometryObject
from indexobject import IndexObject
from rasterobject import RasterObject
from writerobject import WriterObject

class Objecttesting(object):

    def __init__(self):
        self.inpath = '../testfiles/S2/S2B_MSIL2A_20200626T095029_N0214_R079_T34VFN_20200626T123234.SAFE/GRANULE/L2A_T34VFN_A017265_20200626T095032/IMG_DATA'
        self.geometries = '../testfiles/shp/test_parcels_32635_34VFN.shp'
        self.tmpdir = '../testfiles/temp'
        self.alldone = 0
        if not os.path.exists(self.tmpdir):
            os.mkdir(self.tmpdir)
        self.bands = ['B04','B08']
        self.idname = 'ID'
        self.test_raster()
        self.test_cloud()
        self.test_index()
        self.test_geometry()
        self.test_extractor()
        self.test_writer()
        if self.alldone == 6:
            shutil.rmtree(self.tmpdir)
            #for reprofile in glob.glob(os.path.splitext(self.geometries)[0] + '.*'):
                #os.remove(reprofile)

    def test_cloud(self):
        cloudobject = CloudObject(self.inpath, 20, ['SCL'])
        cloudmask = cloudobject.create_cloudmask()
        cloudmaskshape = cloudmask.shape
        rightcloudmaskshape = (10980, 10980)
        assert (cloudmaskshape == rightcloudmaskshape), 'Cloudmask fails'
        self.cloudmask = cloudmask
        self.alldone += 1

    def test_index(self):
        indexobject = IndexObject(self.inpath, 10, self.bands)
        indexarray = indexobject.calculate_ndvi()
        indexarrayshape = indexarray.shape
        rightindexarrayshape = (10980, 10980)
        assert (indexarrayshape == rightindexarrayshape), 'Index fails'
        self.indexarray = indexarray
        self.alldone += 1

    def test_raster(self):
        rasterobject = RasterObject(self.inpath, 10, self.bands)

        bandfiles = rasterobject.bandfiles 
        rightbandfiles = ['../testfiles/S2/S2B_MSIL2A_20200626T095029_N0214_R079_T34VFN_20200626T123234.SAFE/GRANULE/L2A_T34VFN_A017265_20200626T095032/IMG_DATA/R10m/T34VFN_20200626T095029_B04_10m.jp2','../testfiles/S2/S2B_MSIL2A_20200626T095029_N0214_R079_T34VFN_20200626T123234.SAFE/GRANULE/L2A_T34VFN_A017265_20200626T095032/IMG_DATA/R10m/T34VFN_20200626T095029_B08_10m.jp2']
        assert (bandfiles == rightbandfiles), 'Bandfiles fails'

        epsg = rasterobject.get_epsg()
        rightepsg = '32634'
        assert (epsg == rightepsg), 'Raster EPSG fails'

        
        arraylen = len(rasterobject.get_arrays())
        #size of the jp2
        rightarraylen = 2
        assert (arraylen == rightarraylen), 'Arrays fail'
        

        affine = rasterobject.get_affine()
        rightaffine = Affine(10.0, 0.0, 600000.0, 0.0, -10.0, 6800040.0)
        assert (affine == rightaffine), 'Affine fails'
        self.affine = affine
        self.alldone += 1


    def test_geometry(self):
        geometryobject = GeometryObject(self.geometries)

        head,tail,root,ext = geometryobject.split_path() 
        splitpathlist = [head,tail,root,ext]
        rightsplitpathlist = ['../testfiles/shp', 'test_parcels_32635_34VFN.shp','test_parcels_32635_34VFN', '.shp']
        assert (splitpathlist == rightsplitpathlist), 'Splitpath fails'

        projectionfile = geometryobject.get_projectionfile()
        rightprojectionfile = '../testfiles/shp/test_parcels_32635_34VFN.prj'

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
        self.alldone += 1

    def test_extractor(self):
        extractorobject = Extractor(self.cloudmask, self.indexarray, self.geometries, self.idname, self.affine)
        statarrays = extractorobject.extract_arrays_stat()
        statarrayslen = len(statarrays)
        rightstatarrayslen = 3
        assert (statarrayslen == rightstatarrayslen), 'Exract Statarrays fails'

        self.extractedarrays = statarrays
        arrayslen = len(extractorobject.extract_arrays())
        rightarrayslen = 3
        assert (arrayslen == rightarrayslen), 'Extract arrays fails'
        self.alldone += 1

    def test_writer(self):
        date = '20200626'
        tile = '34VFN'
        writerobject = WriterObject(self.tmpdir, date, tile, self.extractedarrays)
        writerobject.write_csv()
        
        assert os.path.exists(writerobject.outpath), 'Writer fails' 
        self.alldone += 1



Objecttesting()
