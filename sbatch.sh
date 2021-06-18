#!/bin/bash -l
#SBATCH --job-name=array_job
#SBATCH --account=2001106
#SBATCH --output=array_job_out_%A_%a.txt
#SBATCH --error=array_job_err_%A_%a.txt
#SBATCH --time=00:30:00
#SBATCH --ntasks=1
#SBATCH --mem-per-cpu=12000

module load geoconda

name=$(sed -n ${SLURM_ARRAY_TASK_ID}p safefiles.txt)

python process.py --file $name --shp /scratch/project_200106/EODIE/testfiles/shp/test_parcels_32635 --out /scratch/project_200106/EODIE/results --id ID --stat 1 --index ndvi
