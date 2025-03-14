import logging

import astropy.units as u
import dateparser
import numpy as np
from astropy.coordinates import SkyCoord
from astropy.io import fits
from astroquery.simbad import Simbad

from astrodb_utils.photometry import assign_ucd

logger = logging.getLogger('astrodb_utils')

def add_missing_keywords(header=None, format='simple-spectrum', keywords=None):
    """Finds the keywords that are missing from a header and adds them with blank values

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
    print("Use the `astrodb_utils.fits.add_wavelength_keywords` function to add the SPEC_VAL, SPEC_BW, and SPECBAND keywords")
    print("\n")
    for keyword, comment in missing_keywords:
        print(f"header.set('{keyword}', \"<value>\")")  # {comment}")

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
        logger.debug(f"Date of observation: {date} parsed to {obs_date}")
        if obs_date is not None:
            obs_date_short = obs_date.strftime("%Y-%m-%d")
            obs_date_long = obs_date.strftime("%b %d, %Y")
            header.set("DATE-OBS", obs_date_short, "date of the observation")
            print(f"Date of observation: {obs_date_long}")
            print(f"DATE-OBS set to : {obs_date_short}.")
        else:
            raise ValueError(f"Date could not be parsed by dateparser.parse: {date}")
    except Exception as e:
        raise e


def check_header(header=None, format='simple-spectrum', ignore_simbad=False):
    """
    Check the header of a FITS file for required keywords and other properties.

    Parameters
    ----------
    header : astropy.io.fits.Header
        The header object to be checked.
    format : str, optional
        The format of the FITS file. Default is 'simple-spectrum'.
    ignore_simbad : bool, optional
        Whether to ignore checking SIMBAD coordinates. Default is False.

    Returns
    -------
    bool
        True if the header passes all checks, False otherwise.

    Raises
    ------
    ValueError
        If the header is not provided.

    """
    #TODO: Check DOI

    result = True

    if header is None:
        raise ValueError("Header is required")
    
    # check for missing keywords
    keywords = get_keywords(format)
    missing_keywords = []    
    for keyword, comment in keywords:
        value = header.get(keyword)
        if value is None:
            if len(missing_keywords) == 0:
                print("The following keywords are not set in the header:")
            missing_keywords.append((keyword, comment))
            print(f"{keyword} : {comment}")            

    coord = make_skycoord(header)
    if coord is None:
        print("Coordinates are required")
        result = False
        logger.debug(f"Coords: {coord}, result: {result}")

    if ignore_simbad is False:
        name_check = check_simbad_name(header)

        if name_check is True:
            print("make sure SIMBAD coords match header coords")
            #check_ra_dec_simbad(simbad_name_results):
        else:
            result = False
        logger.debug(f"name check returns {result}")
        
    if check_date(header) is False:
        result = False
        logger.debug(f"Date check returns {result}")

    logger.debug(f"Header check returns {result}")
    return result


def get_keywords(format):
    #TODO: What do if RA/DEC is present but not RA_TARG/DEC_TARG?


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
            ("AUTHOR", "Authors of original dataset"),
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


def make_skycoord(header):
    # check RA and Dec are in degrees
    ra_targ = header.get('RA_TARG')
    if ra_targ is None:
        ra_targ = header.get('RA')
        if ra_targ is None:
            print("RA_TARG or RA is required")
            ra = None
            return None
    else:
        ra = float(header.get('RA_TARG'))
        if ra > 360:
            print("RA_TARG does not appear to be in degrees")
            print(f"RA_TARG: {ra}")
            print("RA_TARG should be in degrees")
            return None

    dec_targ = header.get('DEC_TARG')
    if dec_targ is None:
        dec_targ = header.get('DEC')
        if dec_targ is None:
            print("DEC_TARG or DEC is required")
            dec = None
            return None
    else:
        dec = float(header.get('DEC_TARG'))

        if dec > 90:
            print("DEC_TARG does not appear to be in degrees")
            print(f"DEC_TARG: {dec}")
            print("DEC_TARG should be in degrees")
            return None

    # Check if ra and dec could be read into SkyCoord object and converted to sexagesimal
    try:
        coord = SkyCoord(ra,dec, unit=(u.deg, u.deg))
        coord_str = coord.to_string('hmsdms')
        print(f"coordinates converted to sexagesimal: {coord_str}")
        return coord
    except Exception as e:
        print(f"coordinates ({ra},{dec}) could not be converted to Skycoord object: {e}")
        return None


def check_simbad_name(header):
     # search SIMBAD for object name
    object_name = header.get('OBJECT')
    
    if object_name is None:
        print("OBJECT name is required")
        return False

    simbad_name_results = Simbad.query_object(object_name)
    logger.debug(f"SIMBAD results for object name {object_name}: {simbad_name_results}")
    print(f"SIMBAD results for object name {object_name}: {simbad_name_results}")
    coord = make_skycoord(header)
    
    if simbad_name_results is None and coord is None:
        print(f"Object name {object_name} not found in SIMBAD")
        return False
    
    # search for object using RA/Dec coordinates
    elif simbad_name_results is None and coord is not None:
        coord_str = coord.to_string('hmsdms')
        print(f"Object name {object_name} not found in SIMBAD, trying 60\" coord search")
        simbad_coord_results = Simbad.query_region(coord, radius='0d0m60s')
        if simbad_coord_results is not None:
            print(f"SIMBAD objects within 60\" search of {coord_str}:")
            print(simbad_coord_results)
            return False
    
    if len(simbad_name_results) == 1:
        print(f"Object name {object_name} found in SIMBAD")
        print(simbad_name_results)
        return True
    else:
        print(f"Multile object name {object_name} matches found in SIMBAD")
        print(simbad_name_results)
        return False


def check_ra_dec_simbad(simbad_name_results):
    # TODO: make this a skycoord object  comparison and figure out correct tolerance
    result = True
    # check RA and  Dec agree with SIMBAD
        # ra_simbad = simbad_name_results['RA']
        # dec_simbad = simbad_name_results['DEC']
        
        # ra_check = np.isclose(ra, ra_simbad, atol=0.1) # check if ra is close to simbad ra
        # dec_check = np.isclose(dec, dec_simbad, atol=0.1) # check if dec
        # if not ra_check or not dec_check:
        #    print("RA_TARG and DEC_TARG do not match SIMBAD coordinates")
        #    print(f"RA_TARG: {ra}, DEC_TARG: {dec}")
        #    print(f"SIMBAD RA: {ra_simbad}, DEC: {dec_simbad}")
        #     result = False

    return result


def check_date(header):
    # check date can be turned to dateTime object
    date = header.get('DATE-OBS')
    if date is None:
        print("DATE-OBS is not set in header")
        result = False
    else:
        try:
            obs_date = dateparser.parse(date)
            obs_date_long = obs_date.strftime("%b %d, %Y")
            print(f"DATE-OBS set to : {date}.")
            print(f"Date of observation: {obs_date_long}")
            result = True
        except Exception as e:
            print(f"Date ({date})could not be converted to Python DateTime object \n {e}")  
            result = False 

    logger.debug(f"Date of observation: {date} returns {result}")
    return result
