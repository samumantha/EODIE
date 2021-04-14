import os
import glob
import re


class Pathfinder(object):

    def __init__(self,rasterdir):
        self.rasterdir = rasterdir
        self.get_imgpath()
        self.get_tileinfo()
        self.get_dateinfo()
        

    def get_imgpath(self):
        # getting the path until IMG_DATA
        patternimg = os.path.join(self.rasterdir ,'*','*','IMG_DATA')
        self.imgpath = glob.glob(patternimg)[0]


    def get_tileinfo(self):
        # extract tilename from filename
        tilepattern = r'(?<=T)[0-9]{2}[A-Z]{3}'
        self.tile = re.search(tilepattern,self.imgpath).group(0)

    def get_dateinfo(self):
        # extract date from filename
        datepattern = r'20[1-2][0-9][0-1][0-9][0-3][0-9]'
        self.date = re.search(datepattern,self.imgpath).group(0)

