Ingest Scripts
==============
Ingest scripts can be used to add a bunch of data to the database at once.
Often ingests are performed by reading in a file (e.g., csv) that contains
a table of data and then ingesting each row of the table into the database.
Below is an example script for ingesting sources discovered by
Rojas et al. 2012 into the SIMPLE Archive from a .csv file
that has columns named `name`, `ra`, `dec`.

.. code-block:: python

    from astropy.io import ascii
    from simple.schema import REFERENCE_TABLES
    from astrodb_utils import load_astrodb, logger, AstroDBError
    from astrodb_utils.sources import ingest_source
    from astrodb_utils.publications import ingest_publication

    SAVE_DB = False # Set to True to write out the JSON files at the end of the script
    RECREATE_DB = True # Set to True to recreate the database from the JSON files

    # Load the database
    db = load_astrodb("SIMPLE.sqlite",
                recreatedb=RECREATE_DB,
                reference_tables=REFERENCE_TABLES,
                felis_schema="simple/schema.yaml",
                )


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
                    reference="Roja12"],
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
