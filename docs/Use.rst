User Manual
============

In this manual the general functionality of EODIE is described. In the end you can also find a usage example :ref:`example` (no external data needed).
For more examples with explanations, please check out :ref:`tutorial`.

Inputs 
^^^^^^^

The following sections describe EODIEs command line arguments and the configuration files. All of the following only matters when using EODIE as command line tool. 

Command line arguments
++++++++++++++++++++++

The following parameters can be used in the commandline:
Note that some parameters have options, some have defaults and some are optional, all flags are optional. See :ref:`nec_input` for inputs that need to be given 

| ``--platform``
| Which platform does the data come from? 
| **type:** String
| **options:** s2, ls8, tif
| The platform information needs to be given in order for EODIE to be able to read the data the right way, eg find tile and date information in the filename. It is possible to extent EODIE to be able to process other datasources than given in options. Please refer to :ref:`extending_eodie` for further information.

| ``--dir``
| The directory where the data to be processed is stored as absolute path. 
| **type:** String
| EODIE can either be given a directory to process data from or a single file (use `--file` parameter instead). If a directory contains other data than what matches with `--platform`, `--startdate`/`--enddate`, (`maxcloudcover` in config) and the area of interest given as shapefile, EODIE finds the fitting data based on these inputs. Avoid having dates in the format of YYYYMMDD and tilenames in format 00XXX in the path!

| ``--file``
| If only one file shall be processed use ``--file`` instead of ``--dir``. Cannot be used together with ``--dir``.
| **type:** String
| Either `--dir` or `--file` needs to be given by user.

| ``--shp``
| Absolute path to the shapefile to be used for processing, without extension and tilename.
| **type:** String
| **example:** Shapefile name is test_polygons.shp in location /home/my/path, then it is given as --shp /home/my/path/test_polygons
| The given shapefile defines the area of interest. Internally, EODIE splits the shapefile based on tiles (`tileshp` in config) and uses that part of the shapefile that has the same tilename as the file to be processed.

| ``--out``
| Absolute path to the directory where the results shall be stored. Will be created if it does not exist.
| **type:** String
| **default:** ``./results``

| ``--id``
| Name of the unique ID-field of the shapefile provided at ``--shp``.
| **type:** String
| **example:** ``--id id``
| Not all shapefiles use `id` as the fieldname for the ID field, it can be `ID`, `PlotID`,`FieldID`,`plotnumber`, etc. The possibilities are endless. Therefore EODIE cannot find the right field automatically and it has to be given by the user. You may examine available fieldnames with the auxiliary script `examine_shapefile.py` (see also :ref:`auxfiles`).

| ``--input_type``
| The file extension of the input file provided in --shp. Supported extensions are .shp, .gpkg, .geojson, .csv and .fgb. If you are using GeoPackage, bear in mind there can be only one layer within. Csv files also need a column for well-known text (WKT) to determine the spatial extent of each feature. 
| **type:** String
| **default:** .shp

| ``--epsg_for_csv``
| If --input_type is .csv, a spatial reference system needs to be defined separately for a successful to a shapefile, as it is not a part of the file structure. 
| **type:** String
| **default:** None

| ``--statistics_out``
| set flag if statistics (see below) shall be calculated per polygon and saved as csv
| **type:** flag

| ``--geotiff_out``
| set flag if geotiff shall be extracted per polygon and saved as geotiff
| **type:** flag

| ``--array_out``
| set flag if arrays of all polygons shall be extracted and saved as pickle
| **type:** flag
| If none of the three above is given, only --statistics_out is set to true

| ``--statistics``
| If --statistics_out is given, specify here which statistics shall be calculated per polygon separated by a space
| **type:** list of Strings
| **options:** one or more of: sum, std, median, mean, majority, minority, unique, range, percentile_x (with x from 0 to 100)
| **default:** ``count`` (always included)
| **example:** ``--statistics sum median percentile_10 percentile_90``

| ``--index``
| Which vegetation index or band shall be extracted per polygon separated by a space
| **type:** list of Strings
| **options:** one or more of ndvi, rvi,savi,nbr,kndvi, ndmi, mndwi, evi, evi2, dvi, cvi, mcari, ndi45, tctb, tctg, tctw, ndwi, plus bands as named in platform filenames (e.g. for Sentinel-2: B02, B03, B04, B05, B06, B07, B08, B8A, B11, B12)
| **example:** ``--index ndvi evi2 B04 B8A``

