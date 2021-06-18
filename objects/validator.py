"""

class to validate user inputs

"""

import os
import datetime


class Validator(object):

    def __init__(self, args):
        
        self.prjCheck(args.inputshape)
        self.dateValidityCheck(args.startdate)
        self.dateValidityCheck(args.enddate)


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

    def file_exists_check(self, filename):
        if not os.path.exists(filename):
            exit('Please check that file {} exists.'.format(filename))
        else:
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


    
 
