import setuptools

#with open("../README.md", "r") as fh:
#    long_description = fh.read()

setuptools.setup(

    name="EODIE",
    version="1.0.0",
    author="Samantha Wittke",
    author_email="samantha.wittke@nls.fi",
    description="Earth Observation Data Information Extractor",
    long_description="# EODIE - Earth Observation Data Information Extractor 

        ## Purpose 

        EODIE is a toolkit ot extract object based timeseries information from Sentinel-2 Earth Observation data.

        The goal of EODIE is to ease the extraction of time series information at object level. Today, vast amounts of 
        Earth Observation data are available to the users via for example earth explorer or scihub. Often, not the whole images 
        are needed for exploitation, but only the timeseries of a certain feature on object level. Objects may be polygons depicting 
        agricultural field parcels, forest plots, or areas of a certain land cover type.

        EODIE takes the objects in as polygons in a shapefile as well as the timeframe of interest and the features (eg vegetation indices) 
        to be extracted. The output is a per polygon timeseries of the selected features over the timeframe of interest.

        ## Installation Instructions and Documentation

        Documentation on readthedocs: https://eodie.readthedocs.io/en/latest/

        ## Maintainers 

        Samantha Wittke, Finnish Geospatial Research Institute in the National Land Survey of Finland

        ## Contributors

        * Eetu Puttonen
        * Juuso Varho
        * Petteri Lehti
        * Paula Litkey
        * Milos Pandzic
        * Mika Karjalainen
        ## Citation 

        EODIE- Earth Observation Data Information Extractor (2021) S. Wittke, online available: https://gitlab.com/eetun-tiimi/EODIE
        ",
    long_description_content_type="text/markdown",
    url="https://eodie.readthedocs.io/en/latest/",
    packages=setuptools.find_packages(),

    install_requires=[

        "numpy",
        "shapely",
        "rasterio",
        "rasterstats",
        "fiona",
        "gdal",
        "pyyaml",
        "pytest",
        "matplotlib"
    ],

    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU GPLv3 License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
