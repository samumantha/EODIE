User Manual
============

In this manual the general functionality of EODIE is described. In the end you can also find a usage example :ref:`example` (no external data needed).
For more examples with explanations, please check out :ref:`tutorial`.

Inputs 
^^^^^^^

The following sections describe EODIEs command line arguments and the configuration files. All of the following only matters when using EODIE as command line tool. 

Command line arguments
++++++++++++++++++++++

The following parameters and flags can be used in the commandline (more information on each parameter and flag below):

``python eodie_process.py --rasterdir/--rasterfile <> --vector <> --out <> --id <>  --gpkg_layer <> --epsg_for_csv <> --platform <> --statistics_out --geotiff_out --array_out --database_out --statistics <> --index <> --start <> --end <> --exclude_border --external_cloudmask <> --no_cloudmask --maxcloudcover <> --resampling_method <> --verbose --test``

Note that some parameters have options, some have defaults and some are optional, all flags are optional. See :ref:`nec_input` for inputs that need to be given.

| ``--platform``
| Which platform does the data come from? 
| **type:** String
| **options:** s2, ls8, tif
| The platform information needs to be given in order for EODIE to be able to read the data the right way, eg find tile and date information in the filename. It is possible to extent EODIE to be able to process other datasources than given in options. Please refer to :ref:`extending_eodie` for further information.

| ``--rasterdir``
| The directory where the data to be processed is stored as absolute path. 
| **type:** String
| EODIE can either be given a directory to process data from or a single file (use `--rasterfile` parameter instead). If a directory contains other data than what matches with `--platform`, `--startdate`/`--enddate`, (`maxcloudcover` in config) and the area of interest given as vectorfile, EODIE finds the fitting data based on these inputs. Avoid having dates in the format of YYYYMMDD and tilenames in format 00XXX in the path!

| ``--rasterfile``
| If only one file shall be processed use ``--rasterfile`` instead of ``--rasterdir``. Cannot be used together with ``--rasterdir``.
| **type:** String
| Either `--rasterdir` or `--rasterfile` needs to be given by user.

| ``--vector``
| Absolute path to the vector file to be used for processing.
| **type:** String
| The given vector defines the area of interest. Internally, EODIE reads the vector file into a geopandas GeoDataFrame.

| ``--out``
| Absolute path to the directory where the results shall be stored. Will be created if it does not exist.
| **type:** String
| **default:** ``./results``

| ``--id``
| Name of the unique ID-field of the vector file provided at ``--vector``.
| **type:** String
| **example:** ``--id id``
| Not all vector files use `id` as the fieldname for the ID field, it can be `ID`, `PlotID`,`FieldID`,`plotnumber`, etc. The possibilities are endless. Therefore EODIE cannot find the right field automatically and it has to be given by the user. If your vector file is not a GeoPackage, you may examine available fieldnames with the auxiliary script `examine_vectorfile.py`. With GeoPackage, you may use `examine_geopackage.py` (see also :ref:`auxfiles`).

| ``--gpkg_layer``
| If the input vectorfile is a GeoPackage (.gpkg), insert the name of the layer in GeoPackage to be processed if there are more than one layer. With one layer only this parameter is not needed.
| **type:** String
| **default:** None

| ``--epsg_for_csv``
| If the input vectorfile is a Comma-Separated Value (.csv), a spatial reference system needs to be defined separately for a successful reading into a GeoDataframe.
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

| ``--database_out``
| set flag if statistics (see below) shall be calculated ber polygon and saved into a sqlite3 .db file. Please be aware that with several simultaneous processes, the output database file can get locked and prevent writing results. 
| **type:** flag

| ``--statistics``
| If --statistics_out or --database_out is given, specify here which statistics shall be calculated per polygon separated by a space
| **type:** list of Strings
| **options:** one or more of: sum, std, median, mean, majority, minority, unique, range, percentile_x (with x from 0 to 100)
| **default:** ``count`` (always included)
| **example:** ``--statistics sum median percentile_10 percentile_90``

| ``--index``
| Which vegetation index or band shall be extracted per polygon separated by a space
| **type:** list of Strings
| **options:** one or more of ndvi, rvi, savi, nbr, kndvi, ndmi, mndwi, evi, evi2, dvi, cvi, mcari, ndi45, tctb, tctg, tctw, ndwi, plus bands as named in platform filenames (e.g. for Sentinel-2: B02, B03, B04, B05, B06, B07, B08, B8A, B11, B12)
| **example:** ``--index ndvi evi2 B04 B8A``

