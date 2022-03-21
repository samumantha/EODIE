"""

class to validate user inputs

authors: Samantha Wittke

"""

import os
import datetime
from eodie.index import Index
import re


class Validator(object):
    """ validate userinputs for EODIE call"""

    def __init__(self, args):
        """ initialize validator object
        Parameters
        -----------
        args: object
            arguments of the userinput
        """
        self.input_amount_check(args.mydir, args.myfile)
        self.input_exists_check(args.mydir, args.myfile)
        self.date_check(args.startdate)
        self.date_check(args.enddate)
        if not args.indexlist is None and not args.indexlist == []:
            self.index_check(args.config,args.indexlist)
        self.vector_check(args.input_type, args.epsg_for_csv)


    def input_amount_check(self,dir, file):
        """ check that either directory of filename is given as input
        Parameters
        ----------
        dir: str or None
            directory with files to be processed or None (not given) 
        file: str or None
            file to be processed or None (not given)
        """
        if dir is None and file is None:
            exit('Please give either a filename or a directory with files to process')
        elif dir is not None and file is not None:
            exit('Please give only one of filename and path to directory of files')
        
    def input_exists_check(self,dir, file):
        """ check that file or directory that are given exist (typo check) 
        Parameters
        ----------
        dir: str or None
            directory with files to be processed or None (not given) 
        file: str or None
            file to be processed or None (not given)
        """

        if dir is not None:
            try:
                os.path.isdir(dir)
            except:
                exit('Please check the path to your input data directory: ' + dir )
        if file is not None:
            try:
                os.path.isfile(file)
            except:
                exit('Please check the path to yout input file and make sure it exists: ' + file)


    def date_check(self, date):
        """ check that given date is a valid date (typocheck) and a date before today
        Parameters
        -----------
        date: str
            date used to define daterange given by user
        Returns
        --------
        date_ok: boolean
            if date given is ok to use, exits if not
        """
        year = date[:4]
        month = date[4:6]
        day = date[6:8]
        try:
            theday = datetime.datetime(int(year), int(month), int(day))
        except ValueError:
            exit('Please give a valid date')

        today = datetime.datetime.now()

        if theday > today:
            exit('Please make sure your dates are in the past')
        return True

    def index_check(self,cfg,indexlist):
        """ check that all given indices and bands are valid strings, exits if any are not
        Parameters
        ----------
        cfg:
           the configuration dictionary used here to get the bad designation for the current platform
        indexlist:
           list of indices given by the user
        Returns
        -------
        indices_ok: boolean
            if all indices and bands given by the user are available
        """
        unknownindices = []
        for index in indexlist:
            if not index in Index.supportedindices and not re.match(cfg['band_designation'], index):
                unknownindices.append(index)
        if len(unknownindices) > 0:
            exit('Chosen index/band {} not available, please make sure you typed the names correctly.'.format(','.join(unknownindices)))
        else:
            return True

    def vector_check(self, extension, epsg):
        """ Check that given object input is of a supported file format, exits if not true
        Parameters
        ----------
        extension:
            the file extension of the object, supported formats are .shp, .gpkg and .geojson
        Returns
        -------
        extension_ok: boolean
            if object given by the user is in a supported format 
        """

        supported_formats = ['.shp', '.gpkg', '.geojson', '.csv', '.fgb'] 
        if extension not in supported_formats:
            exit('Input format is not supported, please use a supported format (.shp, .gpkg, .geojson, .csv or .fgb)')
        if extension == ".csv":
            if epsg == None:
                exit('If using .csv as a vector input, please provide EPSG code for the csv with parameter --epsg_for_csv.')
        else:
            return True     

        


    
 
