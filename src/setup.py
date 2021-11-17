import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(

    name="EODIE",
    version="1.0.0",
    author="Samantha Wittke",
    author_email="samantha.wittke@nls.fi",
    description="Earth Observation Data Information Extractor",
    long_description=long_description,
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