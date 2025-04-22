Converting Spectra
====================================
Spectral data can be stored in a variety of formats, including FITS files, ASCII files, and other formats.  
We recommend converting all spectra to FITS files that are readable by `specutils <https://specutils.readthedocs.io/en/stable/>`_ before ingestion into the database.  
This will ensure that the data (and metadata) are stored in a consistent format and that the data can be easily accessed and visualized.


How to convert spectra 
-------------------------
To convert a spectrum into a specutils-readable FITS file, get the data into Python arrays. 
Add units to those arrays to create Quantity arrays. 
Use the Quantity arrays to create a `specutils.Spectrum` object. 
(`Spectrum1D` in `specutils` earlier than v2.0.)
Create or modify the header of the FITS file to include the necessary metadata in the `Spectrum.meta` attribute.
Then save the spectrum to a FITS file using the `specutils.Spectrum.write`` method.

Here's a basic outline of the steps to convert a spectrum to the `specutils` `tabular-fits`` format:

.. code-block:: python

    import astropy.units as u
    from astropy.io.fits import getheader
    from specutils import Spectrum
    from astrodb_utils.spectra import check_spectrum_plottable
    

    # Read in the data
    wave, flux, err = read_data(<filename>)

    # Read in the header
    header = getheader(<filename>)

    # Create the Spectrum object
    converted_spectrum = Spectrum(
        spectral_axis=wave * u.um, 
        flux=flux * u.Jy, 
        uncertainty=err * u.Jy
    )
    converted_spectrum.meta["header"] = header

    # Write the Spectrum object to a FITS file
    converted_spectrum.write(<new_filename>, format="tabular-fits")

    # Check that the spectrum is readable and plottable
    # If you have matplotlib installed, use show_plot = True to display the spectrum
    check_spectrum_plottable(<new_filename>, show_plot=True)


Creating or modifying a FITS header
------------------------------------   
Oftentimes, the FITS header of a spectrum file will need to be modified or created from scratch.
`astrodb_utils.fits` includes several functions to help with this task.

- :doc:`fits_header_scratch`
- :doc:`fits_header_modify`


API documentation
-----------------
:py:mod:`astrodb_utils.spectra`
:py:mod:`astrodb_utils.fits`
