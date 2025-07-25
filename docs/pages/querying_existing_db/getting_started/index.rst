Getting started
===============

There are multiple ways to use existing databases
with the AstroDB Toolkit.

.. toctree::

  installation


Using Python
------------

To use the AstroDB Toolkit with Python, you need the database
located on your machine.
That likely entails cloning the database's repository or downloading
the database files directly.
Once you have the database files, you can access them using the
`astrodb-utils` package.

.. code-block:: python

    from astrodb-utils import load_astrodb

    # Load the database into a variable called `db`
    # and make a sqlite file
    db = load_astrodb("path/to/database.sqlite")

    # Print the available tables in the database
    for table in db.metadata.tables:
      print(table)

You might need to provide more variables to the
:py:func:`load_astrodb<astrodb_utils.utils.load_astrodb>` function,
depending on how your database is set up.

See the `AstrodbKit documentation <https://astrodbkit.readthedocs.io/en/latest/>`_
for more about how to query the database using Python.

Using a GUI
-----------

Once you have an SQLite database file, you can use a graphical user interface
(GUI) to explore and query the database.
These tools allow you to visually inspect the database schema, run SQL queries,
and view results without writing code.
There are many options available, such as:

- `DB Browser for SQLite <https://sqlitebrowser.org/>`_
- `SQLiteStudio <https://sqlitestudio.pl/>`_
