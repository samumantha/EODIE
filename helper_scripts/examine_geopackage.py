""" 
Python script for examining GeoPackage to be used as an input for EODIE [https://eodie.readthedocs.io/en/latest/]

Inputs:
One GeoPackage file (extension .gpkg)

Output prints to terminal (for each layer):
- layer name
- geometry type
- feature count 
- attribute field names 

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

# Create an empty list for fields
fieldlist = []

# Loop through layers to get their fields
for layer in gpkg:
    # Get layer definition
    defn = layer.GetLayerDefn()
    # List all the fields in a file 
    fields = [defn.GetFieldDefn(i).GetName() for i in range(defn.GetFieldCount())]
    # Add the fields into a nested list
    fieldlist.append(fields)

# Get the geometry types of the layers in geopackage
geometry_types = [ogr.GeometryTypeToName(gpkg.GetLayerByName(name).GetGeomType()) for name in gpkg_layers]

# Print the terminal outputs
print("\nThis GeoPackage contains the following layers:")
# Loop through layers and print relevant information from each
for i in range(len(gpkg_layers)):
    print("\nLayer name: {} | Geometry type: {} | Feature count: {} | Fields: {}".format(gpkg_layers[i], geometry_types[i], layer_features[i], fieldlist[i]))
