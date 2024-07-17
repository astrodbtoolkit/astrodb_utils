import numpy as np
from astropy.io import fits


def missing_keywords(header=None, *,keywords=None):
    """Finds the keywords that are missing from a header

    Inputs
    -------
    header: fits.Header
        a fits header object or dictionary of header values

    keywords: list
        a list of keywords to check for

    Returns
    -------
    a dictionary of missing keywords and their comments

    """
    if header is None:
        header = fits.Header()

    if keywords is None:
        # keywords to check for by default
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
            ("AUTHOR",""),
            ("DATE-OBS", "Date of observation"),
            ("TMID", "[d] MJD of exposure mid-point"),
            ("TELAPSE", "[s] Total elapsed time (s)"),
            ("SPEC_VAL", "[angstrom] Characteristic spectral coordinate"),
            ("SPEC_BW", "[angstrom] width of spectrum"),
            ("SPECBAND", "SED.bandpass"),
            ("APERTURE", "[arcsec] slit width")
    ]

    missing_keywords = fits.Header()

    # Loop through original header and add values to new header
    for keyword, comment in keywords:
        value = header.get(keyword)
        if value is None:
            missing_keywords.set(keyword, None, comment)
    
    # Loop over missing keywords and print for copy and paste purposes
    print("COPY AND PASTE THE FOLLOWING COMMAND INTO YOUR SCRIPT")
    print("Fill in the values you have after the colon (:)")
    print("new_header_keywords_dict =")
    for card in missing_keywords:
        #print(f" \'{card.keyword}\':             ,  #  {card.comment}")
        print(card)
    
    return missing_keywords

def make_spectrum_header(wavelength_data, **original_header_dict):
    """Creates a mostly empty header template for a fits file containing a spectrum

    TODO: if original_header_dict is not provided, what happens?
    TODO: Check that RA and Dec are in degrees

    Inputs
    -------
    wavelength_data: astropy.units.Quantity
        an array of wavelengths. should include units.

    header_dict: dict
        a dictionary or Header object of values to be included in the header

    Returns
    -------
    a fits header dictionary

    """

    # Make new, blank header
    new_header = fits.Header()

    # Use wavelength data to calculate header values
    w_min = min(wavelength_data).astype(np.single)
    w_max = max(wavelength_data).astype(np.single)
    width = (w_max - w_min).astype(np.single)
    w_mid = ((w_max + w_min) / 2).astype(np.single)

    new_header.set("SPEC_VAL", w_mid.value, f"[{w_mid.unit}] Characteristic spec coord")
    new_header.set("SPEC_BW", width.value, f"[{width.unit}] Width of spectrum")
    new_header.set("TDMIN1", w_min.value, f"[{w_min.unit}] Starting wavelength")
    new_header.set("TDMAX1", w_max.value, f"[{w_max.unit}] Ending wavelength")
   
    

    # try:
    #     obs_date = dateparser.parse(original_header_dict["obs_date"]).strftime(
    #         "%Y-%m-%d"
    #     )
    #     header.set("DATE-OBS", obs_date, "date of the observation")
    # except KeyError:
    #     obs_date = input("REQUIRED: Please input the date of the observation: ")
    #     obs_date = dateparser.parse(obs_date).strftime("%Y-%m-%d")
    #     header.set("DATE-OBS", obs_date, "date of the observation")

    # try:
    #     header.set("REFERENC", original_header_dict["doi"], "DOI of dataset")
    # except KeyError:
    #     pass

    # try:
    #     header.set("COMMENT", comment)
    # except KeyError:
    #     pass

    # try:
    #     header.set("HISTORY", history)
    # except KeyError:
    #     pass

    # header.set("DATE", date.today().strftime("%Y-%m-%d"), "Date of file creation")
    # header.set("CREATOR", "simple.spectra.convert_to_fits.py", "FITS file creator")
