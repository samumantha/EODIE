import os
import argparse
from matplotlib import lines
from matplotlib.pyplot import grid, legend, plot, title
from numpy import  empty, where

import pandas as pd
from datetime import datetime
import matplotlib.pylab as plt
from scipy.sparse import data
from tsmoothie.smoother import LowessSmoother
import numpy as np

parser = argparse.ArgumentParser()

parser.add_argument('--dir', dest= 'directory' ,help = 'Write the directory path where the csv files are as absolute path')
parser.add_argument('--out',dest= 'output_directory',help= 'Write the directory path where you want the files to be outputted')
parser.add_argument('--id', dest='ID', default=[],type=int,help="Write a list of id's separated by a space", nargs='*')
parser.add_argument('--index', dest= 'index', default=['kndvi','ndvi'] ,help='write a list of indices you want to be plotted separated by a space', nargs='*')
parser.add_argument('--start', dest='startDate',default="",help='Specify the starting date in format YYYYMMDD. If left empy, will plot all dates available')
parser.add_argument('--end', dest='endDate',default="", help='Specify the ending date in format YYYYMMDD. If left empty, will plot all dates available')
parser.add_argument('--format',dest='fileFormat',default='png', help="write the wanted format of timeseries, can be: 'png','eps','pdf','ps','svg'")
parser.add_argument('--seePoints',dest="seeDatapoints",action='store_true', help="The time series can either show or not show the data points, if this argument give, will show points")
parser.add_argument('--detectOutliers',dest='detectOutliers',action='store_true', help="By creating a prediction interval, anomalies can be detected outside of it. ")
parser.add_argument("--seeInterval", dest="seeInterval", action='store_true' ,help="Visualise the prediction interval which is used for the outlier detection.")
parser.add_argument('--seeSmoothened', dest="seeSmoothened", action='store_true', help="See a smoothened curve made of the data points. Uses Lowess smoothening.")
parser.add_argument("--seeError", dest="standardError",action='store_true', help="You can see the standard error of each individual point. (Requires 'count' as statistic)")
parser.add_argument("--seeGrid", dest="grid", action='store_true', help="The plot will contain a grid if  this argument is given" )
parser.add_argument("--pixelLimit", dest="pixellimit", default=0, type=int, help="Type in percentages if you want datapoints with small sample size marked (compared to original), (requires 'count' as statistic)")
input=parser.parse_args()



directory = input.directory
output = input.output_directory
ID_list = input.ID
indices_list = input.index
startDate = input.startDate
endDate = input.endDate
fileformat = input.fileFormat
seeDatapoints = input.seeDatapoints
detectOutliers = input.detectOutliers
seeSmoothing = input.seeSmoothened
seeInterval = input.seeInterval
standardError = input.standardError
pixelLimit = input.pixellimit
seeGrid = input.grid

# Data collection functions: 
def data_collection1(path): # directory full of small csv files
    """ 
    Collects the data from a directory full of small csv files to a big dataframe by reading csv and concatenating to main dataframe.

    Parameters
    ----------
    path : string 
            contains the path to the datafiles 

    Returns
    -------
    dataframe 
            The read csv files are collected to this big dataframe from which they can be plotted.
    """
    df = pd.DataFrame()
    for entry in os.scandir(path): # Checks every file in the directry
        if (entry.name.endswith('.csv')) and entry.is_file and indices_list.__contains__(entry.name.split('_')[0]):
            nameparser = entry.name.split('_') # Parses the info written in the name
            VI = nameparser[0]
            date = datetime.strptime(nameparser[1],"%Y%m%d") 
            temp_df = pd.read_csv(entry) 
            temp_df['Dates'] = date
            temp_df['Index'] = VI
            
            if len(df)==0: #can't concat with empty dataframe so variable is given to temporary dataframe
                df = temp_df
            else: #So this adds the data to the main dataframe
                df = pd.concat([df,temp_df],axis=0)
    return df


def data_collection2(path): # One big combined csv file ./path/to/combined_INDEX.csv
    """ 
    Collects the data from big combined statistics csv file to a big dataframe.

    Parameters
    ----------
    path : string 
            contains the path to the datafiles 

    Returns
    -------
    dataframe 
            The read csv files are collected to this big dataframe from which they can be plotted.
    """
    df = pd.read_csv(path)
    df['Index'] = path.split('_')[-1].split('.')[0]
    df['Dates'] = pd.to_datetime(df['Dates'], format="%Y%m%d")
    return df



def data_collection3(path): # Directory full of big combined csv files
    """ 
    Collects the data from a directory full of combined statistics csv files to a big dataframe by reading csv's and concatenating to main dataframe.


    Parameters
    ----------
    path : string 
            contains the path to the datafiles, required '/' at the end of path

    Returns
    -------
    dataframe 
            The read csv files are collected to this big dataframe from which they can be plotted.
    """
    df = pd.DataFrame()
    for entry in os.scandir(path):
        if entry.name.endswith('.csv') and entry.is_file:
            temp_df = pd.read_csv(entry)
            temp_df['Index'] = entry.name.split("_")[1].split('.')[0] # Assumes naming is for example 'combined_kndvi.csv' to work
            temp_df['Dates'] = pd.to_datetime(temp_df['Dates'], format="%Y%m%d")

            if len(df) == 0:
                df = temp_df
            else:
                df = pd.concat([df,temp_df],axis=0)      
    return df


