.. _Installation:

Installation
=============

Dependencies 
-------------

See  `environment.yml <https://gitlab.com/fgi_nls/kauko/chade/EODIE/-/blob/main/environment.yml>`_ .

Recommended installation instructions
--------------------------------------

1. Install `Anaconda or Miniconda <https://docs.anaconda.com/anaconda/install/>`_ 
2. Get the code from gitlab ``git clone https://gitlab.com/eetun-tiimi/EODIE.git``
3. Create conda environment from environment.yml ``conda env create -f environment.yml`` 
4. Activate conda environment eodie ``conda activate eodie``
5. Move into EODIE directory ``cd EODIE/src/eodie``

Good to go!

Installation verification
--------------------------

After activating the environment, you can verify that the installation succeeded by typing:

- ``python --version`` 
- ``python -c 'import numpy, shapely, rasterio, fiona, yaml'``
- ``python -c 'from osgeo import gdal'``

In the first case, if the python version is displayed, the verification was successfull.
The other calls are successfull if no output is displayed.
In case of a ``ModuleNotFoundError``, use ``conda install -c conda-forge modulename`` to install the missing module.

You can further verify the installation and learn about the usage of EODIE as command line tool in :ref:`Example` .




