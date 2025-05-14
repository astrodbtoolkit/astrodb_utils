Spectra
#######

.. toctree::
    :glob:
    :maxdepth: 2
    :titlesonly:

    converting_spectra/*


Check if spectra are plottable
------------------------------

Use the :py:mod:`check_spectrum_plottable<astrodb_utils.spectra.check_spectrum_plottable>` function 
to check if a spectrum is loadable by `astropy.specutils` and plottable.
The `matplotlib` package needs to be installed to display the spectrum using `show_plot=True`.

.. code-block:: python
   from astrodb_utils.spectra import check_spectrum_plottable
   file = <path to file>
   plottable = check_spectrum_plottable(file, show_plot=True)
   print plottable
   
   > True
