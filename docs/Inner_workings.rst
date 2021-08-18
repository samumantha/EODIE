Inner workings
===============

The following gives an overview over what is happening in the backgroudn when process.py is called:

The first step after starting the workflow is to find the right data to be processed. 
For that, the shapefile projection is adjusted to match the one of the data, a convexhull 
is created and overlayed with the Sentinel-2 grid to find the tilenames overlapping the 
area of interest. In this step the cloudcover (as indicated in metadata) may be taken into 
account as well. Based on this and the timeframe of interest, a list of filenames is created 
with all files to be processed. In case data is not yet available in the system, data matching 
the needs is downloaded from a dataportal. Until this step both personal computer and HPC process
are same. For efficient processing the input shapefile is split based on the tilegrid to have one 
shapefile per tile, which can then go into the process. Only polygons that are fully within a tile 
are considered. Due to the overlap of the tiles, all data is processed (unless there is a gigantic
shapefile larger than 10 km in one dimension and located directly in the area of overlap). If the 
process is done on computer, each file in the list is processed one after another. The process 
works along the list, choosing the right shapefile for each raster based on tilename. If there is 
different shapefiles for different years, this can be taken into account. On HPC system the process 
can be done in parallel since the single processes do not overlap. Each process takes one raster, 
chooses the shapefile accordingly and applies the following workflow:
A binary cloudmask is extracted based on the scene classification of the S2 tile. With the awareness 
that it is not the best possibly cloudmask, also external binary cloudmasks can be uploaded and used 
instead. Depending on the needs, the data is now processed to vegetation index and resampled if necessary.
The cloudmask is then applied to each index/band and user chosen statistics are extracted. 
This step takes into account all pixels whose midpoint is within the polygons boundary. 
The extracted statistics are stored in csv file format with one file per tile per timepoint per index/band 
and one unique polygon per row of the file.
These csv files can be further combined to form a timeseries per index/band to be ready for input into machine learning models.