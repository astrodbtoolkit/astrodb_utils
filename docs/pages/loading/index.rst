Building and Opening Existing Databases
=======================================

There are multiple ways to use existing databases
with the AstroDB Toolkit.

Using Python
------------

To use the AstroDB Toolkit with Python, you need the database
located on your machine.
That likely entails cloning the database's repository or downloading
the database files directly.

Once you have the database files, you can access them using the
`astrodb-utils` package. To load the database, the relevant functions
are in the :py:mod:`loaders<astrodb_utils.loaders>` module.
These functions use the database settings file (TOML format) to
create an SQLite database file and load the database into Python.

.. code-block:: python

    from astrodb-utils import build_db_from_json

    # Load the database into a variable called `db`
    # and make a sqlite file
    db = build_db_from_json(settings_file = "path/to/database.toml")

    # Print the available tables in the database
    for table in db.metadata.tables:
      print(table)

You might need to provide more variables to the
:py:func:`build_db_from_json<astrodb_utils.loaders.build_db_from_json>` function,
depending on how your database is set up.

If you already have a database file (SQLite format), you can load it
directly using the :py:func:`read_db_from_file<astrodb_utils.loaders.read_db_from_file>` function.

See the `AstrodbKit documentation <https://astrodbkit.readthedocs.io/en/latest/>`_
for more about how to query the database using Python.

Using the Command-Line
----------------------

You can also build an SQLite database from JSON files using the
``build_db_from_json`` command-line script. This is useful for
creating or updating databases without writing Python code.

Basic Usage
^^^^^^^^^^^

The simplest way to build the database is to use the ``build_db_from_json``
command:

.. code-block:: bash

   build_db_from_json

This command will:

* Read the database configuration from ``database.toml``
* Create a new SQLite database file using the JSON data files

For detailed information about all available options, examples, and
troubleshooting, see the :doc:`command_line` page.

Using a GUI
-----------

Once you have an SQLite database file, you can use a graphical user interface
(GUI) to explore and query the database.
These tools allow you to visually inspect the database schema, run SQL queries,
and view results without writing code.
There are many options available, such as:

- `DB Browser for SQLite <https://sqlitebrowser.org/>`_
- `SQLiteStudio <https://sqlitestudio.pl/>`_
