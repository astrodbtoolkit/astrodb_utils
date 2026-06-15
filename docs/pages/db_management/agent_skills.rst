Creating a Database with AI Skills
========================================

`astrodb_bot <https://github.com/astrodbtoolkit/astrodb_bot>`_ provides a set of
**AI skills** that guide an assistant (Claude, Cursor, etc.) through building a
new database from a raw data table: parsing the table, mapping its
columns to the :doc:`AstroDB template schema
<../getting_started/template_schema/template_schema>`,
generating a Felis ``schema.yaml``,
and will creating a populated ``DatabaseName.sqlite``.

These skills automate the manual workflow described elsewhere
in this documentation
(:doc:`make_new_db/index` and :doc:`modifying/index`).

.. note::

   The skills require an AI **skill runner**: an AI tool that reads a ``skills/``
   directory such as ``.claude/skills/``, ``.cursor/skills/``, or ``.agents/skills/``.

Requirements
~~~~~~~~~~~~~
Make sure you are in an environment where the latest versions
of the following packages are installed and available to your AI:

* Python 3.11 or greater
* ``uv`` or ``pip`` to install Python packages
* ``astropy``, ``pandas``, ``lsst-felis``, ``astrodbkit``,
  and ``astrodb_utils``

.. code-block:: bash

    pip install --upgrade astropy pandas lsst-felis astrodbkit astrodb_utils


Installation
------------
Copy the ``skills/`` directory from the
`astrodb_bot repository <https://github.com/astrodbtoolkit/astrodb_bot>`_ into the
location your AI reads skills from. For example, with Claude:

.. code-block:: bash

    git clone https://github.com/astrodbtoolkit/astrodb_bot.git
    mkdir -p .claude/skills
    cp -r astrodb_bot/skills/* .claude/skills/


Example and Prompt Advice
-------------------------
An example prompt is:

    *Use the skills in the astrodb_bot directory and
    create a plan to have a fully working database after going through*
    ``@NearbyGalaxies_Jan2021_PUBLIC.fits``

Plan mode tells the AI inspect the input FITS and propose a complete build plan
using all of the available skills. The output of this prompt was a populated
``LocalGroupDB.sqlite``.
Alternatively, you can also invoke the skills one at a time.

These skills will write intermediate files to a ``tmp/`` folder, and might
ask you for permission to write the initial drafts of those files.
We recommend you allow them to write the files, but this is not the time to
inspect the files. When the skill is done, it will give you links to the
rendered files and you can inspect them then and answer any questions the
AI has about them.

The Skills
----------
The skills are designed to run in sequence, each feeding the next,
but any of them can also be run on its own. Each one links to its
full definition in the ``astrodb_bot`` repository.
The instructions in these skill documents are for your AI tool, not for you.

#. `astrodb-setup <https://github.com/astrodbtoolkit/astrodb_bot/blob/main/skills/astrodb-setup/SKILL.md>`_
   — Sets up the environment for building a new database.
   Has the user clone the template repository and walks them through
   naming their database.

#. `astrodb-parse-data-table <https://github.com/astrodbtoolkit/astrodb_bot/blob/main/skills/astrodb-parse-data-table/SKILL.md>`_
   — Reads a data table (FITS, CSV, ECSV, HDF5, VOTable, Parquet, Excel, ...)
   and summarizes every column's name, description, units, and type as a
   Markdown and HTML report.

#. `astrodb-match-schema <https://github.com/astrodbtoolkit/astrodb_bot/blob/main/skills/astrodb-match-schema/SKILL.md>`_
   — Maps each parsed column to a table and field in the AstroDB
   template schema, assigning a confidence level to every match
   and flagging anything it cannot place.

#. `astrodb-validate-schema-mapping <https://github.com/astrodbtoolkit/astrodb_bot/blob/main/skills/astrodb-validate-schema-mapping/SKILL.md>`_
   — Checks the proposed mapping against the actual data: null values landing
   in non-nullable fields, and type mismatches between the data and the schema.

#. `astrodb-generate-schema <https://github.com/astrodbtoolkit/astrodb_bot/blob/main/skills/astrodb-generate-schema/SKILL.md>`_
   — Turns the validated mapping into a Felis-format ``schema.yaml`` (see
   :doc:`modifying/yaml`) and runs ``felis validate`` on it.

#. `astrodb-create-db <https://github.com/astrodbtoolkit/astrodb_bot/blob/main/skills/astrodb-create-db/SKILL.md>`_
   — Creates an empty SQLite database from the validated ``schema.yaml``,
   following the `astrodb-template-db <https://github.com/astrodbtoolkit/astrodb-template-db>`_ file
   layout, and generates a matching test suite.

#. `astrodb-ingest-publication <https://github.com/astrodbtoolkit/astrodb_bot/blob/main/skills/astrodb-ingest-publication/SKILL.md>`_
   — Generates and runs a script that adds publications (references/citations) to the
   ``Publications`` lookup table using ``astrodb_utils.publications.ingest_publication``.
   Handles a single paper, a batch from a data file's reference column, or backfilling
   existing rows with missing metadata. Every reference used elsewhere in the database
   must exist here first. See also :doc:`../db_access/ingesting/ingesting_publications`.

#. `astrodb-ingest-source <https://github.com/astrodbtoolkit/astrodb_bot/blob/main/skills/astrodb-ingest-source/SKILL.md>`_
   — Generates and runs a script that ingests sources from the data table
   into the new database using ``astrodb_utils.sources.ingest_source``.
   See also
   :doc:`../db_access/ingesting/getting_started_ingesting`.

Intermediate artifacts — the parsed-column report, the schema mapping,
the generated ``schema.yaml``, and the ingest scripts — are written
to a ``tmp/`` folder, so they don't clutter your project and
you can inspect each step.


Advice for working with Claude
------------------------------
* **Keep track of token usage.** The more tokens you use,
  the more expensive it is.
  Using a better model, an advisor AI, and higher effort settings
  will improve the result but also increase the cost.
* **Use plan mode.** This allows the AI to inspect the input data
  and propose a complete build plan using all of the available skills.
