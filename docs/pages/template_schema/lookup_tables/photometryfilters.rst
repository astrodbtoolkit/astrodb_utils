PhotometryFilters
##################

Notes
======
* Band names are listed at the `SVO filter profile service <http://svo2.cab.inta-csic.es/svo/theory/fps3/index.php?mode=browse&gname=Spitzer&asttype=>`_.

* UCDs are listed in the `IVOA controlled vocabulary <https://www.ivoa.net/documents/UCD1+/20200212/PEN-UCDlist-1.4-20200212.html#tth_sEcB>`_.
  Common ones for cool stars are:

  =============  =====================================
  UCD            Description
  =============  =====================================
  `em.opt.R`     Optical band between 600 and 750 nm
  `em.opt.I`     Optical band between 750 and 1000 nm
  `em.IR.J`      Infrared between 1.0 and 1.5 micron
  `em.IR.H`      Infrared between 1.5 and 2 micron 
  `em.IR.K`      Infrared between 2 and 3 micron 
  `em.IR.3-4um`	 Infrared between 3 and 4 micron
  `em.IR.4-8um`  Infrared between 4 and 8 micron
  =============  =====================================

.. seealso::

    :doc:`../data_tables/photometry`
        Documentation for the Photometry table

    :py:mod:`ingest_photometry_filter <astrodb_utils.photometry.ingest_photometry_filter>` 
        Function to ingest photometry filters

    :py:mod:`fetch_svo <astrodb_utils.photometry.fetch_svo>` 
        Function to fetch SVO filter profiles

    :py:mod:`assign_ucd <astrodb_utils.photometry.assign_ucd>` 
        Function to assign UCDs to photometry filters

Table documentation
====================
.. _source: https://github.com/astrodbtoolkit/astrodb-template-db/blob/main/docs/schema/PhotometryFilters.md

The below table is built directly from the schema and is
included here from the `astrodb-template-db` documentation: `source`_.


.. mdinclude:: ../astrodb-template-db/docs/schema/PhotometryFilters.md
