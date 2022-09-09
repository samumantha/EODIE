.. _tutorial:

Tutorial 
=========

On this page are examples of running EODIE in different environments (your own computer vs. a high-performance computing environment) and with different platforms. The basics are the same regardless of platform.
Tutorials for Landsat 8 can be found below Sentinel-2 tutorials.

Sentinel-2 tutorials
=====================


Case 1: growing season mean NDVI timeseries of agricultural fieldparcels of area x (larger than one Sentinel-2 tile)
---------------------------------------------------------------------------------------------------------------------

| Available on computer:

- Sentinel-2 data for years 2017 - 2020 of whole country
- fieldparcel polygons of area x as ESRI shapefile, with unique ID fieldname 'PlotID'

| Additional input:

- timeframe: April 1st - August 31st year 2018 

| Desired output:

- SQLite database containing mean NDVI timeseries for each fieldparcel polygon 

| Workflow:

1. Call EODIE ``python eodie_process.py --platform s2 --rasterdir S2files/dir --vector full/path/to/shapefile.shp --out ./results --id PlotID --database_out --index ndvi --statistics mean`` 
This results into a single SQLite database file (.db) containing results in a table named "ndvi".
2. (optional) Use export_from_database.py script in postprocesses to extract values from database into a single .csv file.

Case 2: As Case 1 but field parcel array timeseries are the desired output
---------------------------------------------------------------------------

| Available on computer:

- Sentinel-2 data for years 2017 - 2020 of whole country 
- fieldparcel polygons of area x as ESRI shapefile, with unique ID fieldname 'PlotID'

| Additional input:

- timeframe: April 1st - August 31st year 2018 

| Desired output:

- timeseries of fieldparcel arrays

| Workflow:

1. Call EODIE: ``python eodie_process.py --platform s2 --rasterdir S2files/dir --vector full/path/to/shapefile.shp --out ./results --id PlotID --array_out --index ndvi`` this results in a number of single pickle files, one for each tile and date with all ids 
2. (optional) Use arrayplot.py in postprocesses to show/save timeseries plots from wished ids.

Case 3: As Case 1 but processing done on HPC environment with SLURM
------------------------------------------------------------------------------------------------------------

| Available on supercomputer:

- Sentinel-2 data for years 2017-2020 of whole country
- fieldparcel polygons of area x as ESRI shapefile, with unique ID fieldname 'PlotID'

| Additional input:

- timeframe: April 1st - August 31st year 2018 

| Desired output:

- database with NDVI timeseries for each fieldparcel polygon with statistics mean, median, standard deviation and range

| Workflow:

1. Create a batch job script (example below is for CSCs Puhti supercomputer) with your data

.. code-block:: bash

    #!/bin/bash -l
    #SBATCH --job-name=   # Give the job a name
    #SBATCH --account=project_  # The project number on which the resources will be spent
    #SBATCH --output=/path/to/job/output/%J_out.txt # Path to where the output text files will be saved
    #SBATCH --error=/path/to/job/output/%J_err.txt # Path to where the error text files will be saved
    #SBATCH --time=02:00:00 # Estimation of the time it takes to process the files
    #SBATCH --ntasks=1 # The number of tasks
    #SBATCH --partition=small # The estimated processing power needed limitations (more partitions can be found in https://docs.csc.fi/computing/running/batch-job-partitions/)
    #SBATCH --mem-per-cpu=5000 # Estimation of how much memory is needed per cpu
    #SBATCH --cpus-per-task=n # Change n to the number of CPUs per task  

    module load geoconda # Loads the needed module for processing    

    cd /path/to/the/program/EODIE/src/ # Needs to be in the EODIE directory to work properly

    # The actual processing:
    python eodie_process.py --platform s2 --rasterdir /path/to/directory/with/SAFEs/ --vector /path/to/vectorfile.shp --out ./results --id PlotID --database_out --index ndvi --statistics mean median std range
    # More specific arguments and their purpose can be found in EODIE documentation:  https://eodie.readthedocs.io/en/latest/   

3. call ``sbatch name_of_above_script.sh``

Case 4: As Case 3 but with data on objectstorage
-------------------------------------------------

| Available on objectstorage:

- Sentinel-2 data for years 2017-2020 of whole country in buckets named Sentinel2-MSIL2A-cloud-0-95-YEAR-TTILE

| Available on supercomputer:

- fieldparcel polygons of area x as ESRI shapefile, with unique ID fieldname 'PlotID'

| Desired output:

- database with NDVI timeseries for each fieldparcel polygon in the whole country with statistics mean, median, standard deviation and range

| Workflow:

1. Similar as Case 3 but this needs another script, called download_and_eodie.sh, for downloading the input files from object storage and launching EODIE after download is completed:

.. code-block:: bash

    start=$1
    end=$2
    startyear=$(echo $start | cut -c1-4)
    endyear=$(echo $end | cut -c1-4)
    shift
    shift
    tiles=$@
    basebucket="s3://Sentinel2-MSIL2A-cloud-0-95"
    timeperiod=$(seq $startyear $endyear)

    for year in $timeperiod; do
        for tile in $tiles; do 
            # Create a directory to download the imagery into
            mkdir $year-$tile
            # Define bucket name
            bucket="$basebucket-$year-T$tile"
            echo $bucket
            # Load files from bucket to directory
            s3cmd get -r $bucket/ $year-$tile/
            # Send batch job with directory name as argument
            sbatch sbatch_smart.sh $year-$tile/
        done
    done

