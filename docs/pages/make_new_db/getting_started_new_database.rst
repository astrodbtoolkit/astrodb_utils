Making a New Database
======================================

.. toctree::
    the_template_schema
    modifying_schema



Overview
--------

1. Make a new Github repository using the `astrodb-template-db <https://github.com/astrodbtoolkit/astrodb-template-db>`_ template repository.
2. Update the README.md file with your database name and description.
   - Please retain the credit line to the template and the AstroDB Toolkit.
3. :doc:`Modify the schema <modifying_schema>` in ``schema/schema.yaml`` to suit your use case.
4. Generate a new entity relationship diagram (ERD) and documentation pages for your schema.
   - To make a new ERD, run ``scripts/build_schema_docs.py``. This generates a .PNG file in the ``docs/figures`` directory.
   - To make new documentation pages, run ``scripts/build_schema_docs.py``. This generates a new set of MarkDown files in the ``docs/schema`` directory.
5. Ingest data by modifing the JSON files by hand (in the ``data/`` directory) or by using ``astrodb_utils`` functions.