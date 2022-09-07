import sqlite3
import pandas as pd
import argparse
import os
import csv
from datetime import datetime

""" 
Script for exporting csv-files from .db file created as EODIE output. Script will filter the database based on user inputs and write a csv of the filtered features. 

Author: Arttu Kivimäki (FGI), Summer 2022

Usage: python export_from_database.py --help 
"""

# Create argument parser
parser = argparse.ArgumentParser()

# Add arguments
parser.add_argument(
    "--database",
    dest="dbfile",
    required=True,
    help="Full path to .db file that contains the EODIE results.",
)
parser.add_argument(
    "--index",
    dest="index",
    default=None,
    nargs="*",
    help="Indices to be extracted from database. Defaults to None and exports all.",
)
parser.add_argument(
    "--out",
    dest="output",
    default=None,
    help="Path to directory where csv files should be exported to. Defaults to same directory as database file.",
)

parser.add_argument(
    "--filter",
    dest = "filter",
    action = "store_true",
    help = "Flag to indicate if the users wants to filter the database content to be written as csv. Defaults to False."
)

parser.add_argument(
    "--ids",
    dest = "ids",
    default = None,
    nargs = "*",
    help = "Feature IDs to be exported. Defaults to all IDs."
)

parser.add_argument(
    "--tiles",
    dest = "tiles",
    default = None,
    nargs = "*",
    help = "Results from given tiles only will be exported. Defaults to all tiles found in table."
)

parser.add_argument(
    "--mincount",
    dest = "mincount",
    default = -99999, 
    help = "Minimal number of valid pixels in feature results to be exported. Defaults to -99999."
)

parser.add_argument(
    "--orbits",
    dest = "orbits",
    default = None,
    nargs = "*",
    help = "Results from given orbits only will be exported. Defaults to all orbits found in table."
)

parser.add_argument(
    "--startdate",
    dest = "startdate",
    default = "20160101",
    help = "Results from this day or later only will be exported. Defaults to 20160101. Format is YYYYMMDD."
)

parser.add_argument(
    "--enddate",
    dest = "enddate",
    default = datetime.now().strftime("%Y%m%d"),
    help = "Results from this day or before only will be exported. Defaults to the current date. Format is YYYYMMDD."
)



# Parse arguments
args = parser.parse_args()

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

# Build the output path
if args.output is None:
    args.output = os.path.split(args.dbfile)[0]

# Define functions for handling the inputs.
def ID_empty(input_ID, table):
    """ Checks if input IDs were given and formats them. If not given, use all IDs found in table.
    
    Parameters:
    -----------
    input_ID: list/None
        list of IDs given by user (or None if no IDs were given)
    table: string
        Name of table from which to fetch IDs from in case no IDs were given

    Returns:
    --------
    id_list: list
        list of IDs, either given by user or that were found from table
    """
    if input_ID is None:
        print("No IDs were given, listing all IDs in table...")
        # Select unique IDs from table.
        all_id_query = """SELECT DISTINCT id FROM {}""".format(table) 
        cursor.execute(all_id_query)
        ids = cursor.fetchall()
        return [item for id in ids for item in id]
    else:
        print("IDs were given, reformatting...")
        id_list = [int(el) for el in input_ID] 
        id_list.append(-9999999) 
        return id_list

def tile_empty(tiles, table):
    """ Checks if input tiles were given and formats them. If not given, uses all tiles found in table.

    Parameters:
    -----------
    tiles: list/None
        list of tiles given by user or None if no tiles were given
    table: string
        Name of table from which to fetch tiles from in case no tiles were given
    
    Returns:
    tile_list: list
        list of tiles, either given by user or that were found from table
    """
    if tiles is None:
        print("No tiles were given, listing all tiles in table...")
        all_tile_query = """SELECT DISTINCT Tile FROM {}""".format(table)
        cursor.execute(all_tile_query)
        tiles = cursor.fetchall()
        return [item for t in tiles for item in t]
    else:
        print("Tiles were given, reformatting...")
        tile_list = [tile for tile in tiles]
        tile_list.append(-9999999)
        return tile_list

def orbit_empty(orbits, table):
    """ Checks if input orbits were given and formats them. If not given, uses all orbits found in table.

    Parameters:
    -----------
    orbits: list/None
        list of orbits given by user or None if no orbits were given
    table: string
        Name of table from which to fetchs orbits in case no orbits were given

    Returns:
    --------
    orbit_list: list
        list of orbits, either given by user or that were found from table
    """
    if orbits is None:
        print("No orbits were given, listing all orbits in table...")
        all_orbit_query = """SELECT DISTINCT orbit FROM {}""".format(table)
        cursor.execute(all_orbit_query)
        orbits = cursor.fetchall()
        return [item for t in orbits for item in t]
    else:
        print("Orbits were given, reformatting...")
        orbit_list = [int(orbit) for orbit in orbits]
        orbit_list.append(-9999999)
        return orbit_list

# Loop through user-defined indices
for index in args.index:

    # Check if the table for given index exists
    if index not in tablelist:
        print("Table {} not found in database, please check your input".format(index))
        next
    # If table is found, read it into a pandas dataframe
    else:
        if not args.filter:   
            print("Table {} exists, writing to csv...".format(index))     
            # Read all data from index table to a pandas dataframe ordered by ID and Date
            df = pd.read_sql_query("""SELECT * FROM {} ORDER BY id, date""".format(index), connection)
            # Build outputpath with index name and user-defined output
            outputpath = os.path.join(args.output, "{}.csv".format(index))
            # Write dataframe to csv
            df.to_csv(path_or_buf=outputpath, index=False)
            # Print a status update
            print("Data is now in {}".format(outputpath))
        else:
            print("Table {} exists, applying filters from user...".format(index))
           
            # Format IDs
            main_input_ID = tuple(ID_empty(args.ids, index)) 
            # Format tiles
            tiles = tuple(tile_empty(args.tiles, index))           
            # Format orbits              
            orbits = tuple(orbit_empty(args.orbits, index))
            # Build SQL query
            query = """SELECT * FROM {} WHERE ID = id AND ID IN {} AND Tile IN {} AND orbit IN {} AND count >= ? AND Date >= ? and Date <= ? ORDER BY ID, DATE""".format(index, main_input_ID, tiles, orbits) 
            # Execute SQL query         
            print("Executing SQL query...")  
            cursor.execute(query, (args.mincount, args.startdate, args.enddate))
            # Fetch column names
            colnames = [description[0] for description in cursor.description]
            # Fetch rows
            rows = cursor.fetchall()
            # Build outputpath for file
            outputpath = os.path.join(args.output, "{}_filtered.csv".format(index))
            print("Writing results into a csv...")
            # Write csv file
            with open(outputpath, mode = "w") as csv_file:
                csv_writer = csv.writer(csv_file, delimiter=",")
                csv_writer.writerow(colnames)
                for row in rows:
                    csv_writer.writerow(row)         
            
# Close connection to the database
connection.close()

print("All requested data exported from database.")