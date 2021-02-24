
dir=$1
#dir=/u/58/wittkes3/unix/Desktop/eodie_example

python splitshp_world.py ...

python splitshp_mp.py $dir/example_parcels.shp $dir/Fin_s2.shp $dir/shp

python process.py --dir $dir/S2 --shp $dir/shp/example_parcels --out $dir/results --id PlotID
