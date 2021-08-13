*****
Documentation for plot_timeseries.py
*****
Purpose
-------

The plot_timeseries.py code is meant to plot the time series of the EODIE statistics output. These are usually small csv files which contain the
information of multiple ids and statistics.  
The user input decides what the figure is going to look like

Inputs, functional
------------------

* '--dir' argument is used to give the data to be read and plotted as a path. The path can  be either to a directory with small csv files that EODIE outputs,
one combined statistics csv file made with other EODIE postprocess or a directory where these big combined csv files are. If directory of
combined statistics files are given, make sure that the directory has the word 'combined' in it, otherwise the code will not undestand the input.
Required argument

* '--out' argument takes in the path you want the figures to be saved. Required argument

* '--id' argument takes in one or multiple id that are wanted to be plotted. If no id is given, the code will create a time series of every id the data
contains. Optional

* '--index' takes in the vegetation index or indices that are wanted to be plotted. Required argument
 
* '--start' and '--end' can be given to limit the time interval of the figure. If no argument given, will plot all available data. Optional

* '--format' argument can specify the format of the outputted figure. The default is png but can also be eps, svg, pdf or ps. Optional

 
inputs, figure creation
-----------------------
These inputs return True just by writing them, otherwise turned off. All arguments are optional but if no arguments given, will return empty figures

* '--seePoints' will plot the data points and also a line between the points.  

* '--seeSmoothing' will show a smoothened curve created with Lowess (locally-weighted least squares) smoothing technique. The smoothing uses 
smooth_fraction of 0.15 but can be changed in the code if needed.

* '--seeInterval' will show a prediction interval created from the previous datapoints. This interval is used to detect anomalies.

* '--detectOutliers' will detect points that are outside the prediction interval and mark them with red x mark. This will also exclude from the smoothing calculation
and the lineplot created by '--seePoints'. 

* '--seeError' can be called if 'count' is one of the statistics EODIE outputs. This argument creates errorbars in the datapoints based by standard error and 95% confidence.

* '--pixelLimit' can be called if 'count' is one of the statistics EODIE outputs. With this argument, points (measurements) with small sample size will be marked with red dots. 
Assumes that the biggest found sample size (count) is the size of the id. Based on that, calculates which points have some percentage less than that.
Takes in the allowed limit in percentages. (30% or less marked --> '--pixelLimit 30')










