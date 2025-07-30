AstroDB Toolkit
==================================

The AstroDB Toolkit provides a set of tools to help astronomers work with
and create databases.
The `astrodb_utils` package provides a set of functions to
query and ingest data into databases built with the
`astrodb-template-db` schema.
Currently, the Toolkit only supports SQLite databases.
Under the hood, the Toolkit uses `AstrodbKit <https://github.com/astrodbtoolkit/AstrodbKit>`_,
a package built on `SQLAlchemy <https://www.sqlalchemy.org/>`_.


User Guide
==================================

.. toctree::
   :glob:
   :maxdepth: 1

   Overview of the AstroDB Toolkit <pages/overview/organization>
   pages/querying_existing_db/index
   pages/ingesting/getting_started_ingesting
   pages/modifying/index
   pages/make_new_db/getting_started_new_database
   pages/template_schema/template_schema
   pages/making_private_version
   pages/ingesting/spectra/converting_spectra/converting_spectra
   pages/getting_help/index
   Developer documentation <pages/dev_docs/developer_installation>
   API documentation <pages/api>


License & attribution
---------------------

Copyright 2024 Kelle Cruz, Arjun B. Savel, David Rodriguez

The source code is made available under the terms of the BSD 3-Clause license.

If you make use of this package, please be sure to reference
this repository in your work.
