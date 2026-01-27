Ingest Scripts
==============

.. toctree::
   :glob:
   :maxdepth: 1

   writing_scripts

Ingest scripts can be used to add a bunch of data to the database at once.
Often ingests are performed by reading in a file (e.g., csv) that contains
a table of data and then ingesting each row of the table into the database.


Loading the Database
--------------------

.. code-block:: python

    from astrodb-utils import build_db_from_json

    db = build_db_from_json(settings_file = "path/to/database.toml")

First, we need to load our database using the
:py:func:`astrodb_utils.loaders.build_db_from_json` function.
This function takes in a settings file (in TOML format) that contains
information about our database, including its name.
The ``build_db_from_json`` function will perform a full rebuild of the
database from the JSON data files,
essentially reconstructing it from scratch.


Setting Up Your Data
--------------------

Often ingests are performed by reading in a file (e.g., csv) that contains a
table of data and then ingesting each row of the table into the database.
Therefore, it is important to convert your data into a format that is easy
to read in Python.

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

First, we define a variable that points to the location of our data file,
in which we then use to read in our data file as an Astropy Table.
Here, we specify that our file is in csv format and provide additional
parameters to ensure the file is read correctly.
For example, data_start and header_start specify which rows contain the data
and the header, respectively, while delimiter indicates that the file is
comma-separated.
The resulting ``L6T6_table`` variable is now an Astropy Table object that
contains all the data from the csv file, which we can then loop through
and ingest each row into the database.


Another Example Ingest Script
-----------------------------
Below is an example script for ingesting sources discovered by
Rojas et al. 2012 into the SIMPLE Archive from a .csv file
that has columns named `name`, `ra`, `dec`.

.. code-block:: python

    from astropy.io import ascii
    from astrodb_utils.loaders import build_db_from_json
    from astrodb_utils.sources import ingest_source
    from astrodb_utils.publications import ingest_publication

    DB_SAVE = True

    # Load the database
    db = build_db_from_json(settings_file="path/to/database.toml")


    def ingest_pubs(db):
        # Ingest discovery publication
        ingest_publication(
            db,
            doi="10.1088/0004-637X/748/2/93"
            )


    def ingest_sources(db):
        # read the csv data into an astropy table
        data_table = ascii.read(file.csv, format="csv")

        n_added = 0
        n_skipped = 0

        for source in data_table:
            try:
                ingest_source(
                    db,
                    source=data_table['name'],
                    ra=data_table['ra'],
                    dec=data_table['dec'],
                    reference="Roja12",
                )
                logger.info(f"Source {source['name']} ingested.")
                n_added += 1
            except AstroDBError as e:
                logger.warning(f"Error ingesting source {source['name']}: {e}")
                n_skipped += 1
                continue


    ingest_pubs(db)
    ingest_sources(db)

    logger.info(f"Added {n_added} sources, skipped {n_skipped} sources.")

    if DB_SAVE:
        db.save()
