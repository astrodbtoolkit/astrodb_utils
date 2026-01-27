Create a New Database
=======================

Start with the template schema which is defined by the
schema YAML file located at ``schema/schema.yaml``.

This file needs to be modified to suit your use case.
e.g., add or rename tables, columns, etc.

#. :doc:`Modify the schema YAML file <../modifying/index>`
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
