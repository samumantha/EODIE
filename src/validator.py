"""

class to validate user inputs

"""

import os
import datetime


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
        #self.prj_check(args.inputshape)
        self.date_check(args.startdate)
        self.date_check(args.enddate)

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

    def prj_check(self, inputshape):
        """ check that the given shapefile has a accompanying "prj" file that is needed for projection information
        Parameters
        -----------
        inputshape: str
            location and name of the shapefile to be checked
        Returns
        --------
        check_ok: boolean
            if projection file exists, exits if not
        """
        
        if inputshape is not None:
            ishapepath, ishapename = os.path.split(inputshape)
            prjfile = os.path.splitext(ishapename)[0] + '.prj'
            
            if prjfile not in os.listdir(ishapepath):
                exit('Please provide a .prj file for the inputshapefile!')
            else:
                return True
        else:
            exit('Please provide a shapefile with polygons')

            


    
 
