Making a New Database
=====================


Overview
--------

#. Make a new GitHub repository using the `astrodb-template-db <https://github.com/astrodbtoolkit/astrodb-template-db>`_ template repository.

#. Update the ``README.md`` file with your database name and description.

   * Please retain the credit line to the AstroDB Toolkit.

#. Update the ``LICENSE`` file with your license of choice.

#. :doc:`Modify the schema <../modifying/index>`
   to suit your use case.

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


