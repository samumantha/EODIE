.. EODIE documentation master file, created by
   sphinx-quickstart on Fri Mar 12 19:57:28 2021.


EODIE 2.0.0 Documentation
==========================

Purpose 
--------

EODIE is a toolkit to extract object based timeseries information from Earth Observation data.

The EODIE code can be found `on Gitlab <https://gitlab.com/fgi_nls/public/EODIE>`_ .

The goal of EODIE is to ease the extraction of time series information at object level. Today, vast amounts of 
Earth Observation data are available to the users via, for example, `Earth Explorer <https://earthexplorer.usgs.gov/>`_  or `SciHub <https://scihub.copernicus.eu/>`_. Often, not the whole images 
are needed for exploitation, but only the timeseries of a certain feature on object level. Objects may be polygons depicting 
agricultural field parcels, forest plots, or areas of a certain land cover type, for instance.

EODIE takes the objects in as polygons in a vector file as well as the timeframe of interest and the features (eg. vegetation indices) 
to be extracted. The output is a per polygon timeseries of the selected features over the timeframe of interest.

Is EODIE suitable for me?
-------------------------

To use EODIE a general understanding of geospatial concepts is helpful.
You will need:

* Access to remote sensing data over your timeframe and area of interest (e.g. Sentinel-2/Landsat 8)
* A geospatial vector file with polygons of your objects of interests - supported formats are, for instance, ESRI Shapefile, GeoPackage, GeoJSON, csv and FlatGeoBuf.

EODIE is particularly designed for people wanting to exploit timeseries information of raster remote sensing data without the need for dealing with particularities of the data itself.
EODIE produces human and machine readable csv files containing all information needed to start working with the data. A database output is also available. 

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
* Arttu Kivimäki


Citation 
---------

EODIE - Earth Observation Data Information Extractor (2022) S. Wittke [online] , DOI: https://doi.org/10.5281/zenodo.4762323

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

The authors would also like to thank the developers of the following tools:

* EODIE processing workflows have been parallelized with `dask <https://docs.dask.org/en/stable/>`_.
* The docstring consistency and grammar have been improved with `pydocstyle <https://github.com/PyCQA/pydocstyle>`_.
* Unused imports have been identified with `Vulture <https://github.com/jendrikseipp/vulture>`_.
* The overall code formatting has been improved with `Black <https://github.com/psf/black>`_.


Changelog
----------

2.0.0
^^^^^^

* Added dependency on dask
* Rewrote eodie_process.py and moved majority of code to workflow.py
* Defined separate workflows for supported platforms (s2, ls8, tif)
* Implemented process parallelization with dask 
* Raster validation, cloudmasking and index extraction are individually parallelized steps - in old EODIE these were executed in loops
* Introduced geopandas GeoDataframe as base format for vector operations
* Removed command line argument --input_type, --keep_splitted_shp and --exclude_splitbytile
* Userinput --vector now requires full path to the vectorfile (extension included)
* Moved content of user_config.yml to userinput and platform-related configuration files
* Added userinput --maxcloudcover to allow user manipulate raster validation
* Added userinput --resampling_method
* Added helper script unzip_ls8_grid.py for unzipping and relocating Landsat 8 tiling grid

1.1.0
^^^^^^

* Added vector file support for GeoPackage, GeoJSON, FlatGeoBuf and csv files.
* Added user inputs for different file types
* Changed user input names (--dir to --rasterdir, --file to --rasterfile, --shp to --vector, --exclude_splitshp to --exclude_splitbytile)
* Removed need for subprocess
* Added helper script examine_geopackage.py
* Renamed helper script examine_shapefile.py to examine_vectorfile.py


1.0.2
^^^^^^

* set usable CPUs for splitshp to 1, if number of available CPUs <= 2

1.0.1
^^^^^^

* Landsat 8 support enabled


.. toctree::
   :titlesonly:
   :caption: Contents:

   self
   Installation
   Gallery
   Example
   Use
   Tutorial
   Galaxy
   Inner_workings
   More
   Database
   Index_table
   Modules