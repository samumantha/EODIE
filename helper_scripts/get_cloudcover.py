"""

Can be used to get basic tilewise cloudcover information about Sentinel-2 data in a given directory. 

input:
location and name of a directory with Sentinel-2 SAFE files

output:
prints in terminal a dictionary of {date:cloudcover percentage}

use: python get_cloudcover.py path/to/Sentinel-2datadir

"""


import sys
import glob
import os
from xml.dom import minidom

s2dir = sys.argv[1]

cc_dir = {}

for file in glob.glob(os.path.join(s2dir,'S2*SAFE')):
    metadatafile = os.path.join(file,'MTD_MSIL2A.xml')
    doc = minidom.parse(metadatafile)
    date = os.path.split(file)[-1].split('_')[2].split('T')[0]
    cloudcover_percentage = float(doc.getElementsByTagName('Cloud_Coverage_Assessment')[0].firstChild.data)
    cc_dir[date] = cloudcover_percentage

print(cc_dir)