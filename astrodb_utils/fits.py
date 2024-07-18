import astropy.units as u
import dateparser
import numpy as np
from astropy.io import fits

from astrodb_utils.photometry import assign_ucd


def add_missing_keywords(header=None, *, format='simple-spectrum', keywords=None):
    """Finds the keywords that are missing from a header

    Inputs
    -------
    header: fits.Header
        a fits header object or dictionary of header values

    format: string
        header schemas to enforce. options, 'simple-spectrum'. Eventually, `IVOA-spectrumdm-1.2`
        if provided, keywords is ignored

    keywords: list
        a list of keywords to check for if format is not specified

    Returns
    -------
    FITS header object

    Examples
    --------
    Returns a header with keywords but blank values
    >>> new_header = add_missing_keywords(format='simple-spectrum')

    Adds missing keywords (with blank values) to an existing header
    >>> new_header = add_missing_keywords(old_header, format='simple-spectrum')
    """

    # If no header was provided, start with a blank one
    if header is None:
        header = fits.Header()

    if keywords is None and format is None:
        format = 'simple-spectrum'

    keywords = get_keywords(format)

    missing_keywords = []
    # Loop through the original header and add keywords with blank values to the new header
    for keyword, comment in keywords:
        value = header.get(keyword)
        if value is None:
            header.set(keyword, None, comment)
            missing_keywords.append((keyword, comment))

    # Loop over missing keywords and print for copy and paste purposes
    print("COPY AND PASTE THE FOLLOWING COMMANDS INTO YOUR SCRIPT")
    print("Replace <value> with the appropriate value for your dataset")
    print("If you're not sure of the correct value, use None")
    print("If you started with a header object not called `header`, replace 'header' with the name of your header object")
    print("Use the `add_wavelength_keywords` function to add the SPEC_VAL, SPEC_BW, and SPECBAND keywords")
    print("\n")
    for keyword, comment in missing_keywords:
        print(f"header.set('{keyword}', <value>)  # {comment}")

    return header


def add_wavelength_keywords(header=None, wavelength_data = None):
    """Uses wavelength array to generate header keywords

    Inputs
    -------
    wavelength_data: astropy.units.Quantity
        an array of wavelengths. should include units.

    header_dict: header
        a Header object 

    Returns
    -------
    None

    Examples
    --------
    >>> wavelength = np.arange(5100, 5300)*u.AA
    >>> add_wavelength_keywords(header=new_header, wavelength_data = wavelength)

    """

    # Make new, blank header
    if header is None:
        header = fits.Header()

    # Use wavelength data to calculate header values
    w_min = min(wavelength_data).astype(np.single)
    w_max = max(wavelength_data).astype(np.single)
    width = (w_max - w_min).astype(np.single)
    w_mid = ((w_max + w_min) / 2).astype(np.single)
    bandpass = assign_ucd(w_mid)

    header.set("SPECBAND", bandpass )
    header.set("SPEC_VAL", w_mid.value, f"[{w_mid.unit}] Characteristic spec coord")
    header.set("SPEC_BW", width.value, f"[{width.unit}] Width of spectrum")
    header.set("TDMIN1", w_min.value, f"[{w_min.unit}] Starting wavelength")
    header.set("TDMAX1", w_max.value, f"[{w_max.unit}] Ending wavelength")
    header['HISTORY'] = "Wavelength keywords added by astrodb_utils.fits.add_wavelength_keywords"
   
    #return header    

   

def add_observation_date(header=None, date=None):
    """Adds the observation date to the header

    Inputs
    -------
    header: fits.Header
        a fits header object or dictionary of header values

    date: string
        the date of the observation

    Returns
    -------
    None

    Examples
    --------
    >>> add_observation_date(header, date='2021-06-01')
    """

    if header is None:
        header = fits.Header()

    if date is None:
        raise ValueError("Date of observation is required")

    try:
        obs_date = dateparser.parse(date)
        obs_date_short = obs_date.strftime("%Y-%m-%d")
        obs_date_long = obs_date.strftime("%b %d, %Y")
        header.set("DATE-OBS", obs_date_short, "date of the observation")
        print(f"Date of observation: {obs_date_long}")
        print(f"DATE-OBS set to : {obs_date_short}.")
    except Exception as e:
        raise e("Invalid date format")
    

    #return header


def check_header(header=None, format=None):
    # check for missing keywords
    # check RA and Dec are in degrees
    # check date can be turned to dateTime object
    # validate the header 

    # search SIMBAD for object name

    # check RA and Dec agree with SIMBAD

    # list missing keywords as a double check

    return None

def get_keywords(format):

    formats = ['simple-spectrum','ivoa-spectrum-dm-1.2']
    if format not in formats:
        msg = f"(Format must be one of these: {formats})"
        raise ValueError(msg)

    if format == 'simple-spectrum':
        keywords = [
            ("OBJECT", "Name of observed object"),
            ("RA_TARG", "[deg] target position"),
            ("DEC_TARG", "[deg] target position"),
            ("DATE-OBS", "Date of observation"),
            ("INSTRUME", "Instrument name"),
            ("TELESCOP", "Telescope name"),
            ("TELAPSE", "[s] Total elapsed time (s)"),
            ("APERTURE", "[arcsec] slit width"),
            ("AUTHOR", "First author of original dataset"),
            ("TITLE", "Dataset title "),
            ("VOREF","URL, DOI, or bibcode of original publication"),
            ("VOPUB", "Publisher"), # TODO: Set to SIMPLE
            ("CONTRIB1","Contributor who generated this header"),
            ("SPEC_VAL", "[angstrom] Characteristic spectral coordinate"),
            ("SPEC_BW", "[angstrom] width of spectrum"),
            ("SPECBAND", "SED.bandpass"),
        ]
    elif format == 'ivoa-spectrum-dm-1.2':    
        keywords = [
            ("VOCLASS","Data model name and version"), # TODO:  'Spectrum-1.2', 
            ("VOPUB", ""),
            ("VOREF", "URL, DOI, or bibcode of original publication"),
            ("TITLE", "Dataset title "),
            ("OBJECT", "Name of observed object"),
            ("RA_TARG", "[deg] target position"),
            ("DEC_TARG", "[deg] target position"),
            ("INSTRUME", ""),
            ("TELESCOP", ""),
            ("OBSERVAT", ""),
            ("AUTHOR", ""),
            ("CONTRIB1","Contributor who generated this file"),
            ("DATE-OBS", "Date of observation"),
            ("TMID", "[d] MJD of exposure mid-point"),
            ("TELAPSE", "[s] Total elapsed time (s)"),
            ("SPEC_VAL", "[angstrom] Characteristic spectral coordinate"),
            ("SPEC_BW", "[angstrom] width of spectrum"),
            ("TDMIN1", "Start in spectral coordinate"),
            ("TDMAX1", "Stop in spectral coordinate"),
            ("SPECBAND", "SED.bandpass"),
            ("APERTURE", "[arcsec] slit width"),
        ]

    return keywords



