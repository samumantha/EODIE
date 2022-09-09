.. _Database:

Database instructions
=====================

Here you can find brief summary on EODIE's database implementation.

How does EODIE save data into the database?
-------------------------------------------

Database implementation of EODIE has been built with `sqlite3 module <https://docs.python.org/3/library/sqlite3.html>`_.
If database is chosen as the output file format for zonal statistics, a new database file with the name ``EODIE_results.db`` will be created in output directory. In case such file already exists, EODIE tries to continue writing to the existing database file. 

Each individual index calculation process in EODIE connects to the database, inserts the results to the respective table and close the connection. Results for each index or band are stored in a separate tables that can have different field structures. 

How to export results from the database?
----------------------------------------

A postprocessing script ``export_from_database.py`` is provided in ``postprocesses`` for filtering and exporting the data into csv-files. Please use ``python export_from_database.py --help`` for detailed instructions. 
The data is in a generic .db file, which can also be opened in other softwares or tools based on user expertise. 

For instance, if you wish to export the data in R software, please see `an example on using RQSlite library <https://gist.github.com/jwolfson/72bc7d7fd8d339955b38>`_.

Potential issues with databases
-------------------------------

1. If the output file ``EODIE_results.db`` already exists and new processes will try adding data to the index tables created earlier, please be aware that the field structure (= number and order of statistics) needs to be the same. Otherwise writing results will lead to errors.  

2. If there are several processes trying to edit the database simultaneously, the database might get locked, halting any further data insertion attempts. This can be avoided by adjusting the timeout parameter in database connection, allowing the processes to wait for their editing turn up to 300 seconds (5 minutes). In case this value needs to be increased, it is set on row 107 in ``writer.py``.