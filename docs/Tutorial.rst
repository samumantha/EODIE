.. _tutorial:

Tutorial 
=========

Case 1: growing season mean NDVI timeseries of agricultural fieldparcels of area x (larger than one Sentinel-2 tile)
---------------------------------------------------------------------------------------------------------------------

Available on computer:

- Sentinel-2 data for years 2017-2020 of whole country:  
- fieldparcel polygons of area x as ESRI shapefile, with unique ID fieldname 'PlotID'

Additional input:
- timeframe: April 1st - August 31st year 2018 

Desired output:

- csv file with NDVI timeseries for each fieldparcel polygon

Workflow:

1. shp_preparation 
    split the shapefile based on Sentinel-2 testfiles
    `` pyhon splitshp.py fieldparcelshp sentinel2tileshp outdir``
2. update configuration file
    open ``config.yml`` with your favorite text editor, eg ``nano config.yml`` and edit it to fit your needs,
    in this case we want to process a pixel size of 10 meters, and use all Sentinel-2 files that have a cloudcover of under 60%, 
    so the config.yml file would look like this
    ```
    maxcloudcover: 60
    resolution: 10
    ```
3. call eodie and store results in results directory
    ``python process.py --dir S2files/dir --shp name/of/shapefile --out ./results --id PlotID --stat 1 --index ndvi``
    this results in a number of single csv files, one for each tile and date

4. call combinator to combine single csv files into one with mean
5. plot timeseries with plotter

Case 2: Data available on object storage and processing done on HPC environment with SLURM
--------------------------------------------------------------------------------------------

