#!/usr/bin/env python

import argparse
import yaml
import sys
sys.path.append("./eodie")
from eodie.splitshp import SplitshpObject 

with open('./user_config.yml', "r") as ymlfile:
    user_cfg = yaml.safe_load(ymlfile)


parser = argparse.ArgumentParser()
parser.add_argument('--polygons', dest='small_poly_file', help='name of the shapefile to be split ', required=True)
parser.add_argument('--outdir', dest='outdir', help='directory where results shall be saved')

args = parser.parse_args()


large_poly_file = user_cfg['tileshp'] + '.shp'
large_poly_namefield = user_cfg['fieldname']

sso = SplitshpObject(args.small_poly_file, large_poly_file, args.outdir , large_poly_namefield)
sso.splitshp()
