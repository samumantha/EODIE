.. _tutorial:

Tutorial 
=========

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

1. Call EODIE ``python eodie_process.py --rasterdir S2files/dir --vector full/path/to/shapefile.shp --out ./results --id PlotID --database_out --index ndvi --statistics mean`` 
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

1. Call EODIE: ``python eodie_process.py --rasterdir S2files/dir --vector full/path/to/shapefile.shp --out ./results --id PlotID --array_out --index ndvi`` this results in a number of single pickle files, one for each tile and date with all ids 
3. (optional) Use arrayplot.py in postprocesses to show/save timeseries plots from wished ids.

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
    #SBATCH --output=/path/to/job/output/array_job_out_%A_%a.txt # Path to where the output text files will be saved
    #SBATCH --error=/path/to/job/output/array_job_err_%A_%a.txt # Path to where the error text files will be saved
    #SBATCH --time=00:15:00 # Estimation of the time it takes to process the files
    #SBATCH --ntasks=1 # The number of tasks
    #SBATCH --partition=small # The estimated processing power needed limitations (more partitions can be found in https://docs.csc.fi/computing/running/batch-job-partitions/)
    #SBATCH --mem-per-cpu=5000 # Estimation of how much memory is needed per cpu
    #SBATCH --cpus-per-task=n # Change n to the number of CPUs per task  

    module load geoconda # Loads the needed module for processing    

    cd /path/to/the/program/EODIE/src/ # Needs to be in the EODIE directory to work properly

    # The actual processing:
    python eodie_process.py --platform s2 --rasterdir /path/to/directory/with/SAFEs/ --vector /path/to/vectorfile --out ./results --id PlotID --database_out --index ndvi --statistics mean median std range
    # More specific arguments and their purpose can be found in EODIE documentation:  https://eodie.readthedocs.io/en/latest/   

3. call ``sbatch name_of_above_script.sh``

Case 4: As Case 3 but with data on objectstorage
-------------------------------------------------

| Available on objectstorage:

- Sentinel-2 data for years 2017-2020 of whole country in buckets named xxx

| Available on supercomputer:

- fieldparcel polygons of area x as ESRI shapefile, with unique ID fieldname 'PlotID'

| Additional input:

- timeframe: April 1st - August 31st year 2018 

| Desired output:

- csv file with NDVI timeseries for each fieldparcel polygon

| Workflow:

1. Same as Case 1
2. Similar as Case 3 but this needs two more scripts. Script one, called run_smart_processing.sh:

.. code-block:: bash

    arglist=$@

    ./per_safe.sh $arglist

    sbatch --array 1-$(less ./arr_temp/count.txt) sbatch_smart.sh

Script 2, called per_safe.sh:

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

    rm -r arr_temp
    mkdir arr_temp

    for year in $timeperiod; do
        for tile in $tiles; do
            bucket="$basebucket-$year-T$tile"
            echo $bucket
            s3cmd ls $bucket >> ./arr_temp/bucketfiles_temporary.txt
        done
    done

    for line in $(less ./arr_temp/bucketfiles_temporary.txt); do
        if [ $(echo $line | cut -c1-2) == "s3" ] && [ $(echo ${line#*/*/*/}) != "index.html" ]; then
            echo $line >> ./arr_temp/safedirs_temporary.txt
        fi
    done

    rm ./arr_temp/bucketfiles_temporary.txt

    for line in $(less ./arr_temp/safedirs_temporary.txt); do
        first_cut=${line#*_*_}
        date_time=${first_cut%_*_*_*_*}
        date=${date_time%T*}
        if [ $date -ge $start ] && [ $date -le $end ]; then
            echo ${line%/} >> ./arr_temp/safedirs_final.txt
        fi
    done

    rm ./arr_temp/safedirs_temporary.txt

    count=0
    for line in $(less ./arr_temp/safedirs_final.txt); do
        count=$((count+1))
    done

    echo $count > ./arr_temp/count.txt


Third script similar to the one in Case 3:

.. code-block:: bash

    #!/bin/bash -l
    #SBATCH --job-name=smart_xxx
    #SBATCH --account=project_xxx
    #SBATCH --output=/scratch/project_xxx/out/array_job_out_%A_%a.txt
    #SBATCH --error=/scratch/project_xxx/out/array_job_err_%A_%a.txt
    #SBATCH --time=00:25:00
    #SBATCH --ntasks=1
    #SBATCH --mem-per-cpu=8000
    #SBATCH --partition=small

    module load allas

    path=/scratch/project_xxx/smart_process/arr_temp
    cd $path


    name=$(sed -n ${SLURM_ARRAY_TASK_ID}p $path/safedirs_final.txt)
    local_dir="job_${SLURM_ARRAY_TASK_ID}"
    mkdir $path/$local_dir
    mkdir $path/$local_dir/SAFE
    cp -r /scratch/project_xxx/shp $path/$local_dir 
    s3cmd get -r $name $path/$local_dir/SAFE

    module unload allas
    module load geoconda

    cd /scratch/project_xxx/EODIE/src/eodie

    python eodie_process.py --rasterdir $path/$local_dir/SAFE --vector $path/$local_dir/shp/name_of_shapefile --out ./results --id PlotID --statistics_out --index ndvi

    rm -r $path/$local_dir

3. call ``bash run_smart_processing.sh startdate enddate tile1 tile2 tile3`` with dates in YYYYMMDD format and tilenames in XX000 format. In this case the tilenames need to be identified beforehand
