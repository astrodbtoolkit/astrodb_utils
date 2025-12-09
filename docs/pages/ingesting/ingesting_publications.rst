.. _ingesting_publications:

Ingesting publications
=======================
Ingesting a publication is a process of creating a new publication in the database.
The publication is created based on the metadata provided by the user.

`astrodb_utils` can query the `NASA Astrophysics Data System <https://ui.adsabs.harvard.edu/>`_ with the `ingest_publications` function.
To use this feature, you'll need to set up an ADS token and add it to your environment.

Set up ADS token
-----------------------

1. Make an ADS account at `https://ui.adsabs.harvard.edu/help/api/`.
2. Go to `https://ui.adsabs.harvard.edu/user/settings/token`.
3. Copy the token.
4. Add the `ADS_TOKEN` environment variable to your shell startup script, 

   * If using the `zsh` shell, this can be done by adding the following line to your `~/.zshenv`. If you don't have a `.zshenv` file, create one in your home directory.
   
    .. code-block:: zsh

        export ADS_TOKEN="<your token>"

replacing <your token> with the token you copied.


Ingesting publications
-----------------------
Below is an example script for ingesting the discovery publication for Rojas et al. 2012 into the SIMPLE Archive

.. code-block:: python
    from astrodb_utils.publications import ingest_publication, find_publication
    from astrodb_utils.loaders import read_db_from_file

    SAVE_DB = False # Set to True to write out the JSON files at the end of the script

    # Load the database
    db = read_db_from_file(db_name = "SIMPLE")

    # Test if publication already exists
    found, pub_ref = find_publication(db =db, doi="10.1088/0004-637X/748/2/93")
    if not found:
        logger.info("Publication not found in database. Ingesting...")
        # Ingest discovery publication
        ingest_publication(
            db,
            doi="10.1088/0004-637X/748/2/93"
        )
    else:
        logger.info("Publication already exists in database: {pub_ref}")

    if SAVE_DB:
        db.save_database()



.. seealso::

  :doc:`../template_schema/lookup_tables/publications`
      Documentation on the Publications table

  :py:mod:`find publication <astrodb_utils.publications.find_publication>` function
        
  :py:mod:`ingest_publication <astrodb_utils.publications.ingest_publication>` function
