"""

Gives information on what fields are available in a given shapefile

input: location and name of a shapefile

output: prints available fieldnames in terminal

use: python examine_shapefile.py path/to/shapefile.shp

"""


import sys
import fiona

shapefilename = sys.argv[1]

shapes = fiona.open(shapefilename)

# first feature
first_feature = next(iter(shapes))

print('Fieldnames available for the given shapefile: ' + str(list(first_feature['properties'].keys())))

