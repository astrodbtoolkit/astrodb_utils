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
   :maxdepth: 2

   pages/getting_started/index
   pages/db_management/index
   pages/db_access/index
   pages/utilities/index
   pages/reference/index


License & attribution
---------------------

Copyright 2024 Kelle Cruz, Arjun B. Savel, David Rodriguez

The source code is made available under the terms of the BSD 3-Clause license.

If you make use of this package, please be sure to reference
this repository in your work.
