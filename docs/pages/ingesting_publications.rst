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
3. Copy the token generated on the package.
4. Add the token as an environment variable, `ADS_TOKEN`. If using the `bash` shell, this can be done with
   
    .. code-block:: bash

        export ADS_TOKEN=<your token>

replacing <your token> with the token you copied.


Ingesting publications
-----------------------
Fill this in...
