Modifying the schema
======================

The template database comes with an existing schema, consisting of a set of tables and columns.
It is expected that every usecase will modify this schema to suit their needs.
However, it is important to follow some guidelines to ensure that the database remains functional with the rest of the toolkit.

There are reference tables that should not be modified, such as the ``sources`` table.
Expected tables include Sources, Publications, and Versions

Optional tables are things like Spectra, Photometry, Radial Velocities, etc. 
These are included in the template database and can be used as models for other data tables and can be removed/modified if not needed.

To add tables, columns, or modify existing columns, you will need to modify the schema file.
We use the `Felis package <https://felis.lsst.io/user-guide/intro.html>`_ to manage the database schema.
Modify the ``schema/schema.yaml`` file to reflect the changes you want to make. 
The `Felis Data Model documentation <Felis documentation>`_ provides a detailed guide on how to represent the schema file.
