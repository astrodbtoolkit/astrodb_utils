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

Example: building a Local Group galaxy database
-----------------------------------------------
The following condensed walkthrough shows the skills used end to end in a real
Claude Code session that built a database from McConnachie's *Nearby Galaxies*
catalog (``NearbyGalaxies_Jan2021_PUBLIC.fits`` — 144 Local Group dwarf galaxies).

**Setting up the session.** A few Claude Code slash commands configured the run
before any work began:

.. code-block:: text

    /effort ultracode    # maximum reasoning effort + dynamic workflow orchestration
    /model               # Opus 4.8 (1M context)
    /advisor             # route review checkpoints to a second Opus 4.8 reviewer
    /plan                # enter plan mode to scope the whole build before any changes

The ``/plan`` prompt was simply *"Review your astro-db skills and create a plan to
have a fully working database after going through @NearbyGalaxies_Jan2021_PUBLIC.fits"*.
Plan mode let the agent inspect the FITS file and propose a complete build plan for
approval *before* touching anything — surfacing up front that the catalog stores
RA/Dec as sexagesimal strings and hides missing values behind a ``999`` sentinel,
both of which had to be handled before ingest.

**Running the pipeline.** With the plan approved, the skills ran in sequence, each
feeding the next:

#. **astrodb-parse-data-table** — parsed all 50 columns (names, units, descriptions).
#. **astrodb-match-schema** — mapped 50 / 50 columns (0 unmatched) onto ``Sources``,
   ``RadialVelocities``, ``ProperMotions``, ``Photometry``, ``Morphology``, and
   ``ModeledParameters``.
#. **astrodb-generate-schema** / **astrodb-validate-schema-mapping** — produced the
   Felis ``schema.yaml`` (``felis validate`` passing) and confirmed 0 nullable
   violations and 0 type mismatches against the real data.
#. **astrodb-create-db** — created ``LocalGroupDB.sqlite`` and a matching test suite.
#. **astrodb-ingest-source** — ingested all 144 galaxies as sources, plus their
   measurements (129 radial velocities, 65 proper motions, 142 V-band magnitudes,
   137 morphologies, 889 modeled parameters).

Real catalogs need adaptation: the data forced a custom cleaning pass (sexagesimal →
decimal coordinates, ``999`` → null) and a few ORM inserts where no skill helper
existed. The skills are the scaffold for the workflow, not a single turnkey button.

**Review checkpoints with the advisor.** Because ``/advisor`` was enabled, a second
Opus 4.8 model reviewed the work at key points. Its most useful catch: counts and
coordinates had been verified, but individual measurement *values* had not — a
swapped error column would still pass every count test. Acting on that, the agent
spot-checked a galaxy with *asymmetric* errors (Columba I) and confirmed
``vh+`` → ``rv_error_upper`` and ``vh-`` → ``rv_error_lower`` were not swapped.

**Result.** A populated ``LocalGroupDB.sqlite`` with all 144 sources and their
measurements, 16 / 16 pytest tests passing, and a clean reload from the saved JSON.
A second ``/plan`` was used later in the same session to resolve the catalog's
numbered footnote references against its bibliography file.
