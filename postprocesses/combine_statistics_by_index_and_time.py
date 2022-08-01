import argparse
import os
import csv


parser = argparse.ArgumentParser()
parser.add_argument(
    "--dir",
    dest="directory",
    help="Write the directory path where the csv files are as absolute path",
)
parser.add_argument(
    "--out",
    dest="output_directory",
    default=".",
    help="Write the directory path where you want the files to be outputted",
)
input = parser.parse_args()
# Takes the directory where the csv files are stored as an input

directory = input.directory
outputDir = input.output_directory

if directory is None or len(directory) == 0:  # Checks if argument is given
    print("please enter the directory path as argument starting with '--dir'")
    quit()


# Creates own directory for the results to be in (Not sure if wanted, might delete)
if not os.path.exists(outputDir + "/combined_statistics"):
    os.mkdir(outputDir + "/combined_statistics")


def k(a, b):  # Function to give multiple keys to sorted
    def _k(item):
        return (item[a], int(item[b]))

    return _k  # Return the list of numbers as items that can be given to sorted key


# Creates a list of all indices that are in the directory
indexlist = []
datelist = []
for entry in os.scandir(directory):
    if not indexlist.__contains__(entry.name.split("_")[0]) and entry.name.endswith(
        ".csv"
    ):
        indexlist.append(entry.name.split("_")[0])
    if entry.name.endswith(".csv") and not datelist.__contains__(
        entry.name.split("_")[1]
    ):
        datelist.append(entry.name.split("_")[1])

# The name of the file always has index in first place (hence [0])
# and the date in [1]


if len(indexlist) == 0:  # Checks if there were any files to be found in the directory
    print("No correct csv files found in this directory")
    quit()


for index in indexlist:  # Creates a new file for every index
    for date in datelist:  # New file for every date
        filename = (
            outputDir + "/combined_statistics/combined_" + index + "_" + date + ".csv"
        )  # directory and name of the new file
        with open(
            filename, "w", newline=""
        ) as newfile:  # Makes new file for every index
            writer = csv.writer(newfile)
            entrycount = 0
            for entry in os.scandir(
                directory
            ):  # checks every file in the directory given as input
                if (
                    entry.path.endswith(".csv")
                    and entry.is_file
                    and entry.name.split("_")[0] == index
                ):
                    # Makes sure the file to be read is .csv file, is the correct index and is a file to begin with
                    fileParser = entry.name.split(
                        "_"
                    )  # Parses the name of the file in segments (index_date_tile_stat.csv)
                    # VI=fileParser[0]
                    # date=fileParser[1] #Resulting files from eodie follow this naming convention
                    tile = fileParser[2]
                    rowcount = 0

                    with open(entry, newline="") as file:
                        reader = csv.reader(file, delimiter=",")
                        # The if-statements make sure that the titles are only printed once, per file
                        for row in reader:
                            if rowcount != 0 and entrycount != 0:
                                writer.writerow([tile] + row)
                            elif entrycount == 0:  # First row of first file
                                writer.writerow(["Tiles"] + row)
                                entrycount = 1
                                rowcount = 1
                            elif entrycount != 0 and rowcount == 0:
                                rowcount = 1
            file.close()
        newfile.close()

        # The following segment sorts the file created in previous step
        readingFile = open(filename, "r")
        reader = csv.reader(readingFile, delimiter=",")
        titles = next(reader)  # remembers the titles and makes sure they aren't sorted
        sortedFile = sorted(reader, key=k(0, 1))
        with open(filename, "w", newline="") as sorting:
            writer = csv.writer(sorting)
            writer.writerow(titles)
            writer.writerows(sortedFile)
        readingFile.close()
        sorting.close()

print(
    "The files can now be found in a directory called 'combined_statistics' in directory "
    + outputDir
)
