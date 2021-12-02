.. _tutorial:

Tutorial 
=========


Case 1: growing season mean NDVI timeseries of agricultural fieldparcels of area x (larger than one Sentinel-2 tile)
---------------------------------------------------------------------------------------------------------------------

| Available on computer:

- Sentinel-2 data for years 2017 - 2020 of whole country
- fieldparcel polygons of area x as ESRI shapefile, with unique ID fieldname 'PlotID'

| Additional input:

- timeframe: April 1st - August 31st year 2018 

| Desired output:

- csv file with NDVI timeseries for each fieldparcel polygon

| Workflow:

1. Update configuration file
    open ``user_config.yml`` with your favorite text editor, eg ``nano config.yml`` and edit it to fit your needs,
    in this case we want to process a pixel size of 10 meters, and use all Sentinel-2 files that have a cloudcover of under 99%, 
    so the config.yml file would look like this

    .. code-block:: bash

        maxcloudcover: 99
        resolution: 10
        tileshp: path/to/sentinel2-tiles-world.shp
        fieldname: Name
        resampling_method: 'bilinear'

2. Call EODIE ``python eodie_process.py --dir S2files/dir --shp name/of/shapefile --out ./results --id PlotID --statistics_out --index ndvi`` this results in a number of single csv files, one for each tile and date

3. (optional) Use any of the combine_X.py scripts in postprocesses to combine the csv files
4. (optional) Plot timeseries with plot_timeseries.py in postprocesses.

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

1. Same as Case 1
2. Call EODIE: ``python eodie_process.py --dir S2files/dir --shp name/of/shapefile --out ./results --id PlotID --array_out --index ndvi`` this results in a number of single pickle files, one for each tile and date with all ids 
3. (optional) Use arrayplot.py in postprocesses to show/save timeseries plots from wished ids.

Case 3: As Case 1 but processing done on HPC environment with SLURM
------------------------------------------------------------------------------------------------------------

| Available on supercomputer:

- Sentinel-2 data for years 2017-2020 of whole country
- fieldparcel polygons of area x as ESRI shapefile, with unique ID fieldname 'PlotID'

| Additional input:

- timeframe: April 1st - August 31st year 2018 

| Desired output:

- csv file with NDVI timeseries for each fieldparcel polygon

| Workflow:

1. Same as Case 1
2. Create a batch job script (example below is for CSCs Puhti supercomputer) with your data

.. code-block:: bash

    #!/bin/bash -l
    #SBATCH --job-name=   # Give the job a name
    #SBATCH --account=project_  # The project number on which the resources will be spent
    #SBATCH --output=/path/to/job/output/array_job_out_%A_%a.txt # Path to where the output text files will be saved
    #SBATCH --error=/path/to/job/output/array_job_err_%A_%a.txt # Path to where the error text files will be saved
    #SBATCH --time=00:15:00 # Estimation of the time it takes to process one file
    #SBATCH --ntasks=1 # The number of cores per one task
    #SBATCH --partition=small # The estimated processing power needed limitations (more partitions can be found in https://docs.csc.fi/computing/running/batch-job-partitions/)
    #SBATCH --mem-per-cpu=5000 # Estimation of how much memory is needed per cpu
    #SBATCH --array=1-n # Change n to the number of files you have (how many jobs will be created), eg 'wc -l all_filenames.txt'

    module load geoconda # Loads the needed module for processing

    path=/path/to/temporary/directory # Path to a temporary directory which is needed for the jobs (make a array_temp directory for example)

    name=$(sed -n ${SLURM_ARRAY_TASK_ID}p /path/to/a_textfile_with_all_safe_names/xxxx/all_filenames.txt) # This gives every array job its individual filename
    # All the safefiles should be in one directory, one can create a text file for example with command 'ls path/to/safes/ > all_filenames.txt
    # The txt file should have every SAFE file name on individual row. The name variable should now have one filename (each array has their own name variable)

    local_dir="job_${SLURM_ARRAY_TASK_ID}" # This creates a name of a temporary directory named job_6 for example. This is needed because EODIE needs to process the shapefile
    # and doing multiple processes on the same shapefile will produce an error. 

    mkdir $path/$local_dir # creates the local directory which was described in previous line

    cp -r /path/to/the/original/shapefiles $path/$local_dir # Copies the shapefile to every temporary local directory

    cd /path/to/the/program/EODIE/src/eodie # Needs to be in the EODIE directory to work properly

    # The actual processing:
    python eodie_process.py --file $name --shp name/of/shapefile --out ./results --id PlotID --statistics_out --index ndvi
    # More specific arguments and their purpose can be found in EODIE documentation:  https://eodie.readthedocs.io/en/latest/
    rm -r $path/$local_dir # Removes the temporary directory which is not needed anymore

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
            bucket="$basebucket-$year-$tile"
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

    python eodie_process.py --dir $path/$local_dir/SAFE --shp $path/$local_dir/shp/name_of_shapefile --out ./results --id PlotID --statistics_out --index ndvi

    rm -r $path/$local_dir

3. call ``bash run_smart_processing.sh``
