"""

class to check that cloudcover is below the maximum given by user
and to check that area of interest is not within nodata zone 

"""

import os
import glob
from xml.dom import minidom
from rasterstats import zonal_stats

class RasterValidator(object):

    def __init__(self, SAFEpath, maxcloudcover, geometryobject):
        self.SAFEpath = SAFEpath
        self.maxcloudcover = maxcloudcover
        self.geometryobject = geometryobject
        self.cloudcovered = self.check_cloudcover()
        self.datacovered = self.check_datacover()
        
    def get_xml(self):
        xmlname = 'MTD_MSIL2A.xml'
        xmlpath = os.path.join(self.SAFEpath, xmlname)
        return xmlpath

    def read_xml(self,xmlpath):
        doc = minidom.parse(xmlpath)
        return doc

    def get_cloudcover_percentage(self, doc): 
        cc_perc = float(doc.getElementsByTagName('Cloud_Coverage_Assessment')[0].firstChild.data)
        return cc_perc
    
    def check_cloudcover(self):
        # checks that according to metadata the cloudcover is below user given threshold
        cloudcover_percentage = self.get_cloudcover_percentage(self.read_xml(self.get_xml()))
        if cloudcover_percentage <= self.maxcloudcover:
            return True
        else:
            return False

    def get_bandpath(self):
        bandpath = glob.glob(os.path.join(self.SAFEpath, '*','*','IMG_DATA','R60m','*'+'B04_60m.jp2'))[0]
        return bandpath

    def check_datacover(self):
        #checks that there is data within the convexhull of the given shapefile
        convex_hull = self.geometryobject.get_convex_hull()

        zonal_statistics = zonal_stats(convex_hull, self.get_bandpath(), stats="mean", band=1, nodata= -99999)
        if zonal_statistics[0]['mean'] == 0.0 or type(zonal_statistics[0]['mean']) is not float:
            return False
        else:
            return True
        
