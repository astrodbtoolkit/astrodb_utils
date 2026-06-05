Creating a Database with AI Skills
========================================

`astrodb_bot <https://github.com/astrodbtoolkit/astrodb_bot>`_ provides a set of
**AI skills** that guide an assistant (Claude, Cursor, etc.) through building a
new database from a raw data table: parsing the table, mapping its columns to the
:doc:`AstroDB template schema <../getting_started/template_schema/template_schema>`,
generating a Felis ``schema.yaml``, and will creating a populated ``DatabaseName.sqlite``.
**Real catalogs are messy.** inconsistent types, missing values, and column names that
don't match the schema. Handling that is becomes much easier when you have an AI 
which has the skills installed. 

These skills automate the manual workflow described elsewhere in this section
(:doc:`make_new_db/index` and :doc:`modifying/index`).

.. note::

   The skills require an AI **skill runner**: an AI that reads a ``skills/``
   directory such as ``.claude/skills/``, ``.cursor/skills/``, or ``.agents/skills/``.

Installation
------------
Copy the ``skills/`` directory from the
`astrodb_bot repository <https://github.com/astrodbtoolkit/astrodb_bot>`_ into the
location your AI reads skills from. For example, with Claude:

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
also be run on its own. Each one links to its full definition in the ``astrodb_bot``
repository.

#. `astrodb-parse-data-table <https://github.com/astrodbtoolkit/astrodb_bot/blob/main/skills/astrodb-parse-data-table/SKILL.md>`_
   — Reads a data table (FITS, CSV, ECSV, HDF5, VOTable, Parquet, Excel, ...) and
   summarizes every column's name, description, units, and type as a Markdown and HTML
   report.

#. `astrodb-match-schema <https://github.com/astrodbtoolkit/astrodb_bot/blob/main/skills/astrodb-match-schema/SKILL.md>`_
   — Maps each parsed column to a table and field in the AstroDB template schema,
   assigning a confidence level to every match and flagging anything it cannot place.

#. `astrodb-validate-schema-mapping <https://github.com/astrodbtoolkit/astrodb_bot/blob/main/skills/astrodb-validate-schema-mapping/SKILL.md>`_
   — Checks the proposed mapping against the actual data: null values landing in
   non-nullable fields, and type mismatches between the data and the schema.

#. `astrodb-generate-schema <https://github.com/astrodbtoolkit/astrodb_bot/blob/main/skills/astrodb-generate-schema/SKILL.md>`_
   — Turns the validated mapping into a Felis-format ``schema.yaml`` (see
   :doc:`modifying/yaml`) and runs ``felis validate`` on it.

#. `astrodb-create-db <https://github.com/astrodbtoolkit/astrodb_bot/blob/main/skills/astrodb-create-db/SKILL.md>`_
   — Creates an empty SQLite database from the validated ``schema.yaml``, following the
   `astrodb-template-db <https://github.com/astrodbtoolkit/astrodb-template-db>`_ file
   layout, and generates a matching test suite.

#. `astrodb-ingest-source <https://github.com/astrodbtoolkit/astrodb_bot/blob/main/skills/astrodb-ingest-source/SKILL.md>`_
   — Generates and runs a script that ingests sources from the data table into the new
   database using ``astrodb_utils.sources.ingest_source``. See also
   :doc:`../db_access/ingesting/getting_started_ingesting`.

Intermediate artifacts — the parsed-column report, the schema mapping, the generated
``schema.yaml``, and the ingest scripts — are written to a ``tmp/`` folder, so they
don't clutter your project and you can inspect each step.

Example and Prompt Advice
-------------------------

**We recommend starting in plan mode (Claude, Cursor, and Codex all have /plan.)** 
The example prompt given was:

    *Review your astro-db skills and create a plan to have a fully working database
    after going through* ``@NearbyGalaxies_Jan2021_PUBLIC.fits``

Plan mode tells the AI inspect the input FITS and propose a complete build plan
using all of the available skills. The output of this prompt was a populated ``LocalGroupDB.sqlite``.
Alternatively, you can also invoke the skills one at a time.


Advice for working with Claude
------------------------------
* **Give the AI the template as a reference.** Point it at the
  `astrodb-template-db <https://github.com/astrodbtoolkit/astrodb-template-db>`_
  repository, which contains example ``schema.yaml`` files and test suites for every
  template table. This helps the AI structure the new database and its tests.

* **Keep track of token usage.** The more tokens you use, the more expensive it is.
  Using a better model, an advisor AI, and higher effort settings will improve the result
  but also increase the cost.