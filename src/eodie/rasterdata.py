"""

Class for everyhing around the rasterdata.

authors: Samantha Wittke

"""

import glob
import os
import re

import numpy as np
import rasterio
from rasterio.enums import Resampling


class RasterData(object):
    """Raster data related information and transformations.

    Attributes
    -----------
    cfg: dict
        dictionary with configuration elements
    imgpath: str
        location and name of the bands within the raster product
    resamplingdict: dict of str and object
        mapping resampling methods from configuration file to functions of rasterio
    test: boolean
        If testing is performed
    crs: str
        coordinate reference system of the raster product
    epsg: str
        EPSG code of the CRS of the raster product
    affine: object
        affine transformation of the raster product
    """

    def __init__(self, inpath:str, resampling_method, cfg:dict, test=False):
        """Initialize the raster object.

        Parameters
        -----------
        inpath: str
            Location and name of the raster bands of the product
        cfg: dict
            dictionary with configuration elements
        test: boolean
            If testing is performed

        """
        self.cfg = cfg
        self.inpath = inpath
        self.get_metadata()
        self.resamplingdict = {
            "bilinear": Resampling.bilinear,
            "nearest": Resampling.nearest,
            "cubic": Resampling.cubic,
            "cubic_spline": Resampling.cubic_spline,
            "lanczos": Resampling.lanczos,
            "average": Resampling.average,
            "mode": Resampling.mode,
            "gauss": Resampling.gauss,
        }
        self.test = test
        self.resampling_method = resampling_method

    def get_bandfile(self, bandname):
        """Get bandfile given a band name.

        Parameters
        -----------
        bandname: str
            banddesignation of the band

        Returns
        --------
        path: str
            location and name of the band with bandname within the rasterproduct
        resolution: str
            pixelsize of the band file found
        """
        pathbuildinglist = self.cfg["pathbuildinglist"]

        pathbuildinglist = [
            bandname if item == "bandname" else item for item in pathbuildinglist
        ]

        possible_pixelsizes = self.cfg[bandname]
        pixelsize = self.cfg["pixelsize"]

        if pixelsize in possible_pixelsizes:
            pathbuildinglist = [
                str(pixelsize) if item == "pixelsize" else item
                for item in pathbuildinglist
            ]
            resolution = pixelsize
        else:
            resolution = str(min(self.cfg[bandname]))
            pathbuildinglist = [
                resolution if item == "pixelsize" else item for item in pathbuildinglist
            ]

        # S2 has extra resolution directories
        if self.cfg["platform"] == "s2":
            path = glob.glob(
                os.path.join(
                    self.inpath,
                    "".join(pathbuildinglist)[0:4],
                    "".join(pathbuildinglist)[4:],
                )
            )[0]
        else:
            path = glob.glob(os.path.join(self.inpath, "".join(pathbuildinglist)))[0]

        return path, resolution

    def get_metadata(self):
        """Get affine from red band file as representation for all."""
        if self.cfg["platform"] == "tif":
            bandfile = self.inpath
        elif self.cfg["platform"] == "s2":
            pixelsize = self.cfg["pixelsize"]
            if pixelsize == 10:
                bandfile, _ = self.get_bandfile(self.cfg["red"])
            elif pixelsize == 20:
                bandfile, _ = self.get_bandfile(self.cfg["8A"])
            elif pixelsize == 60:
                bandfile, _ = self.get_bandfile(self.cfg["coastal"])
        elif self.cfg["platform"] == "ls8":
            pixelsize = self.cfg["pixelsize"]
            if pixelsize == 30:
                bandfile, _ = self.get_bandfile(self.cfg["red"])
        with rasterio.open(bandfile) as src:
            self.crs = src.crs
            self.epsg = str(src.crs).split(":")[-1]
            self.affine = src.transform
            self.bbox = src.bounds

    def read_array(self, bandfile, dtype="f4"):
        """Get array in given datatype according to bandname.

        Parameters
        -----------
        bandfile: str
            location and name of the band with bandname within the rasterproduct
        dtype: numpy datatype, default f4
            datatype of the output array to be read from bandfile
        Returns
        --------
        array: numpy array
            bandfile as numpy array with dtype

        """
        with rasterio.open(bandfile) as f:
            array = np.array(f.read(1))
        if self.test:
            array = array.astype(dtype)

        return array

    def dn_to_reflectance(self, array):
        """Transform the digital number used when storing raster data to reflectance.

        Parameters
        ----------
        array: numpy array
            array as read from bandfile of the rasterproduct
        Returns
        -------
        reflectance: numpy array
            array with values representing the reflectance
        """
        if self.cfg["platform"] == "s2":
            reflectance = np.divide(array, self.cfg["quantification_value"])
            reflectance = self.clip_to_valid_range(reflectance)

        if self.cfg["platform"] == "ls8":
            reflectance = np.multiply(array, self.cfg["quantification_value"]) - 0.2
            reflectance = self.clip_to_valid_range(reflectance)

        return reflectance

    def get_array(self, band, resampling_method=None):
        """Retrieve an array based on band request.

        Parameters
        -----------
        band: str
            band name in human readable format (eg 'red', 'nir' etc)
        resampling_method: str, optional
            which resampling method should be used if resampling is necessary

        Returns
        --------
        array
            array that has been resampled and transformed as needed based on inputs
        """
        resampling_method = (
            resampling_method
            if resampling_method is not None
            else self.resampling_method
        )

        if re.match(r"%s" % self.cfg["band_designation"], band):
            bandname = band
        else:
            bandname = self.cfg[band]
        bandfile, resolution = self.get_bandfile(bandname)
        resolution = int(resolution)
        targetresolution = int(self.cfg["pixelsize"])
        scaling_factor = resolution / targetresolution
        if targetresolution == resolution:
            array = self.read_array(bandfile)
        else:
            array = self.resample(bandfile, scaling_factor, resampling_method)

        if band == "cloudfilename":
            return array
        else:
            return self.dn_to_reflectance(array)

    def resample(self, bandfile, scaling_factor, resampling_method, dtype="f4"):
        """Read the information of a band from raster product and resampling it to fit requirements (inputs).

        Parameters
        ----------
        bandfile: str
            location and name of the band with bandname within the rasterproduct
        scaling_factor: float
            scaling factor for the resampling operation
        resampling_method: str
            which resampling method should be used
        dtype: numpy datatype, default: f4
            datatype of the output array to be read from bandfile
        Returns
        --------
        data: numpy array
            array with the data trnsformed according to inputs
        """
        with rasterio.open(bandfile) as dataset:
            data = dataset.read(
                out_shape=(
                    int(dataset.height * scaling_factor),
                    int(dataset.width * scaling_factor),
                ),
                resampling=self.resamplingdict[resampling_method],
            )
            # above results in 3D data, reshape needed to get 2D data
            data = data.reshape(data.shape[1], data.shape[2])
            if self.test:
                data = data.astype(dtype)
        return data

    def clip_to_valid_range(self, array):
        """Clips the values to valid range ([0,1] in case of Sentinel-2), other values are NoData.

        Parameters
        -----------
        array: array
            array to be clipped

        Returns
        --------
        array: array
            result of clipping
        """

        # Set values above 1 to np.NaN
        array[array > 1] = np.NaN
        # Set values below or equal to 0 to np.NaN
        array[array <= 0] = np.NaN
        return array
