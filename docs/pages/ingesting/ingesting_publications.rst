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
Fill this in...


.. seealso::

  :doc:`../template_schema/lookup_tables/publications`
      Documentation on the Publications table

  :py:mod:`find publication <astrodb_utils.publications.find_publication>` function
        
  :py:mod:`ingest_publication <astrodb_utils.publications.ingest_publication>` function
