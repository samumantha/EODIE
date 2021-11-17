import sys
from eodie.test_all import TestAll
from pytest import fixture


# Prevent pytest from trying to collect the testobjects object as tests:
TestAll.__test__ = False
