"""

script to reate binary cloudmask from non-binary cloudmask raster
name should be xxx_date_tile.xx
outname will be binarized(_resampled)_xxx_date_tile.xxx

"""

import sys
import os
import rasterio
import numpy as np


cloudfile = sys.argv[1]
outdir = sys.argv[2]
tobemasked = sys.argv[3]
resample = sys.argv[4]


name = "binarized"

tobemaskedlist = [int(cloudnumber) for cloudnumber in tobemasked.split(",")]

with rasterio.open(cloudfile) as f:
    array = np.array(f.read(1))
    crs = f.crs
    affine = f.transform

height = array.shape[0]
width = array.shape[1]

mask = np.isin(array, tobemaskedlist)

if resample:
    mask = np.kron(mask, np.ones((2, 2), dtype=int))
    height = height * 2
    width = width * 2
    affine = rasterio.Affine(
        affine[0] / 2, affine[1], affine[2], affine[3], affine[4] / 2, affine[5]
    )
    name = name + "_resampled"

mask = mask.astype("uint8")

with rasterio.open(
    os.path.join(
        outdir,
        name
        + "_"
        + os.path.splitext(os.path.split(cloudfile)[-1])[0]
        + os.path.splitext(cloudfile)[-1],
    ),
    "w",
    height=height,
    width=width,
    count=1,
    crs=crs,
    dtype=mask.dtype,
    transform=affine,
) as dst:
    dst.write(mask, 1)
