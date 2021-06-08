.. _example:

Example 
========

To test if the script runs as intended in your machine and to get familiar with the basic usage, please follow the instructions below:
(Commands provided for UNIX based OS)

1. Download the testfiles and unzip ``wget https://a3s.fi/swift/v1/AUTH_4df394386a5c4f8581f8a0cc34ba5b9a/2001106_eodie_testfiles/testfiles.zip | unzip testfiles.zip``, this may take a moment (testfiles.zip has 240MB)
2. Create conda environment from environment.yml ``conda env create -f environment.yml``
3. Activate conda environment eodie ``conda activate eodie``
4. run following command:
    ``python process.py --dir ./testfiles/S2 --shp ./testfiles/shp/test_parcels_32635 --out ./results --id ID --stat 1 --index ndvi``
5. This should create file ``ndvi_20200626_34VFN_stat.csv`` in results directory.
6. If not, follow the traceback.



