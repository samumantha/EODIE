"""

Class to calculate indices. Returns an indexarray based on index input.

Authors: Petteri Lehti, Samantha Wittke
    
"""

import numpy as np
import re

np.seterr(divide="ignore", invalid="ignore")
from eodie.rasterdata import RasterData


class Index(RasterData):
    """Calculate vegetation indices from remote sensing raster products."""

    supportedindices = [
        "ndvi",
        "rvi",
        "savi",
        "nbr",
        "kndvi",
        "ndmi",
        "mndwi",
        "evi",
        "evi2",
        "dvi",
        "cvi",
        "mcari",
        "ndi45",
        "tctb",
        "tctg",
        "tctw",
        "ndwi",
    ]

    def __init__(self, inpath:str=".", resampling_method=None, cfg:dict={}, test=False):
        """Initialize the index object.

        Parameters
        ----------
        inpath: str
            Location and name of the raster bands of the product
        cfg: dict
            dictionary with configuration elements
        test: boolean
            If testing is performed

        """
        super().__init__(inpath, resampling_method, cfg, test)
        self.resolution = self.cfg["pixelsize"]

    def mask_array(self, array, maskarray):
        """Create a masked array from an array and a mask with fill value -99999 for masked out values ; e.g. masking out cloudpixels from indexarray.

        Parameters
        ----------
        array: float numpy array
            array to be masked
        maskarray: boolean/int numpy array
            array to be used as mask

        Returns
        -------
        masked: float masked numpy array
            masked numpy array with nan where mask was 'True'/1

        """
        masked = np.ma.array(array, mask=maskarray, fill_value=-99999)

        return masked

    def calculate_index(self, index):
        """Run own class method based on index given.

        Parameters
        -----------
        index: str
            vegetation index to be calculated

        Returns
        --------
        nothing itself, but runs given index function which returns a numpy array of the calculated index

        """
        default = "Unavailable index"
        return getattr(self, "calculate_" + index, lambda: default)()

    def norm_diff(self, a: np.ndarray, b: np.ndarray) -> np.ndarray:
        """Calculate normalized difference.

        Parameters
        -----------
        a: float numpy array
            array to be used as a in formula (a-b)/(a+b)
        b: float numpy array
            array to be used as b in formula (a-b)/(a+b)

        Returns
        --------
        normdiff: float numpy array
            normalized difference between a and b
        """
        normdiff = np.divide(a - b, a + b)
        return normdiff

    def calculate_ndvi(self):
        """Calculate Normalized Difference Vegetation Index (NDVI) from red and nir bands (Kriegler FJ, Malila WA, Nalepka RF, Richardson W (1969) Preprocessing transformations and their effect on multispectral recognition. Remote Sens Environ VI:97–132."""
        red = self.get_array("red")
        nir = self.get_array("nir")

        ndviarray = self.norm_diff(nir, red)

        return ndviarray

    def calculate_rvi(self):
        """Calculate Ratio Vegetation Index (Jordan 1969 - https://doi.org/10.2307/1936256) from red and nir bands."""
        red = self.get_array("red")
        nir = self.get_array("nir")

        rviarray = np.divide(nir, red)

        return rviarray

    def calculate_savi(self):
        """Calculate Soil Adjusted Vegetation Index (Huete (1988) - https://doi.org/10.1016/0034-4257(88)90106-X) from red and nir bands with factors 1.5 and 0.5."""
        red = self.get_array("red")
        nir = self.get_array("nir")

        saviarray = np.divide(1.5 * (nir - red), nir + red + 0.5)

        return saviarray

    def calculate_nbr(self):
        """Calculate Normalized Burnt Ratio (Key & Benson (1999))  from nir and swir2 bands."""
        nir = self.get_array("nir")
        swir2 = self.get_array("swir2")

        nbrarray = self.norm_diff(nir, swir2)

        return nbrarray

    def calculate_kndvi(self):
        """Calculate Kernel NDVI (Camps-Valls et al. (2021) - https://doi.org/10.1126/sciadv.abc7447) from red and nir bands with sigma pixelwise calculation."""
        red = self.get_array("red")
        nir = self.get_array("nir")

        # pixelwise sigma calculation
        sigma = 0.5 * (nir + red)
        knr = np.exp(-((nir - red) ** 2) / (2 * sigma**2))
        kndviarray = (1 - knr) / (1 + knr)

        return kndviarray

    def calculate_ndmi(self):
        """Calculate Normalized Moisture Index (NDMI)  as it is used by Wilson (2002) https://doi.org/10.1016/S0034-4257(01)00318-2 similar to the Gao (1996 - https://doi.org/10.1016/S0034-4257(96)00067-3) NDWI, but NOT McFeeters NDWI (1996) https://en.wikipedia.org/wiki/Normalized_difference_water_index."""
        nir = self.get_array(
            "nir"
        )  # B8A would be more accurate for NDWI and would fit well w/ NDMI as well?
        swir1 = self.get_array("swir1")

        ndmiarray = self.norm_diff(nir, swir1)

        return ndmiarray

    def calculate_ndwi(self):
        """Calculate Normalized Difference Water Index (McFeeters (1996) - https://doi.org/10.1080/01431169608948714."""
        green = self.get_array("green")
        nir = self.get_array("nir")

        ndwiarray = self.norm_diff(green, nir)
        return ndwiarray

    def calculate_mndwi(self):
        """Calculate Modified Normalized Difference Water Index (Xu (2006) - https://doi.org/10.1080/01431160600589179)."""
        green = self.get_array("green")  # Modified from McFeeters NDWI
        swir1 = self.get_array("swir1")  # mir, band11 for Sentinel-2

        mndwiarray = self.norm_diff(green, swir1)
        return mndwiarray

    def calculate_evi(self):
        """Calculate Enhanced Vegetation Index (Liu & Huete (1995) - https://doi.org/10.1109/TGRS.1995.8746027) with L =1, C1 = 6, C2 = 7.5 and G= 2.5."""
        nir = self.get_array("nir")
        red = self.get_array("red")
        blue = self.get_array("blue")

        L = 1
        C1 = 6
        C2 = 7.5
        G = 2.5

        num = nir - red
        denom = nir + C1 * red - C2 * blue + L
        eviarray = G * np.divide(num, denom)
        return eviarray

    def calculate_evi2(self):
        """Calculate Enhanced Vegetation Index 2 (Jiang et al. (2008) -  https://doi.org/10.1016%2Fj.rse.2008.06.006) with L=1, C = 2.4, G=2.5."""
        nir = self.get_array("nir")
        red = self.get_array("red")

        L = 1
        C = 2.4
        G = 2.5

        num = nir - red
        denom = np.multiply(C, red) + nir + L
        evi2array = G * np.divide(num, denom)
        return evi2array

    def calculate_dvi(self):
        """Calculate Difference Vegetation Index (Tucker (1979))."""
        nir = self.get_array("nir")
        red = self.get_array("red")

        dviarray = nir - red
        return dviarray

    def calculate_cvi(self):
        """Calculate Chlorophyll Vegetation Index (Vincini, Frazzi & D'Elassio (2008) - https://doi.org/10.1007/s11119-008-9075-z))."""
        nir = self.get_array("nir")
        red = self.get_array("red")
        green = self.get_array("green")

        cviarray = np.divide(np.multiply(nir, red), green**2)
        return cviarray

    def calculate_mcari(self):
        """Calculate Modified Chrolophyll Absorption in Reflectance Index (Daughtry et al. (2000) - https://doi.org/10.1016/S0034-4257(00)00113-9) only usable with platforms with bands in the red edge area (eg. Sentinel-2)."""
        red = self.get_array("red")
        green = self.get_array("green")
        r_edge = self.get_array("r_edge")

        mcariarray = np.multiply(
            r_edge - red - 0.2 * (r_edge - green), np.divide(r_edge, red)
        )
        return mcariarray

    def calculate_ndi45(self):
        """Calculate Normalized Difference Index 45 (Delegido et al. (2011) - https://doi.org/10.1007/s11119-008-9075-z) only usable with platforms with bands in the red edge area (eg. Sentinel-2)."""
        nir = self.get_array("r_edge")
        red = self.get_array("red")

        ndi45array = self.norm_diff(nir, red)
        return ndi45array

    def calculate_tct(self, coeffs):
        """Calculate general Tasseled Cap Index with Sentinel-2 coefficients (Shi & Xu (2019) - https://doi.org/10.1109/JSTARS.2019.2938388).

        Parameters
        ----------
        coeffs: list of float
            coefficients to calculate spcific tasseled cap
        Returns
        -------
        tctarray: numpy array of float
            calculated tasseled cap array from coefficients
        """
        blue = self.get_array("blue")
        green = self.get_array("green")
        red = self.get_array("red")
        nir = self.get_array("nir")
        swir1 = self.get_array("swir1")
        swir2 = self.get_array("swir2")
        bands = [blue, green, red, nir, swir1, swir2]
        weighted_bands = []
        for i in range(len(bands)):
            weighted_bands.append(np.multiply(coeffs[i], bands[i]))
        tctarray = sum(weighted_bands)
        return tctarray

    def calculate_tctb(self):
        """Calculate Tasseled Cap Brightness coefficients only valid for Sentinel-2."""
        coeffs = [0.3510, 0.3813, 0.3437, 0.7196, 0.2396, 0.1949]

        tctbarray = self.calculate_tct(coeffs)
        return tctbarray

    def calculate_tctg(self):
        """Calculate Tasseled Cap Greenness coefficients only valid for Sentinel-2."""
        coeffs = [-0.3599, -0.3533, -0.4734, 0.6633, 0.0087, -0.2856]

        tctgarray = self.calculate_tct(coeffs)
        return tctgarray

    def calculate_tctw(self):
        """Calculate Tasseled Cap Wetness coefficients only valid for Sentinel-2."""
        coeffs = [0.2578, 0.2305, 0.0883, 0.1071, -0.7611, -0.5308]

        tctwarray = self.calculate_tct(coeffs)
        return tctwarray
