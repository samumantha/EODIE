.. _Index_table:

Table of supported indices
==========================

Below you can find the table of vegetation indices EODIE currently supports. 

.. csv-table:: 
    :widths: 30, 30, 30, 30
    :align: center
    :header-rows: 1

    Index name,Abbreviation,Formula,Reference
    Normalized Difference Vegetation Index,NDVI,(NIR - RED) / (NIR + RED), Rouse et al. (1973)
    Ratio Vegetation Index,RVI,NIR / RED, `Jordan (1969) <https://doi.org/10.2307/1936256>`_
    Soil-Adjusted Vegetation Index,SAVI,(1.5 * (NIR - RED)) / (NIR + RED + 0.5),`Huete (1988) <https://doi.org/10.1016/0034-4257(88)90106-X>`_
    Normalized Burn Ratio,NBR,(NIR - SWIR2) / (NIR + SWIR2), `López Garcia & Caselles (1991) <https://doi.org/10.1080/10106049109354290>`_
    Kernel Normalized Difference Vegetation Index,kNDVI,(1 - (-(NIR - RED)^2 / (2 * (0.5 * (NIR + RED)^2)))^2) / (1 + (-(NIR - RED)^2 / (2 * (0.5 * (NIR + RED)^2)))^2), `Camps-Valls et al. (2021) <https://doi.org/10.1126/sciadv.abc7447>`_
    Normalized Difference Moisture Index,NDMI,(NIR - SWIR1) / (NIR + SWIR1),`Gao (1996) <https://doi.org/10.1016/S0034-4257(96)00067-3>`_
    Normalized Difference Water Index,NDWI,(GREEN - NIR) / (GREEN + NIR),`McFeeters (1996) <https://doi.org/10.1080/01431169608948714>`_
    Modified Normalized Difference Water Index,MNDWI,(GREEN - SWIR1) / (GREEN + SWIR1),`Xu (2006) <https://doi.org/10.1080/01431160600589179>`_
    Enhanced Vegetation Index,EVI,2.5 * ((NIR - RED) / (NIR + 6 * RED - 7.5 * BLUE + 1)),`Liu & Huete (1995) <https://doi.org/10.1109/TGRS.1995.8746027>`_
    Enhanced Vegetation Index 2,EVI2,2.5 * ((NIR - RED) / (2.4 * RED + NIR + 1)),`Jiang et al. (2008) <https://doi.org/10.1016%2Fj.rse.2008.06.006>`_
    Difference Vegetation Index,DVI,NIR - RED,`Tucker (1979) <https://doi.org/10.1016/0034-4257(79)90013-0>`_
    Chlorophyll Vegetation Index,CVI, (NIR * RED) / (GREEN * GREEN),"`Vincini, Frazzi & D'Elassio (2008) <https://doi.org/10.1007/s11119-008-9075-z>`_"
    Modified Chlorophyll Absorption in Reflectance Index,MCARI,(R_EDGE - RED - 0.2 * (R_EDGE - GREEN) * (R_EDGE / RED),`Daughtry et al. (2000) <https://doi.org/10.1016/S0034-4257(00)00113-9>`_
    Normalized Difference Index 45,NDI45,(R_EDGE - RED) / (R_EDGE + RED),`Delegido et al. (2011) <https://doi.org/10.3390/s110707063>`_
    Tasseled Cap (for Sentinel-2),TCT,"Coefficients * [BLUE, GREEN, RED, NIR, SWIR1, SWIR2]",`Shi & Xu (2019) <https://doi.org/10.1109/JSTARS.2019.2938388>`_