# Data collection: 


if os.path.isfile(directory):
    try: 
        mainDataFrame = data_collection2(directory)
    except: 
        print("Data collection not possible from " + directory)
        quit()

elif os.path.isdir(directory):
    name = directory.split('/')[-2]
    try: 
        if name.__contains__("combined"):
            mainDataFrame = data_collection3(directory) # Directory to big combined csv files
        else:
            mainDataFrame = data_collection1(directory) # small csv files
    except: 
        print("Data collection was not possible, try rechecking naming convention")
        quit()


if len(ID_list) != 0:
    mainDataFrame = mainDataFrame.query("id in @ID_list")
else: 
    ID_list = mainDataFrame['id'].unique()


if bool(startDate): #Boolean of a string returns true if string is not empty
    startdate=datetime.strptime(startDate,"%Y%m%d")
    mainDataFrame.query("Dates>=@startdate",inplace=True) # Filters out dates that are before the starting period

if bool(endDate):
    enddate=datetime.strptime(endDate,"%Y%m%d")
    mainDataFrame.query("Dates<=@enddate",inplace=True) 

stat='mean' # Now only works for mean but code can be changed to work on other statistics as well


maxPixels = {}

# Plotting:
for id in ID_list:

    try:
        maxPixels[id] = mainDataFrame.query("id==@id")['count'].max() # The maximum pixel size is saved to dictionary
    except:
        pass # if 'count' doesn't exist --> error --> this ignores it

    for index in indices_list:
        plot_df=mainDataFrame.query("id==@id and Index==@index and mean!='None'").set_index('Dates').sort_index()
        if len(plot_df)<3:#with sample sizes less than this, tsmoothie breaks. (and time series is quite useless)
            print(f"Unable to plot {index} of id {id} because data set is too small")
            continue      # df's of size 1 produce and error in the smoothing

        plot_df['mean']=plot_df['mean'].astype(float)
        
        plot_df = plot_df.dropna()

        #operate smoothing
        smoother=LowessSmoother(smooth_fraction=0.15,iterations=1)
        smoother.smooth(plot_df['mean']) #Inputs the original data to tsmoothie
         
        #generate intervals
        low, up = smoother.get_intervals('prediction_interval') #Interval can be changed to something else
        
        plot_df['lower']=low.reshape(-1,1)
        plot_df['upper']=up.reshape(-1,1) 
        
        invalid_points=plot_df.query("mean>=upper or mean<=lower")['mean'] #Saves the detected anomalies

        plt.figure()

        # Figure construction

        if seeInterval: #If userinput is 1, shows the interval
            plt.fill_between(plot_df.index,plot_df['lower'],plot_df['upper'], alpha=0.3, label='Prediction interval')
        
        if detectOutliers: #If outliers wanted to be detected, filters them out from the original and plots the invalid points
            plot_df.query("mean>=lower and mean<=upper", inplace=True) #Takes out the outliers
            if plot_df.empty:
                continue
            plot_df['smoothing']=smoother.smooth(plot_df['mean']).smooth_data.reshape(-1,1) #Adds new column of smooth values 
            invalid_points.plot(style='x', markersize=15, color='r',label='outliers')
        else:
            plot_df['smoothing']=smoother.smooth_data.reshape(-1,1) 
            #If outliers are to be ignored, adds the original smoothened curve to the dataframe


        if seeSmoothing:    
            plt.plot(plot_df['smoothing'],linewidth=3.5,label='Smoothened data')

        if seeDatapoints: 
            plt.plot(plot_df['mean'],'k.-', label='data points',linewidth=1)

        if pixelLimit:
            try:
                plt.plot(plot_df.query("count/@maxPixels[@id]*100 <= @pixelLimit")['mean'], 'ro', markersize=6, label=f'small sample size (less than {pixelLimit}%)' )
            # marks points with small samplesize as red 
            except:
                pass

        if standardError: #Integer value will be interpreted as boolean
            try:
                plot_df['std']=plot_df['std'].astype(float)
                plot_df['SE']= plot_df['std']/((plot_df['count'])**(1/2))  # the formula for standard deviation
                z=1.96 #for 95% interval
                plt.errorbar(x=plot_df.index ,fmt='.k', ecolor='r', y= plot_df["mean"], yerr= z*plot_df["SE"],linewidth=2)
            except:
                print("An error occured in trying to calculate error. Make sure the files you inputted have 'count' statistic in them")

      
        plt.legend()
        plt.xlim(plot_df.index[0],plot_df.index[-1]) #smallest date is first and biggest is last
        plt.title(str(index)+ " time series of id "+ str(id)  )
        plt.ylim(top=1)
        if seeGrid:
            plt.grid(True)
        plt.ylabel(str(index)+", " + str(stat))
        plt.xticks(rotation=45)
        plt.tight_layout()
        #plt.show() # Remove in the final version, add savefig instead
        plt.savefig(os.path.join(output,"Timeseries_of_id_"+str(id)+'_'+index+'.' +fileformat),format=fileformat) # Uncomment in final version
    

# Now works for mean values only. 
# Error: SVD did not converge; invalid value encountered in true divide.   Comes up if sample size is only 1 

# Possible problem: Collects the data with different methods based on the name of the --dir input, so if input follows
# some other naming convention then it probably will produce an error

# tsmoothie breaks if dataframe is too small. Work for big datasets but at least those under length 2 will crash