| ``--start``
| Give the startdate of the timeframe of interest
| **type:** integer YYYYMMDD
| **default:** ``20160101``

| ``--end``
| Give the enddate of the timeframe of interest
| **type:** integer YYYYMMDD
| **default:** todays date

| ``--delete_invalid_geometries``
| Flag to indicate that invalid geometries should be excluded from further processing. Does not necessarily work on all 
| **type**: flag

| ``--exclude_border``
| Flag to indicate that border pixels (within the polygon) should be excluded from statistics calculations / array extraction
| **type:** flag

| ``--external_cloudmask``
| [optional] Absolute path and name of external cloudmask (without tile and date and extension), if available
| **type:** String

| ``--verbose``
| For getting information and warnings in the terminal as well as the log file
| **type:** flag

| ``--test``
| For testing some datatypes are set to smaller, in general not needed by user 
| **type:** flag

| ``--maxcloudcover``
| A value restricting the processing of imagery with too high cloud coverage. Currently only working with Sentinel-2 imagery.
| **type:** integer
| **default**: 99

| ``--resampling_method``
|  If bands are not available directly in the given pixelsize, they need to be resampled. Here the resampling method for up- and downsampling can be changed.
| **Options:** Available resampling methods and a short description can be found here: https://rasterio.readthedocs.io/en/latest/api/rasterio.enums.html#rasterio.enums.Resampling
| **Example:** ``resampling_method: 'bilinear'`` will use bilinear resampling for all necessary resampling of the rasterdata

Configuration files
+++++++++++++++++++

[TODO: image of Sentinel-2 tiles over Finland]

EODIE includes platform-specific configuration files called config_x.yml with x being some platform name or tif. Generally, these configuration files do not need to be touched or changed. One exception to this is for example a 'red edge' band should be used in indices instead of the nir band, that could be changed in the platform specific configuration files. See more about this and about the possibility of extending EODIE to work with other platforms in ref:`platform_spec`.
However, if you wish to change the pixelsize for the outputs (for geotiffs and arrays), the value can be changed in these configuration files. 

| ``pixelsize`` 
| Enter the pixelsize that you want your results to be in. Bands are then resampled to match the given pixelsize. This has most influence on geotiff or array outputs.
| **Type:** Integer
| **Example:** ``pixelsize : 10`` will use bands that are available in 10 m as is and resample bands that are only available in larger pixelsizes to 10m before extracting statistics/array/geotiff

.. _nec_input:

Necessary inputs
^^^^^^^^^^^^^^^^^

| ``--platform --rasterdir/--rasterfile --vector --out --id`` and at least one of  ``--statistics_out/--geotiff_out/--array_out/--database_out``
| ``--index`` also needs to be given, unless ``--platform tif``


Outputs
^^^^^^^^

* A logfile: rasterdir_YYYY-MM-DD.log if --rasterdir was given; rasterfile_YYYY-MM-DD_HH-mm-ss if --rasterfile was given.

| ``--statistics_out``

* One csv per tile, band/vegetation index and date with polygon identifiers in the first column and statistics is the following columns.

| ``--array_out``

* One pickeled numpy array per tile, band/vegetation and date with all polygons

| ``--geotiff_out``

* One geotiff with georeferenced raster per tile, band/vegetation index and polygon

| ``--database_out``

* One SQLite3 database file (.db) that contains results for given indices or bands in tables. Structurally content is similar to statistics.


Usage of external cloudmask
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

If a cloudmask for each file to be processed is available from an external source, make sure the cloudmask fulfills the following requirements:

* date (YYYYMMDD, eg 20210603) and tilename (NNCCC , eg 34VFN) in end of filenames: xxx_date_tile.xx
* supported raster file format (.tif, .jp2, and other formats supported by rasterio)
* binary rastervalues (1,0; with 1 representing clouds/invalid pixels)
* pixelsize == output pixelsize (given in config_x.yml)

The latter two criteria can be achieved by using the auxiliary script create_binary_cloudmask.py (but be aware of issue https://gitlab.com/eetun-tiimi/EODIE/-/issues/62)


