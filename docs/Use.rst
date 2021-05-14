Usage
======


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

