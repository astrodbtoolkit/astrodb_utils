Frequently Asked Questions
================================

    **Q: Why am I getting a `UniqueConstraintError` when trying to ingest data?**

    A: A `UniqueConstraintError` typically occurs when you attempt to ingest data that already exists in the database with the same unique identifier. To avoid this error, use functions such as `find_publication`, `find_source_in_db`, or refer to the database to check for existing entries before ingestion. If an entry already exists, you can skip the ingestion, update the existing entry, or merge the data as needed.

    **Q: Why am I getting an `IntegrityError` when trying to ingest data?**

    A: An `IntegrityError` usually indicates that there is a violation of database constraints, such as foreign key constraints or not-null constraints. This can happen if you are trying to ingest data that references another table, but the referenced entry does not exist in the database. To resolve this, ensure that all referenced entries are present in the database before ingesting the new data. You may need to ingest related data first or check for missing references.

    **Q: Why am I getting an `AstroDBError` when trying to ingest data?**

    A: The `AstroDBError` is a general error that can occur for various reasons during the ingestion process. Common causes include missing required fields, invalid data formats, or duplicate entries. To resolve the issue, check the error message for specific details about the problem. Ensure that all required fields are provided and correctly formatted.

    **Q: Why am I getting a `ForeignKeyViolationError` when trying to ingest data?**

    A: A `ForeignKeyViolationError` occurs when you attempt to ingest data that references another table, but the referenced entry does not exist in the database. To resolve this, ensure that all referenced entries are present in the database before ingesting the new data. You may need to ingest related data first or check for missing references.

    **Q: Why am I getting a `DataTypeError` when trying to ingest data?**

    A: A `DataTypeError` occurs when the data being ingested does not match the expected data type for a particular field in the database. To resolve this, verify that the data types of the fields being ingested align with the database schema. For example, ensure that numerical fields contain numbers, date fields contain valid dates, and string fields contain text.

    .. note:: 
        Make sure to read the error messages carefully, as they often provide specific information about what went wrong during the ingestion process.

        Make sure to refer to the relevant documentation for guidance on how to properly format and ingest data into the database.

        Make sure to keep counters for successfully ingested and skipped entries to monitor the ingestion process effectively.

Sources
-------------------

.. seealso:: `Ingest Scripts <https://astrodb-utils.readthedocs.io/en/stable/pages/ingesting/ingest_scripts.html>`_

Publications
------------------------

.. seealso:: `Ingesting Publications <https://astrodb-utils.readthedocs.io/en/stable/pages/ingesting/ingesting_publications.html>`_

Spectra
---------------------

    Q: I am having trouble ingesting spectra into the database. What are some common issues?
    
    A: Common issues when ingesting spectra include incorrect file formats, missing metadata, or mismatched source references. Ensure that the spectra files are in a supported format (e.g., FITS) and that all required metadata fields are provided. Additionally, verify that the source associated with the spectra exists in the database.   

.. seealso:: `Spectra <https://astrodb-utils.readthedocs.io/en/stable/pages/ingesting/spectra/index.html>`_

Links and Websites
-------------------

    Q: Where can I find more information about `astrodb_utils` and its features?
    
    A: You can visit the official `astrodb_utils GitHub repository <https://github.com/astrodbtoolkit/astrodb_utils>`_

    Q: Are there any other astronomical databases to refer to?

    A: Yes! Here are some useful links:

    - `NASA Astrophysics Data System (ADS) <https://ui.adsabs.harvard.edu/>`_

    - `SIMBAD Astronomical Database <http://simbad.u-strasbg.fr/simbad/>`_

    - `VizieR Catalogue Service <https://vizier.u-strasbg.fr/viz-bin/VizieR>`_

    - `The Sloan Digital Sky Survey (SDSS) <https://www.sdss.org/>`_

    - `The Gaia Archive <https://gea.esac.esa.int/archive/>`_ 


    For additional information, you can also explore the `AstrodbKit documentation <https://astrodbkit.readthedocs.io/en/latest/index.html>`_.
