Spectra
#######

.. seealso::

    :doc:`../lookup_tables/telescopes`
        Documentation for the Telescopes table

    :doc:`../lookup_tables/regimelist`
        Documentation for the RegimeList table`

    :py:mod:`check_spectrum_plottable<astrodb_utils.spectra.check_spectrum_plottable>`
        Function to check if a spectrum is plottable


Relevant functions: `spectra.ingest_spectrum`, `spectra.spectrum_plottable`, `spectra.find_spectra`

If the spectrum provided has been modified from the author-provided one, 
a link to the original spectrum can be provided in the `original_spectrum` column.

The local_spectrum is meant to store the path to a local copy of the spectrum with an 
environment variable to define part of the path (so it can be shared among other users). 
For example: `$ASTRODB_SPECTRA/infrared/filename.fits`

Notes
=====
* An accurate observation date is required for a spectrum to be ingested.
  
* Data based on data from multiple observation dates has 'Multiple observation dates' 
  indicated in the *comments* field. One of the dates should be used for the *observation_date*.

* Spectra for companions should be associated with individual sources and not grouped with the primary source.