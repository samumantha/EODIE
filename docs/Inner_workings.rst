Internals
==========


The following gives an overview over what is happening in the background when the user calls:

``python eodie_process.py --rasterdir ./testfiles/S2 --vector ./testfiles/shp/test_parcels_32635 --out ./results --id ID --index ndvi --platform s2  --statistics_out``

Step 1: Validation
------------------

To make sure all necessary inputs have been given and they are interpretable, EODIE will check the inputs. If any of the input checks fails, EODIE exits and tells, what went wrong so the input can be fixed accordingly.

Step 2: Input vector conversion
-------------------------------

If input vector is ESRI Shapefile (like in this example case), this step will be skipped. Otherwise, EODIE will convert the vector input to ESRI Shapefile format for further processing. 

Step 3: Matching data
---------------------

The actual the workflow begins with finding the right data to be processed (from ``--rasterdir``). 
For that, the input vector's projection is adjusted to match the one of the data, a convexhull is created and overlayed with the Sentinel-2 grid (``tileshp`` in user_config.yml) to find the tilenames overlapping the 
area of interest. Based on this and the timeframe of interest (in this case default for ``--start`` and ``--end``), a list of filenames is created 
with all files to be processed. Until this step both personal computer and HPC process
are same. 

Step 4: Splitting vectors
-------------------------

For efficient processing the input vector is split based on the tilegrid to have one 
shapefile per tile, which can then go into the process. Only polygons that are fully within a tile 
are considered. Due to the overlap of the tiles, all data is processed (rare exceptions). Each file in the list is processed one after another. 

Step 5: Processing vectors
--------------------------

The process works along the list of splitted shapefiles, choosing the right vectorfile (``--vector`` + _tilename + .extension) for each raster based on tilename. On HPC systems, the process 
can be done in parallel since the single processes do not overlap. Each process takes one raster, 
chooses the vectorfile accordingly and copies it to a temporary directory (which is automatically removed after the process) and applies the following workflow:

A binary cloudmask is extracted based on the scene classification of the Sentinel-2 tile. With the awareness 
that it is not the best possibly cloudmask, also external binary cloudmasks can be uploaded and used 
instead (using ``--external_cloudmask``). Depending on the needs, the data is now processed to vegetation index (``--index``) and resampled (to ``pixelsize`` in user_config.yml) if necessary.
The cloudmask is then applied to each index/band and user chosen statistics (default ``count`` since no ``--statistics`` are given) are extracted. 
This step takes into account all pixels that touch the polygons boundary (this can be changed to 'all pixels whose midpoint is within the polygons boundary' by using ``--exclude_border``). 

Step 6: Writing outputs
-----------------------
The extracted statistics are stored in csv file format with one file per tile per timepoint per index/band and one unique polygon per row of the file.
These csv files can be further combined to form a timeseries per index/band by using one of the ``combine_statistics_x`` scripts in postprocesses if needed.
