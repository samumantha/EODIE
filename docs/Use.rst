User Manual
============

In this manual the general functionality of EODIE is described. In the end you can also find a usage example :ref:`example` (no external data needed).
For more examples with explanations, please check out :ref:`tutorial`.

Functionality
------------- 

EODIE can be used to extract polygon based information from a directory of Sentinel-2 (.SAFE) files.


Inputs 
^^^^^^^

The tool requires the following inputs:
(inputs with a default value are optional)

| ``--dir``
| The directory where the Sentinel-2 data to be processed is stored as absolute path.
| type: String
| default: -


| ``--shp``
| Absolute path to the shapefile to be used for processing, without extension and tilename.
| type: String
| default: -

| ``--out``
| Absolute path to the directory where the results shall be stored.
| type: String
| default: -

| ``--id``
| Name of the unique ID-field of the shapefile provided at --shp.
| type: String
| default: -

| ``--stat``
| 1 if statistics (see below) shall be calculated per polygon, 0 if all pixels within the polygon shall be extracted as numpy array
| type: Integer (``1`` or ``0``)
| default: ``1``

| ``--statistics``
| If --stat 1 is given, specify here which statistics shall be calculated per polygon
| type: list of strings, available: sum, std, median, majority, minority, unique, range, percentile_x (with x from 0 to 100)
| default: ``mean std median``

| ``--index``
| Which vegetation index or band shall be extracted per polygon
| type: list of strings, available: NDVI, RVI, SAVI, NBR
| default: -

| ``--start``
| Give the startdate of the timeframe of interest
| type: integer YYYYMMDD
| default: ``01-01-2016``

| ``--end``
| Give the enddate of the timeframe of interest
| type: integer YYYYMMDD
| default: todays date

Outputs
^^^^^^^^
One csv per tile, band/vegetation index and date with polygon identifiers in the first column and statistics is the following columns


Usage of external cloudmask
----------------------------

If a cloudmask for each file to be processed is available from an external source, make sure the cloudmask fulfills the following requirements:
* date (YYYYMMDD, eg 20210603) and tilename (NNCCC , eg 34VFN) in end of filenames: xxx_date_tile.xx
* supported raster file format (.tif, .jp2, and other formats supported by rasterio)
* binary rastervalues (1,0; with 1 representing clouds/invalid pixels)
* pixelsize == output pixelsize (given in config_x.yml)

The latter two criteria can be achieved by using the auxiliary script create_binary_cloudmask.py (but be aware of issue https://gitlab.com/eetun-tiimi/EODIE/-/issues/62)

Inner workflow
----------------

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