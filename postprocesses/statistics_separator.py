import argparse
import os
import csv

# Script is run if different csv files are wanted to be sorted in different folders by their statistics

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
# Takes the directory where the csv files are stored as an input
input = parser.parse_args()
directory = input.directory
outputDest = input.output_directory

if directory is None or len(directory) == 0:  # Checks if argument is given
    print("Please enter the directory path as argument starting with '--dir'")
    quit()


stat_list = []
for entry in os.scandir(directory):
    if entry.name.endswith(".csv") and entry.is_file:
        with open(entry, "r", newline="") as file:
            reader = csv.reader(file, delimiter=",")
            titles = next(reader)  # The first row of csv file
            if not stat_list.__contains__(titles):
                os.mkdir(
                    outputDest + "csvFiles_with_" + "_".join(titles)
                )  # if the directory doesn't exist, it creates one
                stat_list.append(titles)

            command = (
                "cp "
                + entry.path
                + " "
                + outputDest
                + "/csvFiles_with_"
                + "_".join(titles)
            )
            os.system(command)  # Executes the command in the system, copies the file

print(
    "The files should now be copied in separate directories based on their statistics"
)


# Because the combine_statistics scripts currently work only with csv with same statistics, this script
# can be used to separate these different statistics

# Can be its separate script or possibly be connected with the combine_statistics -scripts
