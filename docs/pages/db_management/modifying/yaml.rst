Edit the schema YAML file
=========================
To add tables, columns, or modify existing columns, you will need to modify the schema file.
We use the `Felis package <https://felis.lsst.io/user-guide/intro.html>`_
to manage the database schema.
Modify the ``schema/schema.yaml`` file to reflect the changes you want to make.
The `Felis Data Model documentation <Felis documentation>`_
provides a detailed guide on how to represent the schema file.

We highly recommend using an AI coding assistant (like GitHub Copilot) when modifying this file.

Order matters.
When modifying the schema YAML file, it is important to pay attention to the order of table definitions.
The lookup tables must be defined before any table that uses them.