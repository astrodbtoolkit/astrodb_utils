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





