Writing Scripts
===============

When writing ingest scripts, there are two different ways to go about it:
using existing ingest functions from `astrodb_utils` or using sqlalchemy
commands.


Using Existing Ingest functions
-------------------------------
Using existing ingest functions helps streamline the process of writing an
ingest script.
However, only few ingest functions exist, namely for sources, names, and
instruments.
Therefore, if your data fits into one of these categories, it is recommended
to use the existing functions.

Below is an example of how to use the
:py:func:`astrodb_utils.sources.ingest_source` function to ingest source
data into the database:

.. code-block:: python

    for source in bones_sheet_table:

            ingest_source(
                db,
                source=source["NAME"],
                reference=reference[1],
                ra=source["RA"],
                dec=source["DEC"],
                raise_error=True,
                search_db=True,
                comment="Discovery reference from the BONES archive",
            )

Note that the basic structure for any ingest is looping through each row of
your data table and appropriately ingesting each row into the database with
the relevant parameters.
Each ingest function will have different required and optional parameters,
so be sure to check the API documentation for more details.


Using SQLAlchemy Commands
-------------------------
If there is no existing ingest function for your data type, you can use
sqlalchemy commands to directly ingest into the database.

Below is an example of how to ingest modeled parameters data into the database
using sqlalchemy commands:

.. code-block:: python

    for row in L6T6_table:
        with db.engine.connect() as conn:
            conn.execute(
                db.ModeledParameters.insert().values(
                    {
                        "source": L6T6_table["NAME"],
                        "model": L6T6_table["MODEL"],
                        "parameter": L6T6_table["PARAM"],
                        "value": L6T6_table["VAL"],
                        "upper_error": L6T6_table["UPP_ERR"],
                        "lower_error": L6T6_table["LOW_ERR"],
                        "unit": L6T6_table["UNIT"],
                        "comments": "Ingested from compilation by Zhang et al. (2020ApJ...891..171Z)",
                        "reference": L6T6_table["REF"]
                    }
                )
            )
            conn.commit()

Here, we follow the same format of looping through each row of our data table
and then using insert commands to add each row into the database.

Since there is no existing ingest function, there are a few things to keep
note of. For example, make sure to change the table name after ``db.`` to the
appropriate table you are ingesting into.

It is also important to reference the schema to ensure your code matches the
database structure. For example, make sure that the column names inside the
``values()`` method match exactly with the column names in the database schema.
Additionally, the schema, which is available in your code under the utils
folder, will indicate which columns are required versus optional (check nullable
in the column you are referencing), so be sure to include all required columns in
your code to avoid any errors. Finally, make sure to commit the changes to the
database after executing the command with ``conn.commit()``.

Logging Setup
-------------

When working with data ingestion scripts or database-building workflows,
it's important to have a reliable way to understand what the script is
doing internally.
Python's built-in logging module provides a structured system for
reporting events, progress updates, and errors during execution.

.. code-block:: python

    import logging
    logger = logging.getLogger("AstroDB")
    logger.setLevel(logging.INFO)

By instantiating a logger for your script, it creates an easier way for you
to track what your script is doing: database loading, ingest errors, warnings,
etc.

The line ``logger.setLevel(logging.INFO)`` configures the logger to display
only log messages at level INFO or higher.
Python provides multiple logging levels, including:

* DEBUG:extremely detailed diagnostic output
* INFO: general runtime information
* WARNING: unexpected events that do not stop execution
* ERROR: serious problems that prevent part of the script from running
* CRITICAL: errors severe enough to stop execution entirely

Database ingestion often involves multiple operations happening quickly,
therefore setting the level prevents you from being flooded with low-level
debugging messages.
This filters out unimportant information, making it easier to read and
facilitates the process of diagnosing ingestion problems or error messages.
