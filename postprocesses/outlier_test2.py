
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


from sklearn.ensemble import IsolationForest
import numpy as np

#parser = argparse.ArgumentParser(prog="myprogram",description="foo")
parser = argparse.ArgumentParser()

#parser.add_argument('-f' , dest="f",help="for jupiter notebook testing, error wanted this inserted")
parser.add_argument('--dir', dest= 'directory' , default="/home/jvarho/EODIE/testCSVs/combined_statistics",help = 'Write the directory path where the csv files are as absolute path')
parser.add_argument('--out',dest= 'output_directory',default="/home/jvarho/EODIE/testTimeseries",help= 'Write the directory path where you want the files to be outputted')
parser.add_argument('--id', dest='ID', default="1,63,52,72,3" ,help="Write a list of id's separated by a comma")
parser.add_argument('--index', dest= 'index', default="ndvi,kndvi,rvi,savi" ,help='write a list of indices you want to be plotted separated by a comma')
#parser.add_argument('--stat', dest='statistics', default='mean,std', help='Write the statistics you want to be plotted in the same plot')
parser.add_argument('--start', dest='startDate',default="",help='Specify the starting date in format YYYYMMDD. If left empy, will plot all dates available')
parser.add_argument('--end', dest='endDate',default="", help='Specify the ending date in format YYYYMMDD. If left empty, will plot all dates available')
parser.add_argument('--format',dest='fileFormat',default='png', help="write the wanted format of timeseries, can be: 'png','eps','pdf','ps','svg'")
parser.add_argument('--interpStyle',dest='interpolationStyle',default='line',help='You can specify the wanted style of interpolation. For example: "quadratic","cubic" or "from_derivatives". More methods can be found in pandas interpolate methods documentation')
parser.add_argument('--seePoints',dest="seeDatapoints",default=1,type=int, help="The time series can either show or not show the data points, 1 for show, 0 for hide")
parser.add_argument('--outlierDetection',dest='detectOutliers',default=1, type=int, help="By creating a prediction interval, anomalies can be detected outside of it. 1 for show, 0 for hide")
parser.add_argument("--seeInterval", dest="seeInterval", default=1,type=int ,help="Visualise the prediction interval which is used for the outlier detection. 1 for show, 0 for hide")
parser.add_argument('--seeSmoothened', dest="seeSmoothened", default=1, type=int, help="See a smoothened curve made of the data points. Uses Lowess smoothening. 1 for show, 0 for hide")
input=parser.parse_args()



directory=input.directory
output=input.output_directory
ID_list= list(map(int,input.ID.split(',')))
indices_list=input.index.split(',')
#statistic_list=input.statistics
startDate=input.startDate
endDate=input.endDate
format=input.fileFormat
seeDatapoints=input.seeDatapoints
detectOutliers=input.detectOutliers
seeSmoothing=input.seeSmoothened
seeInterval=input.seeInterval

# Data collection: 
mainDataFrame=pd.DataFrame()

if '.csv' in directory and os.path.isfile(directory) and 'combined_' in directory.split('/')[-1]: #If input is one combined statistics file
    mainDataFrame=pd.read_csv(directory).query("id in @ID_list")#) and "#+stat+"!= 'None'")
    mainDataFrame['Index']=directory.split('/')[-1].split('_')[1].split('.')[0]
    mainDataFrame['Dates']=pd.to_datetime(mainDataFrame['Dates'],format='%Y%m%d')

elif os.path.isdir(directory) and 'combined' in directory.split('/')[-1]: # Else if 'directory' is a directory of combined csv files
    for entry in os.scandir(directory): #For every file in the directory
        if entry.name.endswith('.csv') and entry.is_file:# and indices_list.__contains__(entry.name.split("_")[-1]):
            temp_df=pd.read_csv(entry).query("id in @ID_list")#) and "#+stat+"!= 'None'")
            temp_df['Index']=entry.name.split("_")[1].split('.')[0]
            temp_df['Dates']=pd.to_datetime(temp_df['Dates'],format="%Y%m%d")
            if len(mainDataFrame)==0:
                mainDataFrame=temp_df
            else:
                mainDataFrame=pd.concat([mainDataFrame,temp_df],axis=0)

else: 
    for entry in os.scandir(directory): #checks every file in the directory given as input
        if(entry.name.endswith('.csv') and entry.is_file and indices_list.__contains__(entry.name.split('_')[0])):  #Makes sure the file to be read is .csv file, is the correct index and is a file to begin with
            fileParser=entry.name.split('_') #Parses the name of the file in segments (index_date_tile_stat.csv)
            VI=fileParser[0]
            date=fileParser[1] #Resulting files from eodie follow this naming convention
            filedate=datetime.strptime(date,"%Y%m%d") #Converts string 'yyyymmdd' to form datetime
            temp_df=pd.read_csv(entry).query("id in @ID_list")# and mean!= 'None'"
            temp_df['Dates']=filedate # Change to filedate if datetime object wanted, adds it to df column
            temp_df['Index']=VI # Adds index to df column

            if len(mainDataFrame)==0: #can't concat with empty dataframe so variable is given to temporary dataframe
                mainDataFrame=temp_df
            else: #So this adds the data to the main dataframe
                mainDataFrame=pd.concat([mainDataFrame,temp_df],axis=0)

if bool(startDate): #Boolean of a string returns true if string is not empty
    startdate=datetime.strptime(startDate,"%Y%m%d")
    mainDataFrame.query("Dates>=@startdate",inplace=True) # Filters out dates that are before the starting perioud

if bool(endDate):
    enddate=datetime.strptime(endDate,"%Y%m%d")
    mainDataFrame.query("Dates<=@enddate",inplace=True) 

stat='mean'
wanted_data=['Dates',stat]

print(mainDataFrame.to_string())

# Plotting:
for id in ID_list:
    for index in indices_list:
        plot_df=mainDataFrame.query("id==@id and Index==@index and mean!='None'").set_index('Dates').sort_index()

        if len(plot_df)<3:#with sample sizes less than this, tsmoothie breaks. (and time series is quite useless)
            continue      # df's of size 1 produce and error in the smoothing

        plot_df['mean']=plot_df['mean'].astype(float)
        
        #operate smoothing
        smoother=LowessSmoother(smooth_fraction=0.2,iterations=1)
        smoother.smooth(plot_df['mean']) #Inputs the original data to tsmoothie
        
  
        #generate intervals
        low, up = smoother.get_intervals('prediction_interval') #Interval can be changed to something else
       
        plot_df['lower']=low.reshape(-1,1)
        plot_df['upper']=up.reshape(-1,1) 
        
        invalid_points=plot_df.query("mean>=upper or mean<=lower")['mean'] #Saves the detected anomalies
        print(plot_df)

        plt.figure()


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
     
        plt.legend()
        plt.xlim(plot_df.index[0],plot_df.index[-1]) #smallest date is first and biggest is last
        plt.title(str(index)+ " time series of id "+ str(id)  )
        plt.ylim(top=1)
        plt.grid(True)
        plt.ylabel(str(index)+", " + str(stat))

        plt.show() # Remove in the final version, add savefig instead
        #plt.savefig(os.path.join(output,"Timeseries_of_id_"+str(id)+'_'+index+'.' +format),format=format) # Uncomment in final version
    

#Now works for mean values. Try to change it so it works for any statistic

# Error: SVD did not converge; invalid value encountered in true divide.   Comes up if sample size is only 1 

# Possible problem: Collects the data with different methods based on the name of the --dir input, so if input follows
# some other naming convention then it probably will produce an error

# tsmoothie breaks if dataframe is too small. Work for big datasets but at least those under length 2 will crash
