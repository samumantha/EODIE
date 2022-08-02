Internals
==========


The following gives an overview over what is happening in the background when the user calls:

``python eodie_process.py --rasterdir ./testfiles/S2 --vector ./testfiles/shp/test_parcels_32635.shp --out ./results --id ID --index ndvi --platform s2 --statistics_out``

Step 1: Validation
------------------

To make sure all necessary inputs have been given and they are interpretable, EODIE will check the inputs. If any of the input checks fails, EODIE exits and tells, what went wrong so the input can be fixed accordingly.

Step 2: Launching a workflow
-------------------------------

Workflow is launched based on the platform given by user. Workflows differ slightly between platforms due to differences in processing steps. Some steps are common for all workflows.

Step 3: Validation of remote sensing rasters
---------------------

The actual the workflow begins by reading the vectorfile into a geopandas GeoDataframe. After reading, the GeoDataframe is clipped to match the extent of remote sensing data, ie. features outside Sentinel-2 tiles in ``--rasterdir`` will be excluded from processing.
Then, the raster data is validated based on coverage on vectorfile features and cloudcover. Rasterdata with too high cloud cover percentage or NoData over areas of interest will be excluded from further processing.

With Landsat 8, the validation step only clips the vector data based on data coverage but does not check individual scenes for cloudcover or NoData.

With tif platform, this step is skipped. 

Step 4: Cloudmask creation
-------------------------

For each Sentinel-2 .SAFE directory that was declared valid in the previous step, a binary cloudmask is created based on Scene Classification Layer. 

Cloudmask creation works similarly with Landsat 8 but takes longer due to different file structure of cloudmask file.

Step 5: Calculating and extracting indices
--------------------------

For each Sentinel-2 .SAFE directory, the index calculation and extraction is done separately.
The GeoDataframe is reprojected to match the EPSG code of rasterdata and filtered to only contain data within that Sentinel-2 tile.
Then, vegetation index values (based on userinput ``--index``) are calculated for the whole tile and resampled if necessary. The cloudmask from previous step is applied to each index/band. With the awareness that it is not the best possible cloudmask, also external binary cloudmasks can be uploaded and used 
instead (using ``--external_cloudmask``).

User-chosen zonal statistics are extracted in given format for each polygon feature from the cloudmasked index array. This step takes into account all pixels that touch the polygons boundary (this can be changed to 'all pixels whose midpoint is within the polygons boundary' by using ``--exclude_border``).
After extracting the zonal statistics, they will be written in given output formats. 

Step parallelization
--------------------
Steps 3-5 are individually parallelized with `dask.delayed <https://docs.dask.org/en/stable/delayed.html>_`. In brief, validation for all .SAFE directories is parallelized, cloudmask creation is parallelized and index extraction is parallelized. The workflow moves from one parallelized step to another.
In steps 3 and 4, number of processes consists of numbers of original rasterdata and valid rasterdata, respectively. In step 5, each index or band to be extracted forms their own process, making the total number of processes (number of valid .SAFEs) * (number of indices). For instance, with 3 indices from 5 valid safedirs, the total number of processes in step 5 would be 15. 
