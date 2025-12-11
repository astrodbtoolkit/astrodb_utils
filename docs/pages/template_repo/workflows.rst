Workflows and Magic
===================

There are several GitHub Action workflows setup that automate various tasks:

* Tests

* Making new entity relationship diagram (ERD)

* Generating a new database file

Tests
-----

There are actions setup to run three different kinds of tests

Database Tests
^^^^^^^^^^^^^^
* **Workflow file:** `.github/workflows/run_tests.yml`

The database tests run on every pull request to check the integrity of the
database contents and schema. These are tests which will need to change as
the database contents and schema change. These tests are located in the
`tests/` directory.

Test against `astrodb_utils`
^^^^^^^^^^^^^^^^^^^^^^^^^^^^
* **Workflow file:** `.github/workflows/run_astrodb_utils.yml`

This workflow installs the latest version of astrodb-utils and run its tests
against the database in this repository.

.. error::
    This workflow is currently setup to only work for databases named `astrodb-template-db`.
    `Issue 187 <https://github.com/astrodbtoolkit/astrodb-template-db/issues/187>`_
    tracks updating this workflow to work for any database.


Run tests that take a long time on a schedule 
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
* **Workflow file:** `.github/workflows/run_scheduled_tests.yml`
* **Python script:** `tests/scheduled_checks.py`

There are some tests that take a long time to run. For example, checking
that every URL is valid and checking every name against SIMBAD. This workflow
runs those tests once a month. These tests are written in the
`tests/scheduled_checks.py` file.


Entitiy Relationship diagram (ERD) generation
---------------------------------------------
* **Workflow file:** `.github/workflows/make_erd.yml`
* **Python script:** `scripts/make_schema_erd.py`

On every merge to the main branch,
the make_erd.yml GitHub Action workflow will run.
This runs the scripts/make_schema_erd.py script
to generate an updated entity relationship diagram (ERD)
based on the current state of the database schema.
It adds the new ERD image to docs/figures/schema_erd.png
and commits the change to the main branch.

Database generation
-------------------
* **Workflow file:** `.github/workflows/generate_db.yml`
* **Bash command** : `build_db_from_json`

When you make a new release (by creating a GitHub release),
this workflow will automatically create a new SQLite database file and append
the version number to the database file name.
This database is also added to the current release.

This workflow can also be run manually from the Actions tab
on GitHub by selecting the "Generate database" workflow
and clicking the "Run workflow" button. It will not append a version number
if run this way, but will commit the generated database file to the
current branch.