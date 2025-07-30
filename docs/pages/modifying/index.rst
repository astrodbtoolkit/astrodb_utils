Modifying an Existing Schema
============================
The template database comes with an existing schema,
consisting of a set of tables and columns.
It is expected that every usecase will modify this schema to suit their needs.
However, it is important to follow some guidelines to ensure that the
database remains functional with the rest of the Toolkit.


.. toctree::
   :glob:
   :maxdepth: 1

   new_columns
   new_tables
   yaml

Database structure
------------------
Required tables
~~~~~~~~~~~~~~~~
There are several tables which are expected by ``astrodb_utils``
and should be modified with great care:

* Sources
* Names
* Publications
* Versions
* Telescopes
* Instruments


Optional tables
~~~~~~~~~~~~~~~
Optional tables are things like Spectra, Photometry, Radial Velocities, etc.
These are included in the template database and can be used as models for
other data tables and can be removed/modified if not needed.


Philosophy and guidelines
-------------------------
We encourage users to follow the detailed best practices for
astronomical databases outlined in
`Chen et al. 2022 <https://iopscience.iop.org/article/10.3847/1538-4365/ac6268>`_.


Workflow Overview
-----------------
#. :doc:`Modify the schema YAML file <yaml>`
   in ``schema/schema.yaml`` to suit your use case.

   * We highly recommend using an AI coding assistant
     (like GitHub Copilot) when modifying this file.

#. Generate a new entity relationship diagram (ERD)
   and documentation pages for your schema.

   * To make a new ERD, run ``scripts/build_schema_docs.py``.
     This generates a PNG file in the ``docs/figures/`` directory.

   * To make new documentation pages, run ``scripts/build_schema_docs.py``.
     This generates a new set of Markdown files
     in the ``docs/schema/`` directory.

#. Ingest data by modifying the JSON files by hand
   (in the ``data/`` directory) or by using ``astrodb_utils`` functions.