import argparse
import os
import csv


parser = argparse.ArgumentParser()
parser.add_argument('--dir', dest= 'directory' , help = 'Write the directory path where the csv files are as absolute path')
input=parser.parse_args()
#Takes the directory where the csv files are stored as an input

directory=input.directory
#Creates own directory for the results to be in (Not sure if wanted, might delete)
if not os.path.exists('./combined_statistics'):
    os.mkdir('./combined_statistics')


def k(a,b,c): #Function to give multiple keys to sorted
    def _k(item):
        return (item[a],item[b],item[c])
    return _k #Return the list of numbers as items that can be given to sorted key 


#Creates a list of all indices that are in the directory
indexlist=[]
for entry in os.scandir(directory):
        if not indexlist.__contains__(entry.name.split('_')[0]) and entry.name.endswith('.csv'):
            indexlist.append(entry.name.split('_')[0])
#The name of the file always has index in first place (hence [0])

for index in indexlist: #Creates a new file for every index
    filename = './combined_statistics/combined_'+index+'.csv' #directory and name of the new file
    with open(filename,'w', newline='') as newfile: #Makes new file for every index
        writer=csv.writer(newfile)
        entrycount=0
        for entry in os.scandir(directory): #checks every file in the directory given as input
            if(entry.path.endswith('.csv') and entry.is_file and entry.name.split('_')[0]==index): 
                 #Makes sure the file to be read is .csv file, is the correct index and is a file to begin with
                fileParser=entry.name.split('_') #Parses the name of the file in segments (index_date_tile_stat.csv)
                #VI=fileParser[0]
                date=fileParser[1] #Resulting files from eodie follow this naming convention
                tile=fileParser[2]
                rowcount=0

                with open(entry,newline='') as file:
                    reader=csv.reader(file,delimiter=',')
                    #The if-statements make sure that the titles are only printed once, per file
                    for row in reader:
                        if rowcount!=0 and entrycount!=0:
                            writer.writerow([date,tile]+row)
                        elif entrycount==0:  #First row of first file
                            writer.writerow(['Dates','Tiles']+row)
                            entrycount=1
                            rowcount=1
                        elif entrycount!=0 and rowcount==0:
                            rowcount=1
        file.close()
    newfile.close()  

    #The following segment sorts the file created in previous step
    readingFile=open(filename,'r')
    reader=csv.reader(readingFile,delimiter=',')
    titles=next(reader) #remembers the titles and makes sure they aren't sorted
    sortedFile=sorted(reader,key=k(0,1,2))
    with open(filename,'w',newline='') as sorting:
        writer=csv.writer(sorting)
        writer.writerow(titles)
        writer.writerows(sortedFile)
    readingFile.close()
    sorting.close()

print("The files can now be found in a directory called 'combined_statistics'")

#Feature (/Problem): When sorting, the ID is sorted by the first number first (not by value)
#for example [2,12,3,22,415,11] --> [11,12,2,22,3,415] 

