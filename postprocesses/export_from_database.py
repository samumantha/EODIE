import sqlite3
import pandas as pd 
import argparse
import os

''' 
Script for exporting csv-files from .db file created as EODIE output. Script will write a csv file from user-defined index tables of database.
'''

# Create argument parser
parser = argparse.ArgumentParser()

# Add arguments
parser.add_argument("--database", dest = "dbfile", required = True, help = "Full path to .db file that contains the EODIE results.")
parser.add_argument("--index", dest = "index", default = None, nargs = "*", help = "Indices to be extracted from database. Defaults to None and exports all.")
parser.add_argument("--out", dest = "output", default = None, help = "Path to directory where csv files should be exported to. Defaults to same directory as database file.")

# Parse arguments

args = parser.parse_args()

# Build the output path
if args.output is None:
    args.output = os.path.split(args.dbfile)[0]

# Create connection to the database file
connection = sqlite3.connect(args.dbfile)
cursor = connection.cursor()

# List all tables of the database
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()

# Create a list for tables, loop through table tuples and add them to the list
tablelist = []
for table in tables:
    tablelist.append("".join(table))

# If no indices were given as input, loop through all
if args.index is None:
    args.index = tablelist

# Loop through user-defined indices
for index in args.index:

    # Check if the table for given index exists
    if index not in tablelist:
        print("Table {} not found in database, please check your input".format(index))
        next
    # If table is found, read it into a pandas dataframe 
    else:    
        print("Table {} exists, writing to csv...".format(index))
        df = pd.read_sql_query("SELECT * FROM {}".format(index), connection)
        # Build outputpath with index name and user-defined output
        outputpath = os.path.join(args.output, "{}.csv".format(index))
        # Write dataframe to csv
        df.to_csv(path_or_buf = outputpath, index = False)
        # Print a status update
        print("Data is now in {}".format(outputpath))
