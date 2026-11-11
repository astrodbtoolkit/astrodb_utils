Creating a Database with AI Skills
==================================

`astrodb-bot <https://github.com/astrodbtoolkit/astrodb-bot>`_ provides a set of
**AI skills** that guide an assistant (Claude Code, Cursor, etc.) through building a
new database from a raw data table: setting up a new database project from the
`AstroDB template <https://github.com/astrodbtoolkit/astrodb-template-db>`_,
parsing the table, mapping its
columns to the :doc:`AstroDB template schema
<../getting_started/template_schema/template_schema>`,
generating a Felis ``schema.yaml``,
and creating an empty ``DatabaseName.sqlite``.
Other skills ingest publications, sources, and photometry into the database,
and set up a FastAPI web interface for browsing and
visualizing the database in a browser.
The set of skills is under active development; see the
`astrodb-bot repository <https://github.com/astrodbtoolkit/astrodb-bot>`_
for the current list.

These skills automate the manual workflows described elsewhere
in this documentation
(:doc:`make_new_db/index` and :doc:`modifying/index`).

.. note::

   The skills require an AI **skill runner**: an AI tool that reads a ``skills/``
   directory such as ``.claude/skills/``, ``.cursor/skills/``, or ``.agents/skills/``.

.. admonition:: Recommended settings

   * **Mode:** Use *Manual* (ask before each action) or *Auto*. Do **not** use
     *Plan* mode: the skills already walk through a plan-like sequence of steps
     and ask you to review the results along the way.
   * **Effort:** Use *Low* effort. This makes the AI ask you more questions and
     make fewer assumptions about your data.
   * **Work one step at a time.** Run one skill, review its output, and then move
     on to the next (see :ref:`agent-skills-example`).

Requirements
------------

#. **Packages**

   Make sure you are in an environment where the latest versions
   of the following applications and packages are installed and available to your AI:

   * Python 3.13 or greater
   * ``pip`` to install Python packages
   * ``git``
   * ``astropy``, ``pandas``, ``lsst-felis``, ``astrodbkit``, ``astrodb_utils``, and ``pytest``

   .. code-block:: bash

      pip install --upgrade astropy pandas lsst-felis astrodbkit astrodb_utils pytest

#. **GitHub Account**

   You will also need a GitHub account.
   The AstroDB Toolkit was designed to use a GitHub workflow for hosting and collaboration.

   The first skill (astrodb-build-01-setup) asks you to create a new
   repository for your database from the
   `astrodb-template-db <https://github.com/astrodbtoolkit/astrodb-template-db>`_
   template ("Use this template" button), and it takes care of cloning it for you.


Installation
------------
Because the first skill creates your database project, set up the skills in a
**workspace folder** that is separate from (and above) your database project.
Clone the `astrodb-bot repository <https://github.com/astrodbtoolkit/astrodb-bot>`_
next to that workspace folder,
and then, depending on your AI tool, point your AI to the ``skills/`` directory
with a symbolic link.
This is the recommended way to use the skills, because it allows you to pull
updates to the skills without having to re-copy them.

Here is the recommended directory structure:

