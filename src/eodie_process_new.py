#!/usr/bin/env python

import glob
import math
import argparse
import re
import sys
import os
from eodie.extractor import Extractor
from eodie.mask import Mask
from eodie.index import Index
from eodie.vectordata import VectorData
from eodie.pathfinder import Pathfinder
from eodie.rastervalidator_s2 import RasterValidatorS2
from eodie.writer import Writer
from eodie.userinput import UserInput
from eodie.tilesplitter import TileSplitter
from eodie.rasterdata import RasterData
from eodie.validator import Validator
import logging
from datetime import datetime
import timeit
from dask import delayed
from dask import compute
import geopandas as gpd
from eodie.workflow import Workflow

def read_userinput():
    userinput = UserInput()      
    Validator(userinput)
    return userinput   

def main():    
    
    userinput = read_userinput()  
    process = Workflow(userinput)   
    
if __name__ == '__main__':
    main()