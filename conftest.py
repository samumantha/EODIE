import sys
sys.path.append("./objects")
from test_objects import TestObjects


# Prevent pytest from trying to collect the testobjects object as tests:
TestObjects.__test__ = False
