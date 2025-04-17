Sources
#######

Sources are the objects that are the focus of the database. They can be stars, galaxies, or other celestial objects. 
The Sources table contains information about the sources, including their coordinates and discovery reference.
The Sources table is the main table in the database and is used to link all other tables together. 
Each source has a unique identifier, which is used to link it to other tables in the database.


Notes
-----
* Epoch is the date the source is expected to be at the given coordinate. 
  This date is most relevant for high proper option objects.
* In the case of multiple discovery references, for example independent discovery, choose one
  reference for the `reference` column and put the rest in the `other_references` column.


Table documentation
-------------------

.. mdinclude:: ../../../../astrodb-template-db/docs/schema/Sources.md

