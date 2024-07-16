from astropy.io import fits


def make_spectrum_header(wavelength_data, **original_header_dict):
    """Creates a mostly empty header template for a fits file containing a spectrum

    TODO: Check that RA and Dec are in degrees

    Inputs
    -------
    wavelength_data
        an array of wavelengths

    original_header_dict
        a dictionary of values to be included in the header

    Returns
    -------
    a fits header dictionary

    """

    keywords = [
        ("VOPUB", ""),
        ("VOREF", ""),
        ("TITLE", "Dataset title "),
        ("OBJECT", "Name of observed object"),
        ("RA", "[deg] Pointing position"),
        ("DEC", "[deg] Pointing position"),
        ("INSTRUME",""),
        ("TELESCOP",""),
        ("OBSERVAT",""),
        ("AUTHOR","")
        ("APERATURE", "[arcsec] Slit width"),
        ("DATE-OBS", "Date of observation"),
        ("TMID", "[d] MJD of exposure mid-point"),
        ("TELAPSE", "[s] Total elapsed time (s)"),
        ("SPEC_VAL", "[angstrom] Characteristic spectral coordinate"),
        ("SPEC_BW", "[angstrom] width of spectrum"),
        ("SPECBAND", "SED.bandpass"),
        ("APERTURE", "[arcsec] slit width")

    ]

    # Make new, blank header
    new_header = fits.Header()

    # Loop through and check if any keywords are in the original header
    for key,description in keywords:
        value = original_header_dict.get(key)
        if value is not None:
            new_header.set(key, value, description)







    

   

    try:
        obs_date = dateparser.parse(original_header_dict["obs_date"]).strftime(
            "%Y-%m-%d"
        )
        header.set("DATE-OBS", obs_date, "date of the observation")
    except KeyError:
        obs_date = input("REQUIRED: Please input the date of the observation: ")
        obs_date = dateparser.parse(obs_date).strftime("%Y-%m-%d")
        header.set("DATE-OBS", obs_date, "date of the observation")

    # Wavelength info
    w_units = wavelength_data.unit
    w_min = min(wavelength_data).astype(np.single)
    w_max = max(wavelength_data).astype(np.single)
    width = (w_max - w_min).astype(np.single)
    w_mid = ((w_max + w_min) / 2).astype(np.single)

    new_header.set("SPEC_VAL", w_mid, f"[{w_units}] Characteristic spec coord")
    new_header.set("SPEC_BW", width, f"[{w_units}] Width of spectrum")
    new_header.set("TDMIN1", w_min, f"[{w_units}] Starting wavelength")
    new_header.set("TDMAX1", w_max, f"[{w_units}] Ending wavelength")

   


    try:
        obs_location = original_header_dict["observatory"]
        header.set("OBSERVAT", obs_location, "name of observatory")
    except KeyError:
        obs_location = None

    

   
   
    try:
        header.set("REFERENC", original_header_dict["doi"], "DOI of dataset")
    except KeyError:
        pass

    try:
        header.set("VOPUB", original_header_dict["VOPUB"], "VO Publisher")
    except KeyError:
        pass

    try:
        header.set("COMMENT", comment)
    except KeyError:
        pass

    try:
        header.set("HISTORY", history)
    except KeyError:
        pass

    header.set("DATE", date.today().strftime("%Y-%m-%d"), "Date of file creation")
    header.set("CREATOR", "simple.spectra.convert_to_fits.py", "FITS file creator")

    return header

