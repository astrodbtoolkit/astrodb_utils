Modifying the schema
======================

The template database comes with an existing schema, consisting of a set of tables and columns.
It is expected that every usecase will modify this schema to suit their needs.
However, it is important to follow some guidelines to ensure that the database remains functional with the rest of the Toolkit.

To add tables, columns, or modify existing columns, you will need to modify the schema file.
We use the `Felis package <https://felis.lsst.io/user-guide/intro.html>`_ to manage the database schema.
Modify the ``schema/schema.yaml`` file to reflect the changes you want to make. 
The `Felis Data Model documentation <Felis documentation>`_ provides a detailed guide on how to represent the schema file.


Required tables
----------------
There are several tables which are expected by ``astrodb_utils`` and should be modified with great care: 

* Sources 
* Names
* Publications
* Versions
* Telescopes
* Instruments

Optional tables
----------------
Optional tables are things like Spectra, Photometry, Radial Velocities, etc. 
These are included in the template database and can be used as models for other data tables and can be removed/modified if not needed.



Philosophy and guidelines
---------------------

We encourage users to follow the detailed best practices for astronomical databases outlined in `Chen et al. 2022 <https://iopscience.iop.org/article/10.3847/1538-4365/ac6268>`_.


Long vs Wide tables
~~~~~~~~~~~~~~~~~~~~
Think carefully about the structure of your tables.
TODO: Need an example


Column names
~~~~~~~~~~~~~~~~~~~~
* **Use lowercase column names.** This is a convention.
* **Include units in the column name.** Since we do not have a way of storing Quantities in the database, 
  we recommend including the units in the column name. 
  For example, instead of ``ra`` and ``dec``, use ``ra_deg``, ``dec_deg``. 
  While units are also included in the documentation of the schema, 
  including them in the column name increases their visibility to the user.
  

Units
---------------------------
Per `Chen et al. 2022 <https://iopscience.iop.org/article/10.3847/1538-4365/ac6268>`_, we explicitly define the units
for each table in their name (e.g., in the `Sources` table, the column with Right Ascension values
is named `ra_deg`). Doing so removes unit ambiguity when querying and modifying the database.

Some tables have a dedicated column for units, such as the `ModeledParameters` table. 
These columns expect strings which are resolvable as `Astropy units <https://docs.astropy.org/en/stable/units/index.html>`_.