Creating a Database with AI Skills
==================================

`astrodb-bot <https://github.com/astrodbtoolkit/astrodb-bot>`_ provides a set of
**AI skills** that guide an assistant (Claude Code, Cursor, etc.) through building a
new database from a raw data table: parsing the table, mapping its
columns to the :doc:`AstroDB template schema
<../getting_started/template_schema/template_schema>`,
generating a Felis ``schema.yaml``,
and creating a populated ``DatabaseName.sqlite``.
There is also a skill for setting up a FastAPI web interface for browsing and
visualizing the database in a browser.

These skills automate the manual workflows described elsewhere
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
Clone the `astrodb-bot repository <https://github.com/astrodbtoolkit/astrodb-bot>`_
into a location independent of your database project.
Then, depending on your AI tool, point your AI to the ``skills/`` directory
with a symbolic link.
This is the recommended way to use the skills, because it allows you to pull
updates to the skills without having to re-copy them.

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


Starting in the directory
above your database project, the commands to set this up are:

.. code-block:: bash

    cd ../
    git clone https://github.com/astrodbtoolkit/astrodb-bot.git
    cd my_db
    mkdir -p .claude/skills
    ln -s "../../astrodb-bot/skills" .claude/skills


Example and Expected Output
---------------------------
An example prompt is:

    *Use the astrodb skills to
    create a plan to have a fully working database after going through*
    ``@NearbyGalaxies_Jan2021_PUBLIC.fits``

Plan mode tells the AI to inspect the input FITS and propose a complete build plan
using all of the available skills. The output of this prompt should be a
populated ``LocalGroupDB.sqlite`` database.
Alternatively, you can also invoke the skills one at a time.

These skills will write intermediate files to an ``astrodb-build-artifacts/`` folder
and might ask you for permission to write the initial drafts of those files.
We recommend you allow them to write the files, but this is not the time to
inspect the files. When the skill is done, it should give you links to the
rendered files and you can inspect them then and answer any questions the
AI has about them.

These skills have been built and optimized for Claude Code,
but they should work with any AI tool that can read the skill definitions and
follow the instructions.
Different AI tools have different strengths and weaknesses, so you might have
to experiment with the prompts to get the best results. If you have trouble
getting the skills to work, please post in the `discussion forum
<https://github.com/orgs/astrodbtoolkit/discussions>`_
or open an issue in the
`astrodb-bot issue tracker <https://github.com/astrodbtoolkit/astrodb-bot/issues>`_.


The Skills
----------
Specific skill descriptions are in the `astrodb-bot README.md
<https://github.com/astrodbtoolkit/astrodb-bot/blob/main/README.md>`_
