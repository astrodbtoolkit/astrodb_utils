Getting Started
=======================

Ingest scripts can be used to add a bunch of data to the database at once. 
Below is a snippet of code taken from a script ingesting proper motions from compilation by Zhang et al. 
These lines should exist in every ingest script:

.. code-block:: python

    logger = logging.getLogger("AstroDB")
    logger.setLevel(logging.INFO)
    SAVE_DB = False  
    RECREATE_DB = True  
    SCHEMA_PATH = "simple/schema.yaml" 

    db = load_astrodb("SIMPLE.sqlite", recreatedb=RECREATE_DB, reference_tables=REFERENCE_TABLES, felis_schema=SCHEMA_PATH)

    L6T6_link = (
        "scripts/ingests/zjzhang/L6_to_T6_benchmarks08062025.csv"
    )

    L6T6_table = ascii.read(
        L6T6_link, 
        format="csv",
        data_start=1, 
        header_start=0, 
        guess=False,
        fast_reader=False,
        delimiter=",", 
    )

Logging Setup
--------------------

When working with data ingestion scripts or database-building workflows, it's important to have a reliable way to understand what the script is doing internally. 
Python's built-in logging module provides a structured system for reporting events, progress updates, and errors during execution.

.. code-block:: python

    logger = logging.getLogger("AstroDB")
    logger.setLevel(logging.INFO)

By instantiating a logger for your script, it creates an easier way for you to track what your script is doing: database loading, ingest errors, warnings, etc. 

The line ``logger.setLevel(logging.INFO)`` configures the logger to display only log messages at level INFO or higher. 
Python provides multiple logging levels, including:
- DEBUG:extremely detailed diagnostic output
- INFO: general runtime information
- WARNING: unexpected events that do not stop execution
- ERROR: serious problems that prevent part of the script from running
- CRITICAL: errors severe enough to stop execution entirely

Database ingestion often involves multiple operations happening quickly, therefore setting the level prevents you from being flooded with low-level debugging messages. 
This filters out unimportant information, making it easier to read and facilitates the process of diagnosing ingestion problems or error messages. 


Loading the Database
-------------------------

.. code-block:: python

    SAVE_DB = False  
    RECREATE_DB = True  
    SCHEMA_PATH = "simple/schema.yaml" 
    db = load_astrodb("SIMPLE.sqlite", recreatedb=RECREATE_DB, reference_tables=REFERENCE_TABLES, felis_schema=SCHEMA_PATH)

When loading the database, it is important to know at which stage you are running your script at. 
For example, SAVE_DB will save the data files in addition to modifying the .db file. 
This should only be true for when you are sure your ingest script works so you don't run into errors. 
RECREATE_DB forces a full rebuild of the SIMPLE database from the data files, essentially reconstructing it from scratch. 
Having this set to true will initialize a clean database for you to work off of when you are still in the beginning stages of writing your script and if you are still rerunning your script often, while setting it to false will preserve any existing data.

Our schema path variable simply points to the YAML schema file which defines the structure of our database, including all the tables, columns, constraints, and foreign keys. 
This is important for when we actually load our database so it is built with the correct structure and information. 


Setting Up Your Data
-------------------------

Often ingests are performed by reading in a file (e.g., csv) that contains a table of data and then ingesting each row of the table into the database.
Therefore, it is important to convert your data into a format that is easy to read in Python.

.. code-block:: python

    L6T6_link = (
        "scripts/ingests/zjzhang/L6_to_T6_benchmarks08062025.csv"
    )

    L6T6_table = ascii.read(
        L6T6_link, 
        format="csv",
        data_start=1, 
        header_start=0, 
        guess=False,
        fast_reader=False,
        delimiter=",", 
    )

First, we define a variable that points to the location of our data file, in which we then use to read in our data file as an Astropy Table. 
Here, we specify that our file is in csv format and provide additional parameters to ensure the file is read correctly. 
For example, data_start and header_start specify which rows contain the data and the header, respectively, while delimiter indicates that the file is comma-separated. 
The resulting ``L6T6_table`` variable is now an Astropy Table object that contains all the data from the csv file, which we can then loop through and ingest each row into the database. 






