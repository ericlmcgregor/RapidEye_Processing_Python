import os
import json
import rasterio
import datetime
import math
import RapidEye as re

import matplotlib.pyplot as plt

# Define path for output TOA reflectance image
outpath = os.getcwd() + "\outputs"

# define path to folder with image and metadata files
fpath = os.path.join("data", "20140810_194058_1156207_RapidEye-5")
print(fpath)

# List json metadata files (in this trial just a single file exists)
# We will need the metadata to get solar angle information
flist = []
for file in os.listdir(fpath):
    if file.endswith(".json"):
        flist.append(file)
print(flist)


# read metadata file
with open(fpath + "/" + flist[0]) as fo:
    meta = json.load(fo)
print(meta["properties"])

# Get path to geotiff associated with the chosen metadata file
# The filename is a combo of grid cell id and the scene date
spath = re.GetScenePath(meta, fpath)

# Convert RapidEye image bands from DNs to radiance to TOA reflectance
# args: path to the tif file, desired output location, metadata file
re.ToRef(spath, outpath, meta)

# Load multiband output and view profile
with rasterio.open("outputs/1156207_2014-08-10_RE5_3A_TOAref.tif") as fin:
    print(fin.profile)
