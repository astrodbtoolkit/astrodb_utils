Adding columns to tables with existing data
===========================================

If a table already contains data and you want to add new columns,
follow these steps:

1. Load the database and data as-is
   - Python: create a Database object and .sqlite file using `astrodb_utils`
   - DBBrowser: Open the SQLite database file
2. Modify the tables/columns
   - Python: Use `ALTER TABLE` commands to add new columns
     or modify existing ones.
   - DBBrowser: Use the GUI to add columns or modify existing ones.
3. Use `astrodbkit.save_database` to write the modified database to JSON files
4. Make the modifications to the Felis schema yaml file
5. Reload the database
6. There's an old example here: https://github.com/SIMPLE-AstroDB/SIMPLE-db/blob/main/scripts/updates/update_spectra_colnames.py
