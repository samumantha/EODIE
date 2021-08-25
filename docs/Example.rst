.. _Example:

Example 
========

To test if the script runs as intended in your machine and to get familiar with the basic usage, please follow the instructions below:
(Commands provided for UNIX based OS)

1. Download the testfiles and unzip ``wget https://a3s.fi/swift/v1/AUTH_4df394386a5c4f8581f8a0cc34ba5b9a/2001106_eodie_testfiles/testfiles.zip`` and then ``unzip testfiles.zip``, this may take a moment.
2. Also download the Sentinel-2 tile shapefile , provided https://fromgistors.blogspot.com/2016/10/how-to-identify-sentinel-2-granule.html, ``wget -O sentinel2_tiles_world.zip https://docs.google.com/uc?id=0BysUrKXWIDwBZHF6dENlZ0g1Y0k`` and then ``unzip sentinel2_tiles_world.zip``

3. Create conda environment from environment.yml ``conda env create -f environment.yml``
4. Activate conda environment eodie ``conda activate eodie``
5. run following command:

``python process.py --dir ./testfiles/S2 --shp ./testfiles/shp/test_parcels_32635 --out ./results --id ID --statistics_out --platform s2 --index ndvi``

with:

* ``--dir`` the location of the Sentinel-2 SAFE products to be processed,
* ``--shp`` the location and name of the shapefile with polygons to extract information of
* ``--id`` the fieldname of a unique ID for each polygon in the shapefile
* ``--out`` the location where outputs of the process will be stored
* ``--statistics_out`` to get statistics as output
* ``--platform`` which platform the data in ``--dir`` comes from
* ``--index`` which index to calculate

6. This should create file ``ndvi_20200626_34VFN_statistics.csv`` in results directory.
7. If not, please check your installation and that the testfiles were downloaded correctly.