2. The main batch job script is similar to the one in Case 3, called sbatch_smart.sh:

.. code-block:: bash

    #!/bin/bash -l
    #SBATCH --job-name=smart_xxx
    #SBATCH --account=project_xxx
    #SBATCH --output=/scratch/project_xxx/out/%J_out.txt
    #SBATCH --error=/scratch/project_xxx/out/%J_err.txt
    #SBATCH --time=02:00:00 # Depending on the complexity of your vectorfile, this time window might not be enough.
    #SBATCH --ntasks=1
    #SBATCH --cpus-per-task=5
    #SBATCH --mem-per-cpu=8G
    #SBATCH --partition=small

    # Store argument into variable
    path=$1

    module load geoconda

    cd /scratch/project_xxx/EODIE/src/

    # Call EODIE
    python eodie_process.py --platform s2 --rasterdir $path --vector path/to/vectorfile.shp --out ./results --id PlotID --database_out --index ndvi --statistics mean median std range

    # When ready, the contents of variable $path can be removed as the files are in object storage. Please make sure you have reserved enough time and computational resources for finishing the computations to avoid unnecessary deletion of raster files (or comment the rm off).
    rm -r $path/

3. Call ``bash download_and_eodie.sh startdate enddate tile1 tile2 tile3`` with dates in YYYYMMDD format and tilenames in XX000 format. In this case the tilenames need to be identified beforehand. This will launch the script in step 1 that will proceed to launch EODIE for each tile and year requested. 

Landsat 8 Tutorials
===================

Please note: EODIE currently works only with Landsat 8 Collection 2 data.

Case 1: Growing season mean NDVI timeseries of agricultural fieldparcels of area x (larger than one Landsat 8 tile)
---------------------------------------------------------------------------------------------------------------------

| Available on computer:

- Landsat 8 data downloaded from Earth Explorer as .tar files, covering growing season 2019
- fieldparcel polygons of area x as ESRI shapefile, with unique ID fieldname 'PlotID'

| Desired output:

- SQLite database containing mean NDVI timeseries for each fieldparcel polygon 

| Workflow:

1. Downloading Landsat 8 data from Earth Explorer results to .tar files, from which the imagery needs to be extracted. The goal is to create a directory with the name of the tar file and extract files into the directory.
This can be achieved with some basic software, but in helper scripts there is also script ``extract_from_tar.py`` to do this task for all (Landsat 8) tars in a given directory. 

2. In addition to Landsat 8 imagery, the tiling grid is required. It can be downloaded `here [Descending (daytime)] <https://www.usgs.gov/landsat-missions/landsat-shapefiles-and-kml-files>`_. After downloading, manually unzip and relocate the shapefile to EODIE's source directory or use auxiliary script unzip_ls8_grid.py.

3. After extracting the data, EODIE can be called. Call is basically same as with Sentinel-2 data, but arguments --platform and --rasterdir need to be changed.
``python eodie_process.py --platform ls8 --rasterdir dir/with/extracted/Landsat8/folders/ --vector full/path/to/shapefile.shp --out ./results --id PlotID --database_out --index ndvi --statistics mean median std range``

Case 2: As Case 1 but processing done on HPC environment with SLURM
------------------------------------------------------------------------------------------------------------

| Available on supercomputer:

- Landsat 8 data downloaded from Earth Explorer and extracted from .tar files, covering growing season 2019
- fieldparcel polygons of area x as ESRI shapefile, with unique ID fieldname 'PlotID'

| Additional input:

- timeframe: May 1st - July 31st year 2019

| Desired output:

- database with NDVI timeseries for each fieldparcel polygon with statistics mean, median, standard deviation and range

| Workflow:

1. Create a batch job script (example below is for CSCs Puhti supercomputer) with your data

.. code-block:: bash

    #!/bin/bash -l
    #SBATCH --job-name=EODIE_landsat  # Give the job a name
    #SBATCH --account=project_  # The project number on which the resources will be spent
    #SBATCH --output=/path/to/job/output/%J_out.txt # Path to where the output text files will be saved
    #SBATCH --error=/path/to/job/output/%J_err.txt # Path to where the error text files will be saved
    #SBATCH --time=02:00:00 # Estimation of the time it takes to process the files
    #SBATCH --ntasks=1 # The number of tasks
    #SBATCH --partition=small # The estimated processing power needed limitations (more partitions can be found in https://docs.csc.fi/computing/running/batch-job-partitions/)
    #SBATCH --mem-per-cpu=5000 # Estimation of how much memory is needed per cpu
    #SBATCH --cpus-per-task=n # Change n to the number of CPUs per task  

    module load geoconda # Loads the needed module for processing    

    cd /path/to/the/program/EODIE/src/ # Needs to be in the EODIE directory to work properly

    # The actual processing:
    python eodie_process.py --platform ls8 --rasterdir dir/with/extracted/Landsat8/folders/ --vector full/path/to/shapefile.shp --out ./results --id PlotID --database_out --index ndvi --statistics mean median std range --start 20190501 --end 20190731``
    # More specific arguments and their purpose can be found in EODIE documentation:  https://eodie.readthedocs.io/en/latest/   

2. call ``sbatch name_of_above_script.sh``
