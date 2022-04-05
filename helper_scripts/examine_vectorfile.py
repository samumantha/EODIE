"""

Gives information on what fields are available in a given vectorfile

input: location and name of a vectorfile

output: prints available fieldnames in terminal

use: python examine_vectorfile.py path/to/vectorfile.*

"""


import sys
import fiona

vectorfilename = sys.argv[1]

shapes = fiona.open(vectorfilename)

# first feature
first_feature = next(iter(shapes))

print('Fieldnames available for the given vectorfile: ' + str(list(first_feature['properties'].keys())))

