import sqlite3
import pandas as pd
import argparse
import os

""" 
Script for exporting csv-files from .db file created as EODIE output. Script will write a csv file from user-defined index tables of database.
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


#cursor.execute(all_id_query)
#testi = cursor.fetchall()
#print(testi)

def ID_empty(input_ID):
    if(len(input_ID) == 0):
        print("No IDs were given, listing all IDs in table...")
        all_id_query = """SELECT DISTINCT id FROM ndvi"""
        cursor.execute(all_id_query)
        testi = cursor.fetchall()
        return [item for t in testi for item in t]
    else:
        return_list = [int(el) for el in list(input_ID.split(' '))] 
        return_list.append(-9999999) 
        return return_list

def tile_empty(input_tile):
    if len(input_tile) == 0:
        print("No tiles were given, listing all tiles in table...")
        all_tile_query = """SELECT DISTINCT Tile FROM ndvi"""
        cursor.execute(all_tile_query)
        tiles = cursor.fetchall()
        return [item for t in tiles for item in t]
    else:
        return_list = [tile for tile in list(input_tile.split(' '))]
        return_list.append(-9999999)
        return return_list
def orbit_empty(input_orbit):
    if len(input_orbit) == 0:
        print("No orbit was given, listing all orbits in table...")
        all_orbit_query = """SELECT DISTINCT orbit FROM ndvi"""
        cursor.execute(all_orbit_query)
        orbits = cursor.fetchall()
        return [item for t in orbits for item in t]
    else:
        return_list = [orbit for orbit in list(input_orbit.split(' '))]
        return_list.append(-9999999)
        return return_list

def check_count(mincount):
    if len(mincount) == 0:
        return -1
    else:
        return float(mincount)

def check_startdate(startdate):
    if len(startdate) == 0:
        return 20140101
    else:
        return startdate

def check_enddate(enddate):
    if len(enddate) == 0:
        return 20501231
    else:
        return enddate

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
            df = pd.read_sql_query("""SELECT * FROM {}""".format(index), connection)
            # Build outputpath with index name and user-defined output
            outputpath = os.path.join(args.output, "{}.csv".format(index))
            # Write dataframe to csv
            df.to_csv(path_or_buf=outputpath, index=False)
            # Print a status update
            print("Data is now in {}".format(outputpath))
        else:
            print("Table {} exists, requesting filters from user...".format(index))
            #ids = input("Give feature IDs: ")

            ID_main_in = input("IDs of the features: ")
            tiles_input = input("Tiles: ")
            minimum_count = input("Minimum pixels in feature: ")
            startdate = input("Earliest date (YYYYMMDD): ")
            enddate = input("Latest date (YYYYMMDD): ")
            orbit = input("Orbit: ")


            

            main_input_ID = tuple(ID_empty(ID_main_in)) 
            tiles = tuple(tile_empty(tiles_input))             
            orbits = tuple(orbit_empty(orbit))
                                   
            #tiles = input("Give tiles: ")
            #tile_input = (tiles,)
            #print(type(tile_input))
            #quit()
            #print(tile_input)
   
            query = """SELECT * FROM {} WHERE ID = id AND ID IN {} AND Tile IN {} AND orbit in {} AND count >= ? AND Date >= ? and Date <= ? ORDER BY ID""".format(index, main_input_ID, tiles, orbits)            
            mitatamaon = cursor.execute(query, (check_count(minimum_count), check_startdate(startdate), check_enddate(enddate)))
            print(mitatamaon)
            quit()
            rows = cursor.fetchall()
            print(rows)
            #df = pd.read_sql_query("""SELECT * FROM {} WHERE ID = id AND ID IN {} AND tsuiba >= ? ORDER BY ID""".format(index, ids), connection)
            


