Internals
==========


The following gives an overview over what is happening in the backgroudn when the user calls:

``python process.py --dir ./testfiles/S2 --shp ./testfiles/shp/test_parcels_32635 --out ./results --id ID --index ndvi --platform s2  --statistics_out``

The first step after starting the workflow is to find the right data to be processed (from ``--dir``). 
For that, the shapefile (``--shp``) projection is adjusted to match the one of the data, a convexhull 
is created and overlayed with the Sentinel-2 grid (``tileshp`` in user_config.yml) to find the tilenames overlapping the 
area of interest. 

Based on this and the timeframe of interest (in this case default for ``--start`` and ``--end``), a list of filenames is created 
with all files to be processed. Until this step both personal computer and HPC process
are same. For efficient processing the input shapefile is split based on the tilegrid to have one 
shapefile per tile, which can then go into the process. Only polygons that are fully within a tile 
are considered. Due to the overlap of the tiles, all data is processed (rare exceptions). Each file in the list is processed one after another. 

The process works along the list, choosing the right shapefile (``--shp`` + _tilename + .shp) for each raster based on tilename. On HPC systems, the process 
can be done in parallel since the single processes do not overlap. Each process takes one raster, 
chooses the shapefile accordingly and applies the following workflow:

A binary cloudmask is extracted based on the scene classification of the Sentinel-2 tile. With the awareness 
that it is not the best possibly cloudmask, also external binary cloudmasks can be uploaded and used 
instead (using ``--external_cloudmask``). Depending on the needs, the data is now processed to vegetation index (``--index``) and resampled (to ``pixelsize`` in user_config.yml) if necessary.
The cloudmask is then applied to each index/band and user chosen statistics (default mean,median and std since no ``--statistics`` are given) are extracted. 
This step takes into account all pixels that touch the polygons boundary (this can be changed to 'all pixels whose midpoint is within the polygons boundary' by using ``--exclude_border``). 
The extracted statistics are stored in csv file format with one file per tile per timepoint per index/band 
and one unique polygon per row of the file.
These csv files can be further combined to form a timeseries per index/band by using one of the ``combine_statistics_x`` scripts in postprocesses if needed.
