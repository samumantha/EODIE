
safedir=$1

# list all safedirs in txt
ls $safedir > safefiles.txt

#count SAFE files in dir
count=$(wc -l < safefiles.txt)

##run EODIE array job
echo "starting Puhti Array job"

echo sbatch --array=1-$count sbatch.sh