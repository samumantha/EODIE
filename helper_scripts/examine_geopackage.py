""" 
Python script for examining GeoPackage to be used as an input for EODIE [https://eodie.readthedocs.io/en/latest/]

Inputs:
One GeoPackage file (extension .gpkg)

Output prints to terminal:
- Number of layers in GeoPackage
- Layer names and the geometry types

Usage: python examine_geopackage.py path/to/geopackage.gpkg

Written by Arttu Kivimäki, March 2022

"""

import sys
from osgeo import ogr 

# Store path to geopackage from command line argument
gpkg_path = sys.argv[1]

# Open geopackage with ogr
gpkg = ogr.Open(gpkg_path)

# Get the names of the layers in geopackage
gpkg_layers = [layer.GetName() for layer in gpkg]

# Get the number of features in each layer
layer_features = [layer.GetFeatureCount() for layer in gpkg]

# Get the geometry types of the layers in geopackage
geometry_types = [ogr.GeometryTypeToName(gpkg.GetLayerByName(name).GetGeomType()) for name in gpkg_layers]

print("\nThis GeoPackage contains the following layers:")
for i in range(len(gpkg_layers)):
    print("\nLayer name: {} | Geometry type: {} | Feature count: {}".format(gpkg_layers[i], geometry_types[i], layer_features[i]))








#print(gpkg_definitions)

#print(gpkg_layers)





