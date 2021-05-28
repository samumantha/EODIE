Installation
=============

Dependencies
-------------

  - python=3.7
  - shapely=1.7
  - rasterio=1.2
  - fiona=1.8
  - numpy=1.20
  - gdal=3.1.4
  - pyyaml=5.4.1

see also ``environment.yml``

Installation instructions
--------------------------

1. Install `Anaconda or Miniconda <https://docs.anaconda.com/anaconda/install/>`_ 
2. Create conda environment from environment.yml ``conda env create -f environment.yml`` 
3. Activate conda environment eodie ``conda activate eodie``

Good to go!

Installation verification
--------------------------

After activating the environment, you can verify that the installation succeeded by typing:

- ``python --version`` 
- ``python -c 'import numpy, shapely, rasterio, fiona, pyyaml'``
- ``python -c 'from osgeo import gdal'``

In the first case, if the python version is displayed, the verification was successfull.
The other calls are successfull if no output is displayed.
In case of a ``ModuleNotFoundError``, use ``conda install -c conda-forge modulename`` to install the missing module.




