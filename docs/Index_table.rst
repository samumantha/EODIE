.. _Index_table:

Table of supported indices
==========================

Below you can find the table of vegetation indices EODIE currently supports. 

.. csv-table:: 
    :widths: 30, 30, 30, 30
    :align: right
    :header-rows: 1

    Index name,Abbreviation,Formula,Reference
    Normalized Difference Vegetation Index,NDVI,(NIR - RED) / (NIR + RED),Kriegler et al. (1969)
    Ratio Vegetation Index,RVI,NIR / RED,Tucker (1979)
    Soil-Adjusted Vegetation Index,SAVI,(1.5 * (NIR - RED)) / (NIR + RED + 0.5),`Huete (1988) <https://www.google.com>`_
    Normalized Burnt Ratio,NBR,(NIR - SWIR2) / (NIR + SWIR2),
    Kernel Normalized Difference Vegetation Index,kNDVI,, `Camps-Valls et al. (2021) <https://doi.org/10.1126/sciadv.abc7447>`_
    Normalized Difference Moisture Index,NDMI,(NIR - SWIR1) / (NIR + SWIR1),Gao (1996)
    Normalized Difference Water Index,NDWI,(GREEN - NIR) / (GREEN + NIR),McFeeters (1996)
    Modified Normalized Difference Water Index,mNDWI,(GREEN - SWIR1) / (GREEN + SWIR1),Xu (2007)
    Enhanced Vegetation Index,EVI,2.5 * ((NIR - RED) / (NIR + 6 * RED - 7.5 * BLUE + 1)),Matsushita et al. (2007)
    Enhanced Vegetation Index 2,EVI2,2.5 * ((NIR - RED) / (2.4 * RED + NIR + 1)),Jiang et al. (2008)
    Difference Vegetation Index,DVI,NIR - RED,Naji (2018)
    Chlorophyll Vegetation Index,CVI, (NIR * RED) / (GREEN²),"Clevers, Koolstra & Van den Brande (2017)"
    Modified Chlorophyll Absorption in Reflectance Index,MCARI,(R_EDGE - RED - 0.2 * (R_EDGE - GREEN) * (R_EDGE / RED),Daughtry et al. (2000)
    Normalized Difference Index 45,NDI45,(R_EDGE - RED) / (R_EDGE + RED),Kumar et al. (2021)
    Tasseled Cap (for Sentinel-2),TCT,"Coefficients * [BLUE, GREEN, RED, NIR, SWIR1, SWIR2]",Shi & Xu (2019)
