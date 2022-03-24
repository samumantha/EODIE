.. EODIE documentation master file, created by
   sphinx-quickstart on Fri Mar 12 19:57:28 2021.


EODIE Documentation
====================

Purpose 
--------

EODIE is a toolkit to extract object based timeseries information from Earth Observation data.

The EODIE code can be found `on Gitlab <https://gitlab.com/fgi_nls/public/EODIE>`_ .

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
* A geospatial vector data file with polygons of your objects of interests - supported formats are ESRI 
Shapefile, (GeoPackage, GeoJSON, csv and FlatGeoBuf coming soon!)

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

Samantha Wittke, Finnish Geospatial Research Institute in the National Land Survey of Finland ([ORCiD](https://orcid.org/0000-0002-9625-7235))

Contributors
-------------

* Eetu Puttonen ([ORCiD](https://orcid.org/0000-0003-0985-4443))
* Juuso Varho
* Petteri Lehti
* Paula Litkey
* Miloš Pandžić ([ORCiD]( https://orcid.org/0000-0003-4982-2630))
* Mika Karjalainen


Citation 
---------

EODIE- Earth Observation Data Information Extractor (2022) S. Wittke [online] , DOI: https://doi.org/10.5281/zenodo.4762323

Projects
---------

Projects, enabled by EODIE or where EODIE or a derivative of EODIE has been used:

* Project related to deforestation monitoring with Sentinel-1 funded by the European Space Agency (S14Science- Amazonas (http://project.gisat.cz/s14scienceAmazonas/ )),
* Two projects related to crop and crop yield monitoring funded by Eurostat (CROPYIELD (https://www.luke.fi/projektit/cropyield/) and BIGDATA&EO (https://www.luke.fi/projektit/bigdataeo/),
* A Business Finland co-creation project, working with Finnish companies in EO-business to find business opportunities (EODIE: 5332/31/2018),
* Three projects  related to forest phenology and crop monitoring funded by the Academy of Finland (AICropPro (publication https://doi.org/10.1371/journal.pone.0251952), decision numbers 315896 and 316172  (https://www.luke.fi/projektit/ai-croppro/) , BigData, grant-number: 295047, E. Puttonen fellowship, grant-number: 316096),
* Multiple larger national agriculture related projects (such as DIGITALIS (https://www.luke.fi/projektit/digitalis-01/), Peltopiste (https://www.luke.fi/projektit/peltopiste/), Ikivihreä (https://www.luke.fi/projektit/ikivihrea-2/).


Contribution guide 
-------------------

Contributions can be made following the `Contribution Guide <http://www.contribution-guide.org/>`_ 

Acknowledgements
-----------------

This project was initiated under the Academy of Finland research project 295047 in collaboration with Paula Litkey and Miloš Pandžić and has been supported also from the project 316096/320075. Part of the work has also been done under the umbrella of Academy of Finland flagship project UNITE (337656). Ms. Wittke acknowledges the PhD grant from Aalto School of Engineering. We are also grateful for the constructive comments on the code and documentation by the Nordic-RSE community (Richard Darst, Radovan Bast, Luca Ferranti, Enrico Glerean and Matthew West). The development of the `EODIE Galaxy Tool <https://usegalaxy.eu/root?tool_id=toolshed.g2.bx.psu.edu/repos/climate/eodie/eodie/1.0.2>`_ has been supported by EOSC-Nordic, a project funded by the European Union’s Horizon 2020 research and innovation programme under grant agreement No 857652 and implemented by Anne Fouilloux.


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
   



