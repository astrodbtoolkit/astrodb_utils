Creating a Database with AI Skills
==================================

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
------------
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
Clone the `astrodb_bot repository <https://github.com/astrodbtoolkit/astrodb_bot>`_
into a location independent of your database project.
Then, depending on your AI tool, point your AI to the ``skills/`` directory
with a symbolic link.
This is the recommended way to use the skills, because it allows you to pull
updates to the skills without having to copy them into every project.

Here is the recommended directory structure:

.. parsed-literal::

   **astrodb-bot/**
   └── skills/
      ├── astrodb-build-setup/
      ├── astrodb-build-schema-match/
      ├── astrodb-build-create-db/
      └── ... (other skill folders)
   my_db/
   └── **.claude/**
      └── **skills  ──symlink──>  ../../astrodb-bot/skills**
   ├── data/
   ├── docs/
   ├── my_db.sqlite
   ├── my_db.toml
   ├── schema.yaml
   └── ... (other astrodb files and folders)


The commands to set this up are, starting in the directory
above your database project:

.. code-block:: bash

    cd ../
    git clone https://github.com/astrodbtoolkit/astrodb_bot.git
    cd my_db
    mkdir -p .claude/skills
    ln -s "../../astrodb-bot/skills" .claude/skills


Example and Expected Output
---------------------------
An example prompt is:

    *Use the astrodb skills to
    create a plan to have a fully working database after going through*
    ``@NearbyGalaxies_Jan2021_PUBLIC.fits``

Plan mode tells the AI inspect the input FITS and propose a complete build plan
using all of the available skills. The output of this prompt should be a
populated ``LocalGroupDB.sqlite`` database.
Alternatively, you can also invoke the skills one at a time.

These skills will write intermediate files to an ``astrodb-build-artifacts/``
folder,
and might ask you for permission to write the initial drafts of those files.
We recommend you allow them to write the files, but this is not the time to
inspect the files. When the skill is done, it will give you links to the
rendered files and you can inspect them then and answer any questions the
AI has about them.

These skills have been built and optimized for Claude,
but they should work with any AI tool that can read the skill definitions and
follow the instructions.
Different AI tools have different strengths and weaknesses, so you might have
to experiment with the prompts to get the best results. If you have trouble
getting the skills to work, please open an issue in the
`astrodb_bot issue tracker <https://github.com/astrodbtoolkit/astrodb_bot/issues>`_.


The Skills
----------
Each one links to its full definition in the ``astrodb_bot`` repository.
The instructions in these skill documents are for your AI tool, not for you.

Build Skills
^^^^^^^^^^^^
These skills build a schema-validated SQLite database
based on a data table.
They are designed to run in sequence, but you can also run them one at a time.


#. `astrodb-build-setup <https://github.com/astrodbtoolkit/astrodb_bot/blob/main/skills/astrodb-build-setup/SKILL.md>`_
   — Sets up the environment for building a new database.
   Has the user clone the template repository and walks them through
   naming their database.

#. `astrodb-build-parse-table <https://github.com/astrodbtoolkit/astrodb_bot/blob/main/skills/astrodb-build-parse-table/SKILL.md>`_
   — Reads a data table (FITS, CSV, ECSV, HDF5, VOTable, Parquet, Excel, ...)
   and summarizes every column's name, description, units, and type as a
   Markdown and HTML report.

#. `astrodb-build-schema-match <https://github.com/astrodbtoolkit/astrodb_bot/blob/main/skills/astrodb-build-schema-match/SKILL.md>`_
   — Maps each parsed column to a table and field in the AstroDB
   template schema, assigning a confidence level to every match
   and flagging anything it cannot place.

#. `astrodb-build-schema-validate <https://github.com/astrodbtoolkit/astrodb_bot/blob/main/skills/astrodb-build-schema-validate/SKILL.md>`_
   — Checks the proposed mapping against the actual data: null values landing
   in non-nullable fields, and type mismatches between the data and the schema.

#. `astrodb-build-schema-generate <https://github.com/astrodbtoolkit/astrodb_bot/blob/main/skills/astrodb-build-schema-generate/SKILL.md>`_
   — Turns the validated mapping into a Felis-format ``schema.yaml`` (see
   :doc:`modifying/yaml`) and runs ``felis validate`` on it.

#. `astrodb-build-create-db <https://github.com/astrodbtoolkit/astrodb_bot/blob/main/skills/astrodb-build-create-db/SKILL.md>`_
   — Creates an empty SQLite database from the validated ``schema.yaml``,
   following the `astrodb-template-db <https://github.com/astrodbtoolkit/astrodb-template-db>`_ file
   layout, and generates a matching test suite.

Ingest Skills
^^^^^^^^^^^^^
These skills populate the database with data from source tables.

#. `astrodb-ingest-publications <https://github.com/astrodbtoolkit/astrodb_bot/blob/main/skills/astrodb-ingest-publications/SKILL.md>`_
   — Generates and runs a script that adds publications (references/citations)
   to the ``Publications`` lookup table using
   ``astrodb_utils.publications.ingest_publication``.
   Handles a single paper, a batch from a data file's reference column,
   or backfilling existing rows with missing metadata.
   Every reference used elsewhere in the database must exist here first.
   See also :doc:`../db_access/ingesting/ingesting_publications`.

#. `astrodb-ingest-sources <https://github.com/astrodbtoolkit/astrodb_bot/blob/main/skills/astrodb-ingest-sources/SKILL.md>`_
   — Generates and runs a script that ingests sources from the data table
   into the new database using ``astrodb_utils.sources.ingest_source``.
   See also
   :doc:`../db_access/ingesting/getting_started_ingesting`.

Website Skills
^^^^^^^^^^^^^^
These skills set up tools for browsing and visualizing the database
in a browser.

#. `astrodb-website <https://github.com/astrodbtoolkit/astrodb_bot/blob/main/skills/astrodb-website/SKILL.md>`_
   — Sets up and runs a FastAPI web interface
   for browsing and visualizing the database in a browser.
   Guides the user through creating a repo from the template
   (`astrodb-web <https://github.com/astrodbtoolkit/astrodb-web>`_),
   configuring the ``.env`` file, and starting the server.
