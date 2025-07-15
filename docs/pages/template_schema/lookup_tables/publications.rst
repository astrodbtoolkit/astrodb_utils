Publications
############

Notes
-----
* `Reference` is typically a six letter string consisting of first four letters of first author name and two digit year. 
 
  * Smith et al. 2020 would be `Smit20`.
  
  * In the case of short last names, either first letters of first name or underscores can be used to construct the four letter string. For example, `WuXi21` or `Wu__21`

  * In the case of multiple publications in the same year, a short string is appended which corresponds to the 
    last digits of the DOI or Bibcode. For example, `Smit20.123`. Avoid using `abc` suffixes.

.. seealso::

    :ref:`ingesting_publications`
        Documenation on ingesting publications 

    :py:mod:`ingest_publication <astrodb_utils.publications.ingest_publication>`
        Function to ingest publication data

    :py:mod:`find publication <astrodb_utils.publications.find_publication>`
        Function to find publications in the database


Table documentation
-------------------

.. mdinclude:: ../astrodb-template-db/docs/schema/Publications.md


