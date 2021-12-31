import json
import os
import datetime
import math
import rasterio


###########################
# Define Exo-Atmospheric Irradiance values for 5 RE bands
############################
eai_b1 = 1997.8
eai_b2 = 1863.5
eai_b3 = 1560.4
eai_b4 = 1395.0
eai_b5 = 1124.4


# # Get earth sun distance based on meta data
# def ESdist(metadata):
#     # get scene date
#     scene_date = datetime.datetime.fromisoformat(metadata["properties"]["acquired"][:-1])
#     # get day of year
#     doy = scene_date.timetuple().tm_yday
#     # Earth-Sun distance (from doy)
#     # http://physics.stackexchange.com/questions/177949/earth-sun-distance-on-a-given-day-of-the-year
#     return 1 - 0.01672 * math.cos(0.9856 * (doy - 4))


# Get path to scene
# input metadata object and a directory to look for associated image
def GetScenePath(metadata, dir):
    scene_date = datetime.datetime.fromisoformat(metadata["properties"]["acquired"][:-1])
    return dir + "/" + metadata["properties"]["grid_cell"] + "_" + str(scene_date.date()) + "_RE5_3A.tif"


# Convert multiband image to radiance
# def ToRad(path):
#     with rasterio.open(path) as f:
#         return f.read() * 0.01



# Convert image bands to TOA radiance and then to TOA reflectance and write output to file
def ToRef(ScenePath, outpath, metadata):
    # Get filename to use for appending to output
    fname = os.path.splitext(os.path.basename(ScenePath))[0]

    # Get Earth-Sun Distance
    # get scene date
    scene_date = datetime.datetime.fromisoformat(metadata["properties"]["acquired"][:-1])
    # get day of year
    doy = scene_date.timetuple().tm_yday
    # Earth-Sun distance (from doy)
    # http://physics.stackexchange.com/questions/177949/earth-sun-distance-on-a-given-day-of-the-year
    esd = 1 - 0.01672 * math.cos(0.9856 * (doy - 4))

    # First convert to radiance using scaling factor 0.01
    with rasterio.open(ScenePath) as f:
        profile = f.profile.copy()
        rad = f.read() * 0.01
        # Get Solar Zenith and convert to radians
        SolarZ = (90 - metadata["properties"]["sun_elevation"]) * 0.01745329
        # Apply TOA reflectance equation to each band
        b1TOA = rad[0] * ((math.pi * esd ** 2) / eai_b1 * math.cos(SolarZ))
        b2TOA = rad[1] * ((math.pi * esd ** 2) / eai_b2 * math.cos(SolarZ))
        b3TOA = rad[2] * ((math.pi * esd ** 2) / eai_b3 * math.cos(SolarZ))
        b4TOA = rad[3] * ((math.pi * esd ** 2) / eai_b4 * math.cos(SolarZ))
        b5TOA = rad[4] * ((math.pi * esd ** 2) / eai_b5 * math.cos(SolarZ))
        # List bands
        final = [b1TOA, b2TOA, b3TOA, b4TOA, b5TOA]
        # Update metadata (additional meta updates needed?)
        profile.update({'dtype': 'float32'})
        # Write output to multiband geotiff
        with rasterio.open(outpath + "/" + fname + "_TOAref.tif", 'w', **profile) as out:
            for band, layer in enumerate(final, start=1):
                out.write(layer, band)