| ``--start``
| Give the startdate of the timeframe of interest
| **type:** integer YYYYMMDD
| **default:** ``20160101``

| ``--end``
| Give the enddate of the timeframe of interest
| **type:** integer YYYYMMDD
| **default:** todays date

| ``--keep_shp``
| Flag to indicate all necessary shapefiles created when running EODIE should be stored for further usage
| **type:** flag 

| ``--exclude_border``
| Flag to indicate that border pixels (within the polygon) should be excluded from statistics calculations / array extraction
| **type:** flag

| ``--external_cloudmask``
| [optional] Absolute path and name of external cloudmask (without tile and date and extension) if available
| **type:** String

| ``--exclude_splitshp``
| Flag to indicate that splitshp has been run manually beforehand
| **type:** flag

| ``--verbose``
| For getting information and warnings in the terminal as well as the log file
| **type:** flag

| ``--test``
| For testing some datatypes are set to smaller, in general not needed by user 
| **type:** flag


Configuration file
+++++++++++++++++++

Some adjustments only need to be set once by the user. These are available in `user_config.yml`.
The most important setting in the userconfig is the path to the tile shapefile (`tileshp`) and the fieldname where the tilename is stored (`fieldname`).
The tileshapefile is a shapefile containing the units, also called tiles, that data is provided for each platform. 

[TODO: image of Sentinel-2 tiles over Finland]

When processing data that is not tiled, or no tile shapefile is provided, this parameter can be left empty.

Other settings that can be adjusted in the configuration file are:

| ``maxcloudcover``
| Enter the maximum cloudcover of a file that is still processed in percentage
| **Type:** Integer
| **Example:** ``maxcloudcover: 99`` excludes all files in the directory that have > 99 % cloudcover over the whole tile according to metadata.

| ``pixelsize`` 
| Enter the pixelsize that you want your results to be in. Bands are then resampled to match the given pixelsize. This has most influence on geotiff or array outputs.
| **Type:** Integer
| **Example:** ``pixelsize : 10`` will use bands that are available in 10 m as is and resample bands that are only available in larger pixelsizes to 10m before extracting statistics/array/geotiff

| ``resampling method``
| If bands are not available directly in the given pixelsize, they need to be resampled. Here the resampling method for up- and downsampling can be changed.
| **Options:** available resampling methods and a short description can be found here: https://rasterio.readthedocs.io/en/latest/api/rasterio.enums.html#rasterio.enums.Resampling
| **Example:** ``resampling_method: 'bilinear'`` will use bilinear resampling for all necessary resampling of the rasterdata

EODIE also includes other configuration files called config_x.yml with x being some platform name or tif. These configuration files do not need to be touched or changed in general. One exception to this is for example a 'red edge' band should be used in indices instead of the nir band, that could be changed in the platform specific configuration files. See more about this and about the possibility of extending EODIE to work with other platforms in ref:`platform_spec`.

.. _nec_input:

Necessary inputs
^^^^^^^^^^^^^^^^^

| ``--platform --dir/--file --shp --out --id`` and at least one of  ``--statistics_out/--geotiff_out/--array_out``
| ``--index`` also needs to be given, unless ``--platform tif``


Outputs
^^^^^^^^

* A logfile: YYYYMMDD-hhmmss.log 

| ``--statistics_out``

* One csv per tile, band/vegetation index and date with polygon identifiers in the first column and statistics is the following columns.

| ``--array_out``

* One pickeled numpy array per tile, band/vegetation and date with all polygons

| ``--geotiff_out``

* One geotiff with georeferenced raster per tile, band/vegetation index and polygon


Usage of external cloudmask
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

If a cloudmask for each file to be processed is available from an external source, make sure the cloudmask fulfills the following requirements:

* date (YYYYMMDD, eg 20210603) and tilename (NNCCC , eg 34VFN) in end of filenames: xxx_date_tile.xx
* supported raster file format (.tif, .jp2, and other formats supported by rasterio)
* binary rastervalues (1,0; with 1 representing clouds/invalid pixels)
* pixelsize == output pixelsize (given in config_x.yml)

The latter two criteria can be achieved by using the auxiliary script create_binary_cloudmask.py (but be aware of issue https://gitlab.com/eetun-tiimi/EODIE/-/issues/62)


