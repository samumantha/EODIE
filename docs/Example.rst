.. _Example:

Small example 
==============

To test if the script runs as intended in your machine and to get familiar with the basic usage, please follow the instructions below:
(Commands provided for UNIX based OS)

0. If you have not done so yet, follow the installation instructions to install EODIE and activate the eodie environment.
1. Download the testfiles ``wget https://a3s.fi/swift/v1/AUTH_4df394386a5c4f8581f8a0cc34ba5b9a/2001106_eodie_testfiles/EODIE_Galaxy_testfiles.zip`` and unzip ``unzip EODIE_Galaxy_testfiles.zip`` to a place of your choice.
2. Run the following command (with your adjusted paths to where you stored the unzipped testfiles) from within your EODIE/src directory :

``python eodie_process.py --platform tif --rasterfile /path/to/your/EODIE_Galaxy_testfiles/smaller_area_20100401.tif --vector /path/to/your/EODIE_Galaxy_testfiles/test_polygons.shp --id id --statistics_out --statistics mean std median ``

with:

* ``--platform`` which platform the data in ``--rasterfile`` comes from
* ``--rasterfile`` the location of the tif file to be processed,
* ``--vector`` full path of the vector file with polygons to extract information of
* ``--id`` the fieldname of a unique ID for each polygon in the vectorfile
* ``--statistics_out`` to get statistics as output
* ``--statistics mean std median`` which statistics to process for each polygon in ``--vector``

6. This should create file ``testrgb_20100401__statistics.csv`` in ./results directory.
7. If not, please check your installation and that the testfiles were downloaded correctly.

Larger example using Sentinel-2 data
======================================

0. If you have not done so yet, follow the installation instructions to install EODIE and activate the eodie environment.
1. Download the testfiles ``wget https://a3s.fi/swift/v1/AUTH_4df394386a5c4f8581f8a0cc34ba5b9a/2001106_eodie_testfiles/testfiles.zip`` and unzip ``unzip testfiles.zip`` to a place of your choice, this may take a moment.
2. Also download the Sentinel-2 tilegrid in KML format from `here <https://sentinels.copernicus.eu/web/sentinel/missions/sentinel-2/data-products>`_ and run the following command from within your EODIE/helper_scripts directory:
``python tilegrid_to_shp.py path/to/tilegrid/KML/file`` . After running, there should be a folder ``sentinel2_tiles_world`` within EODIE/src directory, containing ``sentinel2_tiles_world.shp`` and auxiliary files. 

3. Run the following command (with your adjusted paths to where you stored the unzipped testfiles) from within your EODIE/src directory :

``python eodie_process.py --platform s2 --rasterdir /path/to/testfiles/S2 --vector /path/to/testfiles/shp/test_parcels_32635.shp --out ./results --id ID --statistics_out --index ndvi --statistics mean median std``

with:

* ``--rasterdir`` the location of the Sentinel-2 SAFE products to be processed,
* ``--vector`` full path of the vector with polygons to extract information of
* ``--id`` the fieldname of a unique ID for each polygon in the vectorfile
* ``--out`` the location where outputs of the process will be stored
* ``--statistics_out`` to get statistics as output
* ``--platform`` which platform the data in ``--dir`` comes from
* ``--index`` which index to calculate

4. This should create file ``ndvi_20200626_34VFN_statistics.csv`` in results directory.
5. If not, please check your installation and that the testfiles were downloaded correctly.


Examples on using different vector input formats
================================================

EODIE can directly read vector file formats supported by `fiona <https://fiona.readthedocs.io/en/latest/manual.html>`_. With GeoPackage and Comma-Separated Value files there are some extra steps. 

GeoPackage
----------

GeoPackages can contain one or several vector layers, which complicates things a bit.

If there is only one layer in the input GeoPackage, no extra inputs are needed. 

``python eodie_process.py --platform tif --rasterfile /path/to/your/EODIE_Galaxy_testfiles/smaller_area_20100401.tif --vector /path/to/your/EODIE_Galaxy_testfiles/test_polygons.gpkg--id id --statistics_out --statistics mean std median``

If there are more than one layers in the input GeoPackage, the user needs to additionally define the layer to be used. If no layer is defined, EODIE will throw an error.
Let's imagine the test_polygons.gpkg contains two layers, called ``polygons`` and ``points``, and we want to use the ``polygons`` layer. In this case, we will define the name of the layer with argument --gpkg_layer.
The call would then be

``python eodie_process.py --platform tif --rasterfile /path/to/your/EODIE_Galaxy_testfiles/smaller_area_20100401.tif --vector /path/to/your/EODIE_Galaxy_testfiles/test_polygons.gpkg --gpkg_layer polygons --id id --statistics_out --statistics mean std median``

If you do not know, how many layers your GeoPackage contains and what the layer names are, you can examine the GeoPackage with auxiliary script ``examine_geopackage.py`` (see also :ref:`auxfiles`).

CSV 
---

To be used with EODIE, CSV file needs to contain the spatial information in one column as well-known text (WKT). Currently columns with x & y point coordinates are not supported.
Additionally, EODIE has to know in which EPSG-code the spatial information is provided. This EPSG-code will be defined with another input parameter --epsg_for_csv. If --epsg_for_csv is not defined, EODIE will throw an error. 

The EPSG code for the test_polygons file is 3067, so it will be used here as an example.

``python eodie_process.py --platform tif --rasterfile /path/to/your/EODIE_Galaxy_testfiles/smaller_area_20100401.tif --vector /path/to/your/EODIE_Galaxy_testfiles/test_polygons.csv --epsg_for_csv 3067 --id id --statistics_out --statistics mean std median``

If the EPSG code is defined wrong, EODIE might run but produce false or no results.
