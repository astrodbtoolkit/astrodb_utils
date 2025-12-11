Querying
========

Example SQL Query
-----------------
This query finds all of the near-infrared (NIR) spectra and their
corresponding spectral types from the database:

.. code-block:: sql

    SELECT * from Sources
    JOIN Spectra ON Sources.source = Spectra.source
    JOIN SpectralTypes ON Sources.source = SpectralTypes.source
    WHERE Spectra.regime like "NIR"
    AND SpectralTypes.regime = "nir"
