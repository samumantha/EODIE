# EODIE - Earth Observation Data Information Extractor 

## Purpose 

EODIE is a toolkit ot extract object based timeseries information from Sentinel-2 Earth Observation data.

The goal of EODIE is to ease the extraction of time series information at object level. Today, vast amounts of 
Earth Observation data are available to the users via for example earth explorer or scihub. Often, not the whole images 
are needed for exploitation, but only the timeseries of a certain feature on object level. Objects may be polygons depicting 
agricultural field parcels, forest plots, or areas of a certain land cover type.

EODIE takes the objects in as polygons in a vectorfile as well as the timeframe of interest and the features (e.g. vegetation indices) 
to be extracted. The output is a per polygon timeseries of the selected features over the timeframe of interest.

## Installation Instructions and Documentation

Documentation on readthedocs: https://eodie.readthedocs.io/en/latest/

## Maintainers 

Samantha Wittke, Finnish Geospatial Research Institute in the National Land Survey of Finland ([ORCiD](https://orcid.org/0000-0002-9625-7235))

## Contributors

* Eetu Puttonen ([ORCiD](https://orcid.org/0000-0003-0985-4443))
* Juuso Varho
* Petteri Lehti
* Paula Litkey
* Miloš Pandžić ([ORCiD]( https://orcid.org/0000-0003-4982-2630))
* Mika Karjalainen
* Arttu Kivimäki

## Projects

Projects, enabled by EODIE or where EODIE or a derivative of EODIE has been used:

* Project related to deforestation monitoring with Sentinel-1 funded by the European Space Agency (S14Science- Amazonas (http://project.gisat.cz/s14scienceAmazonas/ )),
* Two projects related to crop and crop yield monitoring funded by Eurostat (CROPYIELD (https://www.luke.fi/projektit/cropyield/) and BIGDATA&EO (https://www.luke.fi/projektit/bigdataeo/),
* A Business Finland co-creation project, working with Finnish companies in EO-business to find business opportunities (EODIE: 5332/31/2018),
* Three projects  related to forest phenology and crop monitoring funded by the Academy of Finland (AICropPro (publication https://doi.org/10.1371/journal.pone.0251952), decision numbers 315896 and 316172  (https://www.luke.fi/projektit/ai-croppro/) , BigData, grant-number: 295047, E. Puttonen fellowship, grant-number: 316096),
* Multiple larger national agriculture related projects (such as DIGITALIS (https://www.luke.fi/projektit/digitalis-01/), Peltopiste (https://www.luke.fi/projektit/peltopiste/), Ikivihreä (https://www.luke.fi/projektit/ikivihrea-2/).

## Citation 

EODIE- Earth Observation Data Information Extractor (2022) S. Wittke [online], DOI: https://doi.org/10.5281/zenodo.4762323

## Contribution guide 

Contributions can be made following the [Contribution Guide](http://www.contribution-guide.org/) 

## Acknowledgements

This project was initiated under the Academy of Finland research project 295047 in collaboration with Paula Litkey and Miloš Pandžić and has been supported also from the project 316096/320075. Part of the work has also been done under the umbrella of Academy of Finland flagship project UNITE (337656). Ms. Wittke acknowledges the PhD grant from Aalto School of Engineering. We are also grateful for the constructive comments on the code and documentation by the Nordic-RSE community (Richard Darst, Radovan Bast, Luca Ferranti, Enrico Glerean and Matthew West). The development of the [EODIE Galaxy Tool](https://usegalaxy.eu/root?tool_id=toolshed.g2.bx.psu.edu/repos/climate/eodie/eodie/1.0.2) has been supported by EOSC-Nordic, a project funded by the European Union’s Horizon 2020 research and innovation programme under grant agreement No 857652 and implemented by Anne Fouilloux.

The authors would also like to thank the developers of the following tools:

* EODIE processing workflows have been parallelized with [dask](https://docs.dask.org/en/stable/). 
* The docstring consistency and grammar have been improved with [pydocstyle](https://github.com/PyCQA/pydocstyle).
* Unused imports have been identified with [Vulture](https://github.com/jendrikseipp/vulture).
* The overall code formatting has been improved with [Black](https://github.com/psf/black).




