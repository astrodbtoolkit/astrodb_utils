New Columns
===========


Column names
------------
* **Use lowercase column names.** This is a convention.
* **Include units in the column name.**
  Since we do not have a way of storing Quantities in the database,
  we recommend including the units in the column name.
  For example, instead of ``ra`` and ``dec``, use ``ra_deg``, ``dec_deg``.
  While units are also included in the documentation of the schema,
  including them in the column name increases their visibility to the user.


Units
~~~~~

Per `Chen et al. 2022 <https://iopscience.iop.org/article/10.3847/1538-4365/ac6268>`_,
we explicitly define the units for each column in their name
(e.g., in the `Sources` table, the column with Right Ascension values
is named `ra_deg`).
Doing so removes unit ambiguity when querying and modifying the database.

Some tables have a dedicated column for units,
such as the `ModeledParameters` table.
These columns expect strings which are resolvable as
`Astropy units <https://docs.astropy.org/en/stable/units/index.html>`_.



Adding columns to tables with existing data
-------------------------------------------

If a table already contains data and you want to add new columns,
follow these steps:

1. Load the database and data as-is

   * **Python:** create a Database object and .sqlite file using
     `astrodb_utils`
   * **DBBrowser:** Open the SQLite database file

2. Modify the tables/columns

   * **Python:** Use `ALTER TABLE` commands to add new columns
     or modify existing ones.
   * **DBBrowser:** Use the GUI to add columns or modify existing ones.

3. Use `astrodbkit.save_database` to write the modified database to JSON files

4. Make the modifications to the Felis schema yaml file: :doc:`yaml`

5. Reload the database

.. seealso::
   Old example using Python: https://github.com/SIMPLE-AstroDB/SIMPLE-db/blob/main/scripts/updates/update_spectra_colnames.py

