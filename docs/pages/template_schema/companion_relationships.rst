Companion Relationships
=========================

.. mdinclude:: https://github.com/astrodbtoolkit/astrodb-template-db/blob/main/docs/schema/CompanionParameters.md


Notes
-----
Relationship types are not currently constrained but should be one of the following:

* *parent*: The source is higher mass/brighter than the companion
* *sibling*: The source is similar to the companion in the system heirarchy 
* *child*: The source is lower mass/fainter than the companion
* *unresolved parent*: The source is the unresolved, combined light source of an unresolved multiple system which includes the companion