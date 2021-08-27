.. EODIE documentation master file, created by
   sphinx-quickstart on Fri Mar 12 19:57:28 2021.


EODIE Documentation
====================

Purpose 
--------

EODIE is a toolkit to extract object based timeseries information from Earth Observation data.

The goal of EODIE is to ease the extraction of time series information at object level. Today, vast amounts of 
Earth Observation data are available to the users via for example earth explorer or scihub. Often, not the whole images 
are needed for exploitation, but only the timeseries of a certain feature on object level. Objects may be polygons depicting 
agricultural field parcels, forest plots, or areas of a certain land cover type.

EODIE takes the objects in as polygons in a shapefile as well as the timeframe of interest and the features (eg vegetation indices) 
to be extracted. The output is a per polygon timeseries of the selected features over the timeframe of interest.

Is EODIE suitable for me?
-------------------------

To use EODIE a general understanding of geospatial concepts is helpful.
You will need:
* Access to remote sensing data over your timeframe and area of interest (e.g. Sentinel-2/Landsat)
* A shapefile with polygons of your objects of interests

EODIE is particularly designed for people wanting to exploit timeseries information of raster remote sensing data without the need for dealing with particularities of the data itself.
EODIE produces human and machine readable csv files containing all information needed to start working with the data.

Gallery
--------

Take a look at examples of what EODIE (and its auxiliary scripts) have been used for at :ref:`Gallery`

Installation
-------------

Please visit :ref:`Installation` for installation instructions using conda.

Getting started 
---------------

You can test the usage of EODIE as command line tool by following the :ref:`Example` .

Maintainers
------------

Samantha Wittke, Finnish Geospatial Research Institute in the National Land Survey of Finland

Contributors
-------------

* Eetu Puttonen
* Juuso Varho
* Petteri Lehti
* Paula Litkey
* Milos Pandzic
* Mika Karjalainen

Citation 
---------

EODIE- Earth Observation Data Information Extractor (2021) S. Wittke, online available: https://gitlab.com/eetun-tiimi/EODIE

(Zenodo DOI in progress:
EODIE- Earth Observation Data Information Extractor (2021) S. Wittke [online] reserved DOI: 10.5281/zenodo.4762323)

Contribution guide 
-------------------

Contributions can be made following the `Contribution Guide <http://www.contribution-guide.org/>`_ 


.. toctree::
   :maxdepth: 2
   :caption: Contents:

   self
   Installation
   Gallery
   Example
   Use
   Tutorial
   Inner_workings
   More
   modules
   



