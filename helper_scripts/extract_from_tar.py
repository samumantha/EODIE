"""
Script for extracting Landsat 8 files from their native .tar packages distributed from Earth Explorer.

Author: Arttu Kivimäki (FGI) - August 2022

Use python extract_from_tar.py --help for details.

"""

# Imports
import argparse
import tarfile
import os
import glob

# Initialize argumentparser
parser = argparse.ArgumentParser()

# Add arguments
parser.add_argument(
    "--tardir",
    dest = "tardir",
    required = True,
    help = "Path to directory where .tar files are. Required."
)

parser.add_argument(
    "--outdir",
    dest = "outdir",
    default = None, 
    help = "Path to directory where you would like to extract the tars. Defaults to --tardir."
)

# Parse arguments
args = parser.parse_args()

# Glob tarfiles from given directory
tars = glob.glob(args.tardir + "/*.tar")

# Build outputpath
if args.outdir is not None:
    outpath = args.outdir
else:
    outpath = args.tardir

# Loop through list of tar files 
for tar in tars:
    # Extract filename for folder creation
    filepath = os.path.splitext(tar)    
    filename = filepath[0].split(os.sep)[-1]
    # Build extractionpath based on outpath and filename
    extractionpath = os.path.join(outpath, filename)
    # Create extractionpath
    os.mkdir(extractionpath)

    # Open tarfile and extract its contents
    with tarfile.open(tar, "r") as tar_out:
        tar_out.extractall(extractionpath)

print("All tars extracted!")



    
