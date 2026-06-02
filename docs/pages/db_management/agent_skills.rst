Creating a Database with AI Agent Skills
========================================

`astrodb_bot <https://github.com/astrodbtoolkit/astrodb_bot>`_ provides a set of
**AI agent skills** that guide an assistant (Claude, Cursor, etc.) through building a
new database from a raw data table: parsing the table, mapping its columns to the
:doc:`AstroDB template schema <../getting_started/template_schema/template_schema>`,
generating a Felis ``schema.yaml``, and creating the SQLite database.

In other words, these skills automate the manual workflow described elsewhere in this
section (:doc:`make_new_db/index` and :doc:`modifying/index`).

.. note::

   The skills require an AI **skill runner** — an agent that reads a ``skills/``
   directory such as ``.claude/skills/``, ``.cursor/skills/``, or ``.agents/skills/``.

   These skills only apply to the local repository you're running the agent from.
   If you want these skills to be available globally, copy them into ``%USERPROFILE%/.claude/skills/`` or the equivalent for your agent.

Installation
------------
Copy the ``skills/`` directory from the
`astrodb_bot repository <https://github.com/astrodbtoolkit/astrodb_bot>`_ into the
location your agent reads skills from. For example, with Claude:

.. code-block:: bash

    git clone https://github.com/astrodbtoolkit/astrodb_bot.git
    mkdir -p .claude/skills
    cp -r astrodb_bot/skills/* .claude/skills/

Requirements
~~~~~~~~~~~~~
* Python 3.11 or greater
* ``uv`` or ``pip`` to install Python packages
* ``astropy``, ``pandas``, ``lsst-felis``, ``astrodbkit``, and ``astrodb_utils``

The skills
----------
The skills are designed to run in sequence, each feeding the next, but any of them can
also be run on its own.

#. **astrodb-parse-data-table** — Reads a data table (FITS, CSV, ECSV, HDF5, VOTable,
   Parquet, Excel, ...) and summarizes every column's name, description, units, and
   type as a Markdown and HTML report.

#. **astrodb-match-schema** — Maps each parsed column to a table and field in the
   AstroDB template schema, assigning a confidence level to every match and flagging
   anything it cannot place.

#. **astrodb-validate-schema-mapping** — Checks the proposed mapping against the actual
   data: null values landing in non-nullable fields, and type mismatches between the
   data and the schema.

#. **astrodb-generate-schema** — Turns the validated mapping into a Felis-format
   ``schema.yaml`` (see :doc:`modifying/yaml`) and runs ``felis validate`` on it.

#. **astrodb-create-db** — Creates an empty SQLite database from the validated
   ``schema.yaml``, following the
   `astrodb-template-db <https://github.com/astrodbtoolkit/astrodb-template-db>`_ file
   layout, and generates a matching test suite.

#. **astrodb-ingest-source** — Generates and runs a script that ingests sources from
   the data table into the new database using ``astrodb_utils.sources.ingest_source``.
   See also :doc:`../db_access/ingesting/getting_started_ingesting`.
