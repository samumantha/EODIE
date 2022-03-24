.. _Example:

Small example 
==============

To test if the script runs as intended in your machine and to get familiar with the basic usage, please follow the instructions below:
(Commands provided for UNIX based OS)

0. If you have not done so yet, follow the installation instructions to install EODIE and activate the eodie environment.
1. Download the testfiles ``wget https://a3s.fi/swift/v1/AUTH_4df394386a5c4f8581f8a0cc34ba5b9a/2001106_eodie_testfiles/EODIE_Galaxy_testfiles.zip`` and unzip ``unzip EODIE_Galaxy_testfiles.zip`` to a place of your choice.
2. Run the following command (with your adjusted paths to where you stored the unzipped testfiles) from within your EODIE/src directory :

``python eodie_process.py --platform tif --rasterfile /path/to/your/EODIE_Galaxy_testfiles/smaller_area_20100401.tif --vector /path/to/your/EODIE_Galaxy_testfiles/test_polygons --id id --statistics_out --statistics mean std median --exclude_splitbytile``

with:

* ``--platform`` which platform the data in ``--file`` comes from
* ``--rasterfile`` the location of the tif file to be processed,
* ``--vector`` the location and name of the vector file with polygons to extract information of
* ``--id`` the fieldname of a unique ID for each polygon in the shapefile
* ``--statistics_out`` to get statistics as output
* ``--statistics mean std median`` which statistics to process for each polygon in ``--shp``
* ``--exclude_splitbytile`` necessary flag when not working with supported tiled data

6. This should create file ``testrgb_20100401__statistics.csv`` in ./results directory.
7. If not, please check your installation and that the testfiles were downloaded correctly.

Larger example using Sentinel-2 data
======================================

0. If you have not done so yet, follow the installation instructions to install EODIE and activate the eodie environment.
1. Download the testfiles ``wget https://a3s.fi/swift/v1/AUTH_4df394386a5c4f8581f8a0cc34ba5b9a/2001106_eodie_testfiles/testfiles.zip`` and unzip ``unzip testfiles.zip`` to a place of your choice, this may take a moment.
2. Also download the Sentinel-2 tile shapefile , originally provided by https://fromgistors.blogspot.com/2016/10/how-to-identify-sentinel-2-granule.html, ``wget -O sentinel2_tiles_world.zip https://a3s.fi/swift/v1/AUTH_4df394386a5c4f8581f8a0cc34ba5b9a/2001106_eodie_testfiles/sentinel2_tiles_world.zip`` and unzip them ``unzip sentinel2_tiles_world.zip``

3. Run the following command (with your adjusted paths to where you stored the unzipped testfiles) from within your EODIE/src directory :

``python eodie_process.py --dir /path/to/testfiles/S2 --shp /path/to/testfiles/shp/test_parcels_32635 --out ./results --id ID --statistics_out --platform s2 --index ndvi --statistics mean median std``

with:

* ``--rasterdir`` the location of the Sentinel-2 SAFE products to be processed,
* ``--vector`` the location and name of the vector with polygons to extract information of
* ``--id`` the fieldname of a unique ID for each polygon in the shapefile
* ``--out`` the location where outputs of the process will be stored
* ``--statistics_out`` to get statistics as output
* ``--platform`` which platform the data in ``--dir`` comes from
* ``--index`` which index to calculate

4. This should create file ``ndvi_20200626_34VFN_statistics.csv`` in results directory.
5. If not, please check your installation and that the testfiles were downloaded correctly.





