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
   ├── my_table.fits
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
Work through the build one skill at a time rather than asking for everything
in a single prompt. Each step produces files you should review before moving on.
An example prompt to get started, using
``my_data.fits`` as the input table, is:

 *Use the astrodb-bot skills to start a new database called my_db using the data in ``@my_data.fits``

If the skills are installed correctly, the AI assistant should start with 
the ``astrodb-build-01-setup`` skill and step you through the several steps of
creating a new database project from the template.
After each step, read what the AI reports, answer its questions, and ask for
changes before asking it to continue.

These skills will write intermediate files to an ``astrodb-build-artifacts/`` folder
and might ask you for permission to write the initial drafts of those files.
We recommend you allow them to write the files, but this is not the time to
inspect the files. When the skill is done, it should give you links to the
rendered files and you can inspect them then and answer any questions the
AI has about them.

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


The Skills
----------
The skills are grouped by stage:

* **Build**: set up the database project, parse the input table, match and
  validate its columns against the template schema, generate ``schema.yaml``,
  create the database, and draw an entity relationship diagram.
* **Ingest**: add publications, sources, and photometry to the database.
* **Website**: set up a web interface for browsing and visualizing the database.

The set of skills is still changing. To see what is currently available, look in
the ``skills/`` folder of your ``astrodb-bot`` clone or ask your AI which AstroDB
skills it can use.
