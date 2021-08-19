More
====

Platform specific configuration files
--------------------------------------

The platform specific configuration files are named config_x.yml with x being the platform name.
These files allow changes that are specific to the platform that is used. 
In general, the user will not need to touch these ever. 
The only cases where changes in these files are necessary is:

* If e.g. a red edge band (in case of Sentinel-2) should be used instead of the red band in index calcualtions with the red band.
* If the classes of pixels masked in EODIE need to be changed eg to exclude the masking of cirrus clouds or include the masking of snow (where available)

The following parameters need to be included in a config_x.yml file to be used in EODIE:

platform: 
tobemaskedlist: 

red : 
green: 
blue: 
nir: 
r_edge: 
swir1: 
swir2: 

bandlocation: 
pathbuildinglist: 
cloudfilename:
tilepattern: 
datepattern: 
band_designation:
quantification_value: 

B01: 
B02: 
B03: 
B04: 
B05: 
B06: 
B07: 
B08: 
B8A: 
B09: 
B11: 
B12: 



.. _extending_eodie:

Extending EODIE
----------------

EODIE is a never ending story, there is always more to be done. While you can report missing functionality via issue on the gitlab repository, please also consider contributing.
One 'no coding required' option to contribute is, to extend the platform capabilities of EODIE.
This can be done by adding another ``config_x.yml`` with x being the platform in question. 
See above for the parameters that need to be included in the config_x.yml file to be used in EODIE.




