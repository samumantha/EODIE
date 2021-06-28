"""

class to validate user inputs

"""

import os
import datetime


class Validator(object):

    def __init__(self, args):
        self.input_amount_check(args.mydir, args.myfile)
        self.input_exists_check(args.mydir, args.myfile)
        self.prjCheck(args.inputshape)
        self.dateValidityCheck(args.startdate)
        self.dateValidityCheck(args.enddate)

    def input_amount_check(self,dir, file):
        if dir is None and file is None:
            exit('Please give either a filename or a directory with files to process')
        elif dir is not None and file is not None:
            exit('Please give only one of filename and path to directory of files')
        
    def input_exists_check(self,dir, file):
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
        if inputshape is not None:
            ishapepath, ishapename = os.path.split(inputshape)
            prjfile = os.path.splitext(ishapename)[0] + '.prj'
            
            if prjfile not in os.listdir(ishapepath):
                exit('Please provide a .prj file for the inputshapefile!')
            else:
                return True
        else:
            exit('Please provide a shapefile with polygons')


    
 