.. parsed-literal::

   **astrodb-bot/**
   └── skills/
      ├── astrodb-build-01-setup/
      ├── astrodb-build-02-parse-table/
      ├── astrodb-build-03-schema-match/
      └── ... (other skill folders)
   my_workspace/
   ├── **.claude/**
   │   └── **skills  ──symlink──>  ../../astrodb-bot/skills**
   ├── my_datatable.csv
   └── my_db/   (created by the astrodb-build-01-setup skill)
       ├── data/
       ├── docs/
       ├── database.toml
       ├── schema.yaml
       ├── astrodb-build-artifacts/
       └── ... (other astrodb files and folders)


Starting in the folder that contains your workspace folder,
the commands to set this up are:

.. code-block:: bash

    git clone https://github.com/astrodbtoolkit/astrodb-bot.git
    mkdir my_workspace
    cd my_workspace
    mkdir .claude
    ln -s ../../astrodb-bot/skills .claude/skills

Then start your AI tool from inside ``my_workspace`` and keep working from there:
the ``astrodb-build-01-setup`` skill will create the ``my_db`` folder inside it.


.. _agent-skills-example:

Example and Expected Output
---------------------------
Expect to work through the build one skill at a time rather than getting a complete database
from a single prompt. Each step produces files and questions that you should review before moving on.
An example prompt to get started, using
``my_datatable.csv`` as the input table, is:

    *Use the astrodb-bot skills to start a new database called my_db using the data in*
    ``@my_datatable.csv``

If the skills are installed correctly, the AI assistant should start with
the ``astrodb-build-01-setup`` skill and step you through the several steps of
creating a new database project from the template.
After each step, read what the AI reports, answer its questions, and ask for
changes before asking it to continue.

If you already have a directions file (see below), add it to the prompt, for example:
*"...and my directions are in* ``@my_directions.md`` *"*.

These skills will write intermediate files to an ``astrodb-build-artifacts/`` folder
and might ask you for permission to write the initial drafts of those files.
We recommend you allow them to write the files, but this is not the time to
inspect the files. When the skill is done, it should give you links to the
rendered files and you can inspect them then and answer any questions the
AI assistant has about them.

The end result of this sequence is a ``my_db`` database project with its schema
and an empty SQLite database. The ingest skills then fill it with your data
(for example, "ingest the publications", then "ingest the sources").

These skills have been built and optimized for Claude Code,
but they should work with any AI tool that can read the skill definitions and
follow the instructions.
Different AI tools have different strengths and weaknesses, so you might have
to experiment with the prompts to get the best results. If you have trouble
getting the skills to work, please post in the `discussion forum
<https://github.com/orgs/astrodbtoolkit/discussions>`_
or open an issue in the
`astrodb-bot issue tracker <https://github.com/astrodbtoolkit/astrodb-bot/issues>`_.


The Directions File
-------------------
The ``directions.md`` file is an optional markdown file where you write down what you
already know about your data and the decisions you have made, *before* the AI
starts asking questions.
If you don't provide one, the ``astrodb-build-01-setup`` skill creates it, and the
skills ask you questions about your data and record your
decisions in ``astrodb-build-artifacts/directions.md`` as you go.

Every build skill reads it, so anything you record there is
something you do not have to answer again, and the AI is less likely to guess.

You can provide it in either of two ways:

* **Give the AI a path** when you start, as in the example above. The
  ``astrodb-build-01-setup`` skill copies it to
  ``my_db/astrodb-build-artifacts/directions.md``, where all later skills look for it.
* **Write it as you go.** If you don't provide one, the setup skill shows you an
  example and offers to help you write one. You can also create or edit
  ``astrodb-build-artifacts/directions.md`` yourself at any point, and
  the skills will pick up your changes.

A directions file can contain, for example:

* **Database**: the name (which becomes ``db_name`` in ``database.toml`` and names
  the ``.sqlite`` file) and a description used in the README.
* **License**: the license and copyright holder(s) for the database.
* **Data overview**: what each row of your table represents and which file holds what.
* **Column handling**: which columns go into which tables, and which to ignore.
* **Source matching**: how to match your objects to existing sources.
* **Schema notes, known issues, and open questions.**

Include only what you know. For anything you leave out, the skills ask you.
Skills tell you which values they took from the file, so you can check them.
Here is a short example:

.. code-block:: markdown

   # Directions

   ## Database
   - **Name**: `StreamDB`
   - **Description**: A catalog of stellar stream members with metallicities
     and membership probabilities.

   ## License
   - **License**: BSD 3-Clause
   - **Copyright holder(s)**: Jane Astronomer, 2026

   ## Column Handling
   - `Feh` and `AFe`: ingest into the `ModeledParameters` table
   - Ignore `x`, `y`, `z` in the main source table

The skills also add to this file as decisions are made, so treat it as a record that
you keep up to date. The bot repository has a longer example at
`directions_example.md
<https://github.com/astrodbtoolkit/astrodb-bot/blob/main/skills/astrodb-build-01-setup/references/directions_example.md>`_.


Expect to Build More Than Once
------------------------------
You will most likely build your database more than once. Your first pass will
turn up columns that were mapped to the wrong place, schema choices you want to
change, or questions you didn't know to answer. That is normal and is part of the process.

To make this easy:

* **Add a version suffix to the database name**, such as ``my_db_v1``,
  ``my_db_v2``, and so on. Each attempt then gets its own GitHub repository
  (the setup skill suggests giving the repository the same name as the database) and
  its own folder, so you can compare versions and never overwrite one you want
  to keep.
* **Keep your directions file.** Copy the ``directions.md`` from
  your previous attempt and give its path when you start the next one. The
  decisions you recorded carry over, and what you learned about the data is not lost.
* **Keep the artifacts.** The ``astrodb-build-artifacts/`` folder in each version
  records what was decided and why.

Once you are satisfied with a version, you can drop the suffix for the
final, published database. If you do, rename the GitHub repository and the folder, and
update ``db_name`` in ``database.toml`` so that the ``.sqlite`` file gets the new name too.


What You'll Have at the End
---------------------------
After working through the build skills, your database project contains:

* ``schema.yaml``: the Felis description of your database schema.
* ``database.toml``: the settings file for your database.
* ``data/``: the JSON files that hold your data. These are the source of truth.
* ``my_db.sqlite``: the SQLite database built from the schema (and your data,
  once you have run the ingest skills).
  This file can be rebuilt at any time and does not need to be tracked in git.
* ``docs/``: documentation of your schema, including an entity relationship diagram.
* ``astrodb-build-artifacts/``: the intermediate files written by the skills
  (table summaries, column mappings, validation notes). Keep these as a record
  of the decisions made while building your database.

All of this lives in the git repository you created from the template,
so you can commit it and share it.
