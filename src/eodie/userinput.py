"""
Class with all userinput for running eodie as command line tool.

Authors: Samantha Wittke, Juuso Varho, Petteri Lehti

"""

import argparse
import os
from datetime import datetime
import glob
import re
import yaml
import logging
from eodie.validator import Validator


class UserInput(object):
    """Userinput object for EODIE.

    Attributes
    -----------
    see help text for description of each attribute
    """

    def __init__(self):
        """Initialize UserInput object."""
        self.get_userinput()
        self.create_logfile(self.outpath, self.verbose)

    def get_userinput(self):
        """Get all userinput from commandline call to run the tool and stores them as userinput attributes."""
        parser = argparse.ArgumentParser()
        parser.add_argument(
            "--platform",
            dest="platform",
            help="which platform does the data come from? options: s2, tif, ls8",
            choices=["s2", "tif", "ls8"],
            required=True,
        )
        inputrastergroupparser = parser.add_mutually_exclusive_group(required=True)
        inputrastergroupparser.add_argument(
            "--rasterdir", dest="rasterdir", help="directory where data is stored"
        )
        inputrastergroupparser.add_argument(
            "--rasterfile", dest="rasterfile", help="one file"
        )

        parser.add_argument(
            "--vector",
            dest="vectorbase",
            help="name of the vectorfile",
            required=True,
        )
        parser.add_argument(
            "--out",
            dest="outpath",
            default=os.path.join(os.getcwd(), "results"),
            help="directory where results shall be saved",
        )
        parser.add_argument(
            "--id", dest="idname", help="name of ID field in vectorfile", required=True
        )

        parser.add_argument(
            "--gpkg_layer",
            dest="gpkg_layer",
            default=None,
            help="Determine the layer in geopackage to be used",
        )

        parser.add_argument(
            "--epsg_for_csv",
            dest="epsg_for_csv",
            default=None,
            help="Determine the EPSG code if vector input is csv file",
        )

        parser.add_argument(
            "--statistics",
            dest="statistics",
            default = ["count", "mean", "median", "std"],
            help="statistics to be extracted",
            nargs="*",
        )
        parser.add_argument(
            "--index",
            dest="indexlist",
            help=" give names of indices to be processed",
            nargs="*",
        )
        parser.add_argument(
            "--start",
            dest="startdate",
            default="20160101",
            help="give startdate of timerange of interest",
        )
        parser.add_argument(
            "--end",
            dest="enddate",
            default=datetime.now().strftime("%Y%m%d"),
            help="give enddate of timerange of interest",
        )

        parser.add_argument(
            "--tiles",
            dest="tiles",
            default=None,
            help="Sentinel-2 Tile or tiles to be processed in format XX*** where X are numbers and * are letters",
            nargs="*",
        )
        parser.add_argument(
            "--tifbands",
            dest="tifbands",
            default=[1],
            nargs="*",
            help="Bands of tif to be processed. Defaults to [1].",
        )

        parser.add_argument(
            "--test",
            dest="test",
            action="store_true",
            help="only needed for automatic testing",
        )
        parser.add_argument(
            "--exclude_border",
            dest="exclude_border",
            action="store_true",
            help="if this flag is set border pixels are excluded from calculations",
        )
        parser.add_argument(
            "--external_cloudmask",
            dest="extmask",
            default=None,
            help=" location and name of external cloudmask (without tile and date and extension) if available",
        )
        parser.add_argument(
            "--no_cloudmask",
            dest="nomask",
            action="store_true",
            help="Flag to indicate that cloudmask shall not be applied.",
        )
        parser.add_argument(
            "--delete_invalid_geometries",
            dest="drop_geom",
            action="store_true",
            help="Flag to indicate if invalid geometries should be removed from the processing.",
        )
        parser.add_argument(
            "--verbose",
            "-v",
            dest="verbose",
            action="store_true",
            help=" logging in logfile and prints in terminal",
        )

        parser.add_argument(
            "--geotiff_out",
            dest="geotiff_out",
            action="store_true",
            help="flag to indicate that geotiffs shall be extracted",
        )
        parser.add_argument(
            "--statistics_out",
            dest="statistics_out",
            action="store_true",
            help="flag to indicate that statistics shall be calculated",
        )
        parser.add_argument(
            "--array_out",
            dest="array_out",
            action="store_true",
            help="flag to indicate that arrays shall be extracted",
        )
        parser.add_argument(
            "--database_out",
            dest="database_out",
            action="store_true",
            help="flag to indicate that statistics shall be saved to a database",
        )

        parser.add_argument(
            "--maxcloudcover",
            dest="maxcloudcover",
            default=99,
            help="A value restricting the processing of imagery with too high cloud coverage. Defaults to 99. Currently only operational with Sentinel-2 imagery."
        )

        parser.add_argument(
            "--resampling_method",
            dest="resampling_method",
            default="bilinear",
            help="If bands are not available directly in the given pixelsize, they need to be resampled. Available resampling methods and a short description can be found here: https://rasterio.readthedocs.io/en/latest/api/rasterio.enums.html#rasterio.enums.Resampling"
        )

        args = parser.parse_args()

        self.platform = args.platform
        configfile = "config/config_" + self.platform + ".yml"

        # loading config files and merging into one dict
        with open(configfile, "r") as ymlfile:
            platform_cfg = yaml.safe_load(ymlfile)

        self.config = platform_cfg

        self.rasterdir = args.rasterdir
        self.rasterfile = args.rasterfile
        if self.rasterfile is not None:
            if self.rasterfile[-1] == "/":
                self.rasterfile = self.rasterfile[:-1]
            self.input = [self.rasterfile]

        else:
            # self.input = glob.glob(os.path.join(args.rasterdir,self.config['productnameidentifier']))
            # this searches for exact right files fitting a given pattern
            self.input = [
                os.path.join(self.rasterdir, file)
                for file in os.listdir(self.rasterdir)
                if re.search(self.config["filepattern"], file)
            ]
            if self.rasterdir[-1] == "/":
                self.rasterdir = self.rasterdir[:-1]

        if not self.input:
            quit("No imagery for given platform was found. Please check your inputs.")
        self.epsg_for_csv = args.epsg_for_csv
        self.gpkg_layer = args.gpkg_layer
        # remove extension if given by mistake (assumption, . is only used to separate filename from extension)
        # if '.' in args.vectorbase:
        # self.vectorbase = os.path.splitext(args.vectorbase)[0]
        # else:
        self.vectorbase = args.vectorbase
        self.outpath = args.outpath
        if not os.path.exists(self.outpath):
            os.mkdir(self.outpath)
        self.idname = args.idname

        self.statistics_out = args.statistics_out

        self.array_out = args.array_out
        self.indexlist = args.indexlist

        # Change indices to lower range in case they were written uppercase
        if self.indexlist:
            for i in range(len(self.indexlist)):
                if self.indexlist[i].startswith("B"):
                    continue
                else:
                    self.indexlist[i] = self.indexlist[i].lower()
        
        # Add count to statistics in case it's missing
        default_statistics = ["std", "median", "mean", "count"]
        for stat in default_statistics:
            if stat not in args.statistics:
                args.statistics.insert(0, stat)

        self.statistics = args.statistics      
        self.startdate = args.startdate
        self.enddate = args.enddate
        self.database_out = args.database_out

        self.drop_geom = args.drop_geom

        self.tiles = args.tiles
        self.tifbands = args.tifbands

        self.geotiff_out = args.geotiff_out
        self.test = args.test
        self.exclude_border = args.exclude_border
        self.extmask = args.extmask
        self.nomask = args.nomask
        self.maxcloudcover = args.maxcloudcover
        self.resampling_method = args.resampling_method
        self.verbose = args.verbose

        # Determine output formats
        self.format = []
        if self.statistics_out:
            self.format.append("statistics")
        if self.geotiff_out:
            self.format.append("geotiff")
        if self.array_out:
            self.format.append("array")
        if self.database_out:
            self.format.append("database")

        # If no output formats are specified, only output statistics
        if len(self.format) == 0:
            self.format.append("statistics")

    def create_logfile(self, output_directory, verbose):

        # Build logfolder name
        logdir = os.path.join(output_directory, "logs")
        # Check if directory exists; if not, create it
        if not os.path.exists(logdir):
            os.mkdir(logdir)

        # Extract filename or directory name based on the length of userinput
        if self.rasterfile is not None:
            inputname = os.path.split(self.rasterfile)[1].split(".")[0]
        else:
            dirname = os.path.split(self.rasterdir)[1]

        if verbose:
            if self.rasterfile is not None:
                logfilename = os.path.join(
                    logdir,
                    inputname
                    + "_"
                    + datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
                    + ".log",
                )
                handlers = [logging.FileHandler(logfilename), logging.StreamHandler()]
            else:
                logfilename = os.path.join(
                    logdir, dirname + "_" + datetime.now().strftime("%Y-%m-%d") + ".log"
                )
                handlers = [logging.FileHandler(logfilename), logging.StreamHandler()]

            logging.basicConfig(level=logging.INFO, handlers=handlers)

        else:
            if self.rasterfile is not None:
                logfilename = os.path.join(
                    logdir,
                    inputname
                    + "_"
                    + datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
                    + ".log",
                )
                logging.basicConfig(filename=logfilename, level=logging.INFO)
            else:
                logfilename = os.path.join(
                    logdir, dirname + "_" + datetime.now().strftime("%Y-%m-%d") + ".log"
                )
                logging.basicConfig(filename=logfilename, level=logging.INFO)
