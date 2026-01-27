Querying
========

Create the Database
------------------------
To query an existing database, you first need to load it using the
load_db_from_json or **read_db_from_file** functions.

.. code-block:: python

    from astrodb_utils.loaders import read_db_from_file

    SAVE_DB = False  # save the data files in addition to modifying the .db file

    # LOAD THE DATABASE
    db = read_db_from_file(db_name = "SIMPLE")


Exploring the Schema
-------------------------
The AstroDB Toolkit makes extensive use of the Astrodbkit package.
Astrodbkit provides the Database class and useful methods for exploring the database.

The database schema is accessible via the **db.metadata** attribute after
loading the database.

Below is an example of how to load the database and print the available
tables from the schema.

.. code-block:: python

    for table in db.metadata.tables:
        print(table)

You can also explore the columns of a specific table.
For example, to view the first 10 columns in the `Sources` table:

.. code-block:: python

    db.query(db.Sources).limit(10).table()

Search Object function
-------------------------
The **search_object** method allows you to search for astronomical
objects in the database by name or identifier. It returns a list
of matching sources along with their details.

You can use fuzzy search and alternative names to search for objects
as well. You can also specify which table to search from.

.. code-block:: python

    #search by object name
    db.search_object("2MASS J03480772-6022270")
    #search by specifying table
    db.search_object("2MASS J03480772-6022270", table="Sources")

Inventory Search function
-------------------------
The **inventory_search** method returns all data for an object

.. code-block:: python

    data = db.inventory_search("2MASS J03480772-6022270", pretty_print = True)

String Search function
-------------------------
The **string_search** method allows you to search for objects that contain a specific string

.. code-block:: python

    #Search for objects that have 2MASS in their name
    db.string_search("2MASS")
    #Search for objects that have Burn13 as a reference
    db.string_search("Burn13", column="reference")

Query Region function
-------------------------
The **query_region** method allows you to search for objects
within a specified region.
It expects astropy SkyCoord and Quantity objects for the position and radius

.. code-block:: python

    coords_result = db.query_region(SkyCoord(ra = 57.0305*u.degree, dec = -60.3742*u.degree), radius=60.*u.arcsec)
    #Searching in the photometry table
    coords_result_photometry = db.query_region(SkyCoord(ra = 57.0305*u.degree, dec = -60.3742*u.degree), radius=60.*u.arcsec, table="Photometry")

.. seealso::
    `Querying Getting Started Demo <https://github.com/SIMPLE-AstroDB/SIMPLE-db/blob/main/docs/notebooks/Demo_Queries_1.0.ipynb>`_

    `Advanced Querying Demo <https://github.com/SIMPLE-AstroDB/SIMPLE-db/blob/main/docs/notebooks/Demo_Queries_1.5.ipynb>`_