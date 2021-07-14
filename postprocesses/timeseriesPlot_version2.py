import os
import argparse
from matplotlib.pyplot import grid, plot, title
from numpy import empty
import pandas as pd
from datetime import datetime
import matplotlib.pylab as plt


parser = argparse.ArgumentParser()
parser.add_argument('--dir', dest= 'directory' , help = 'Write the directory path where the csv files are as absolute path')
parser.add_argument('--out',dest= 'output_directory',default='.',help= 'Write the directory path where you want the files to be outputted')
parser.add_argument('--id', dest='ID', help="Write a list of id's separated by a comma")
parser.add_argument('--index', dest= 'index', help='write a list of indices you want to be plotted separated by a comma')
parser.add_argument('--stat', dest='statistic', default='mean', help="Write the statistic you want to be plotted in the same plot, for example: 'mean','median','std'")
parser.add_argument('--start', dest='startDate',help='Specify the starting date in format YYYYMMDD. If left empy, will plot all dates available')
parser.add_argument('--end', dest='endDate',help='Specify the ending date in format YYYYMMDD. If left empty, will plot all dates available')
parser.add_argument('--fileformat',dest='fileFormat',default='png', help="write the wanted format of timeseries, can be: 'png','eps','pdf','ps','svg'")

input=parser.parse_args()

directory=input.directory
output=input.output_directory
ID_list= list(map(int,input.ID.split(',')))
indices_list=input.index.split(',')
stat=input.statistic
startDate=input.startDate
endDate=input.endDate
format=input.fileFormat

mainDataFrame=pd.DataFrame() #created before and is overwritten later 

if '.csv' in directory and 'combined_' in directory.split('/')[-1]: #If input is one combined statistics file
    mainDataFrame=pd.read_csv(directory).query("id in @ID_list and "+stat+"!= 'None'")
    mainDataFrame['Index']=directory.split('/')[-1].split('_')[1].split('.')[0]
    mainDataFrame['Dates']=pd.to_datetime(mainDataFrame['Dates'],format='%Y%m%d')
    
    
else:
    for entry in os.scandir(directory): #checks every file in the directory given as input
        if(entry.name.endswith('.csv') and entry.is_file and indices_list.__contains__(entry.name.split('_')[0])):  #Makes sure the file to be read is .csv file, is the correct index and is a file to begin with
            nameParser=entry.name.split('_') #Parses the name of the file in segments (index_date_tile_stat.csv)
            VI=nameParser[0]
            date=nameParser[1] #Resulting files from eodie follow this naming convention

            if startDate is not None or endDate is not None: #if the either variable are not empty, then user has given the argument
                if startDate is not None and endDate is not None:
                    if not( int(date)>=int(startDate) and int(endDate)>=int(date)): 
                        #If both arguments are given but the date is not between them --> next iteration 
                        continue #stops this entry and goes to the next one
                elif startDate is not None and endDate is None:
                    if int(date)<=int(startDate):
                        continue #If start date given and not end date and the file date is smaller than starting date --> skip
                elif startDate is None and endDate is not None:
                    if  int(date)>=int(endDate):
                        continue #If only ending date given and the date of the file is bigger --> skip
                
                #This is one solution, is there a better way? 

            filedate=datetime.strptime(date,"%Y%m%d") #Converts string 'yyyymmdd' to form datetime
            temp_df=pd.read_csv(entry).query("id in @ID_list and "+stat+"!= 'None'")
            temp_df['Dates']=filedate
            temp_df['Index']=VI

            if len(mainDataFrame)==0: #can't concat with empty dataframe so variable is given to temporary dataframe
                mainDataFrame=temp_df
            else: #So this adds the data to the main dataframe
                mainDataFrame=pd.concat([mainDataFrame,temp_df],axis=0)

print(mainDataFrame)
#Eli tässä vaiheessa kerää kaikki id:t ja tilastot yhteen isoon dataframeen
#Tämän jälkeen helppo joko tehdä kaikista id:istä oma plot tai sitten for each id

#plot_df=mainDataFrame.pivot(index=['Date'], columns= 'Index', values='mean')#.sort_values('Date',ascending=True).reset_index()
#print(plot_df)

for id in ID_list:
    plot_df=mainDataFrame.query("id==@id").pivot(index=['Dates'],columns='Index',values=stat)
    if len(plot_df)==0:
        continue
    plot_df=plot_df.astype(float)
    #print(plot_df)
    plot_df.plot(marker='h',grid=True,title='Timeseries of id '+str(id)+" "+stat)
    plt.savefig(os.path.join(output,"Timeseries_of_id_"+str(id)+'_'+stat+'.' +format),format=format)
    
# Make separate codes which work for different inputs rather than 1 long. 
# the main script could try to interpret the input and activate call different codes based on the input
# For example for combined stat.csv or combined stat folder or 