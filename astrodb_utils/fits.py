from astropy.io import fits


def make_spectrum_header(wavelength_data, **original_header_dict):
    """Creates a header from a dictionary of values.
    Based on the IVOA Data Model 1.2. 
    https://www.ivoa.net/documents/SpectrumDM/20111120/REC-SpectrumDM-1.1-20111120.pdf

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

    mandatory_keywords = [
        ("VOCLASS", "VO Data Model"),
        ("VOPUB", ""),
        ("TITLE", "Dataset title "),
        ("OBJECT", "Name of observed object"),
        ("RA", "[deg] Pointing position"),
        ("DEC", "[deg] Pointing position"),
        ("APERATURE", "[arcsec] Slit width"),
        ("TMID", "[d] MJD of exposure mid-point"),
        ("TELAPSE", "[s] Total elapsed time (s)"),
        ("SPEC_VAL", "[angstrom] Characteristic spectral coordinate"),
        ("SPEC_BW", "[angstrom] width of spectrum"),
        ("TDMIN1", ""),
        ("TDMAX1", ""),
        ("TTYPE1", ""),
        ("TTYPE2", "")
    ]
     
    recommended_keywords = [
        ("VOREF",""),
        ("INSTRUME",""),
        ("AUTHOR","")
    ]

    new_header = fits.Header()
    # add original_header to new header

    keywords_given = list(original_header_dict.keys())

    # Loop through and assign all mandatory keywords 
    for key,comment in mandatory_keywords:
        value = original_header_dict.get(key)
        if value is not None:
            new_header.set(key, value, description)







    
    # try:
    #    header.set("VOCLASS", original_header_dict["voclass"], "VO Data Model")
    # except KeyError:
    #    logging.warning("No VO Data Model")

    # REQUIRED Target Data
    try:
        header.set(
            "OBJECT", original_header_dict["object_name"], "Name of observed object"
        )
    except KeyError:
        object_name = input("REQUIRED: Please input a name for the object: ")
        header.set("OBJECT", object_name, "Name of observed object")

    try:
        telescope = original_header_dict["telescope"]
        header.set("TELESCOP", telescope, "name of telescope")
    except KeyError:
        telescope = input("REQURIED: Please input the name of the telescope: ")
        header.set("TELESCOP", telescope, "name of telescope")

    try:
        instrument = original_header_dict["instrument"]
        header.set("INSTRUME", instrument, "name of instrument")
    except KeyError:
        instrument = input("REQUIRED: Please input the name of the instrument: ")
        header.set("INSTRUME", instrument, "name of instrument")

    try:
        ra = original_header_dict["RA"]
        header.set("RA_OBJ", ra, "[deg] Right Ascension of object")
    except KeyError:
        ra = input(
            "REQUIRED: Please input the right ascension of the object in degrees: "
        )
        header.set("RA_OBJ", ra, "[deg] Right Ascension of object")

    try:
        dec = original_header_dict["dec"]
        header.set("DEC_OBJ", dec, "[deg] Declination of object")
    except KeyError:
        dec = input("REQUIRED: Please input the declination of the object in degrees: ")
        header.set("DEC_OBJ", dec, "[deg] Declination of object")

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

    header.set("SPEC_VAL", w_mid, f"[{w_units}] Characteristic spec coord")
    header.set("SPEC_BW", width, f"[{w_units}] Width of spectrum")
    header.set("TDMIN1", w_min, f"[{w_units}] Starting wavelength")
    header.set("TDMAX1", w_max, f"[{w_units}] Ending wavelength")

    try:
        bandpass = original_header_dict["bandpass"]
        header.set("SPECBAND", bandpass, "SED.bandpass")
    except KeyError:
        bandpass = assign_ucd(w_mid * wavelength_data.unit)
        header.set("SPECBAND", bandpass, "SED.bandpass")

    # OPTIONAL Header keywords
    try:
        exposure_time = original_header_dict["exposure_time"]
        header.set("TELAPSE", exposure_time, "[s] Total elapsed time")
    except KeyError:
        exposure_time = input("Please input the exposure time in seconds: ")
        if exposure_time != "":
            header.set("TELAPSE", exposure_time, "[s] Total elapsed time")

    try:
        time_start = Time(dateparser.parse(original_header_dict["start_time"])).jd
        header.set("TSTART", time_start, "[d] MJD start time")
    except KeyError:
        time_start = None

    try:
        time_stop = Time(dateparser.parse(original_header_dict["stop_time"])).jd
        header.set("TSTOP", time_stop, "[d] MJD stop time")
    except KeyError:
        time_stop = None

    try:
        time = (
            Time(dateparser.parse(original_header_dict["start_time"])).jd
            + Time(dateparser.parse(original_header_dict["stop_time"])).jd
        ) / 2
        header.set("TMID", time, "[d] MJD mid expsoure")
    except KeyError:
        time = None

    try:
        obs_location = original_header_dict["observatory"]
        header.set("OBSERVAT", obs_location, "name of observatory")
    except KeyError:
        obs_location = None

    try:
        aperture = original_header_dict["aperture"]
        header.set("APERTURE", aperture, "[arcsec] slit width")
    except KeyError:
        aperture = input("OPTIONAL: Please input the slitwidth in arcseconds: ")
        if aperture != "":
            header.set("APERTURE", aperture, "[arcsec] slit width")

    # Publication Information
    try:
        title = original_header_dict["title"]  # trim so header wraps nicely
        header.set("TITLE", title, "Data set title")
    except KeyError:
        title = None

    try:
        header.set("AUTHOR", original_header_dict["author"], "Authors of the data")
    except KeyError:
        author = input("OPTIONAL: Please input the original authors of the data: ")
        if author != "":
            header.set("AUTHOR", author, "Authors of the data")

    try:
        header.set("VOREF", original_header_dict["bibcode"], "Bibcode of dataset")
    except KeyError:
        pass

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
