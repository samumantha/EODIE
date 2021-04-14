#!/bin/bash -l
#SBATCH --job-name=peltopiste
#SBATCH --account=project_2001106
#SBATCH --partition=small
#SBATCH --time=03-00:00:00
#SBATCH --ntasks=1
#SBATCH --mem-per-cpu=12G
#SBATCH --array=1-50

small_polygon_shapefile=
large_polygon_shapefile= 
results_directory=
tilenumber=${SLURM_ARRAY_TASK_ID}

module load geoconda

python splitshp_hpc.py $small_polygon_shapefile $large_polygon_shapefile $results_directory $tilenumber



