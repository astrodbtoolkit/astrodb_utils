import datetime
import importlib.util
import logging
import os
import sqlite3
import sys
from typing import Optional

import astropy.units as u
import numpy as np
import requests
import sqlalchemy.exc
from astrodbkit.astrodb import Database
from astropy.io import fits
from specutils import Spectrum
from sqlalchemy import and_

from astrodb_utils import AstroDBError, exit_function
from astrodb_utils.instruments import get_db_instrument
from astrodb_utils.publications import get_db_publication
from astrodb_utils.sources import find_source_in_db
from astrodb_utils.utils import check_obs_date, get_db_regime, internet_connection

matplotlib_check = importlib.util.find_spec("matplotlib")
if matplotlib_check is not None:
    import matplotlib.pyplot as plt


__all__ = ["check_spectrum_plottable", "ingest_spectrum", "find_spectra"]

logger = logging.getLogger(__name__)


def check_spectrum_plottable(
    spectrum_path: str | Spectrum, raise_error: bool = True, show_plot: bool = False, format: str = None
):
    """
    Check if spectrum is readable and plottable with specutils.
    show_plot = True requires matplotlib to be installed.

    Parameters
    ----------
    spectrum_path : str or Spectrum
        Path to spectrum file or Spectrum object

    raise_error : bool. Default=True
        True: Raise error if spectrum is not plottable
        False: Do not raise error if spectrum is not plottable. Log warning instead.

    show_plot : bool. Default=False
        True: Show plot of spectrum. Matplotlib must be installed.

    format : str, optional
        Format of the spectrum file. If not provided, the format will be inferred by specutils.

    Returns
    -------
    bool
        True: Spectrum is plottable
        False: Spectrum is not plottable

    """
    # check if spectrum is a Spectrum object or a file path
    # if it's a file path, check if it can be read as a Spectrum object
    if isinstance(spectrum_path, Spectrum):
        spectrum = spectrum_path
    elif isinstance(spectrum_path, str):
        try:
            spectrum = Spectrum.read(spectrum_path, format=format)
        except Exception as error_message:
            msg = f"Unable to load file as Spectrum object:{spectrum_path}:\n{error_message}"
            exit_function(msg, raise_error=raise_error)
    else:
        msg = f"Input is not a valid path or Spectrum object: {spectrum_path}"
        exit_function(msg, raise_error=raise_error)

    # checking spectrum has good units
    wave_unit_check = _check_spectrum_wave_units(spectrum, raise_error=raise_error)
    if not wave_unit_check:
        return False

    flux_unit_check = _check_spectrum_flux_units(spectrum, raise_error=raise_error)
    if not flux_unit_check:
        return False

    # check for NaNs
    nan_check = _check_spectrum_not_nans(spectrum, raise_error=raise_error)
    if not nan_check:
        return False

    if show_plot:
        _plot_spectrum(spectrum)

    return True


def _check_spectrum_not_nans(spectrum, raise_error=True):
    nan_check: np.ndarray = ~np.isnan(spectrum.flux) & ~np.isnan(spectrum.spectral_axis)
    wave = spectrum.spectral_axis[nan_check]
    if not len(wave):
        msg = "Spectrum is all NaNs"
        if raise_error:
            logger.error(msg)
            raise AstroDBError(msg)
        else:
            logger.warning(msg)
            return False
    else:
        return True


def _check_spectrum_wave_units(spectrum, raise_error=True):
    try:
        spectrum.spectral_axis.to(u.micron).value
        return True
    except AttributeError as e:
        logger.debug(f"{e}")
        msg = f"Unable to parse spectral axis: {spectrum}"
        if raise_error:
            logger.error(msg)
            raise AstroDBError(msg)
        else:
            logger.warning(msg)
            return False
    except u.UnitConversionError as e:
        logger.debug(f"{e}")
        msg = f"Unable to convert spectral axis to microns:  {spectrum}"
        if raise_error:
            logger.error(msg)
            raise AstroDBError(msg)
        else:
            logger.warning(msg)
            return False
    except ValueError as e:
        logger.debug(f"{e}")
        msg = f"Value error: {spectrum}:"
        if raise_error:
            logger.error(msg)
            raise AstroDBError(msg)
        else:
            logger.warning(msg)
            return False


def _check_spectrum_flux_units(spectrum, raise_error=True):
    expected_units = [
        u.get_physical_type(u.erg / u.s / u.cm**2 / u.AA),
        u.get_physical_type(u.Jy),
    ]

    unit_type = u.get_physical_type(spectrum.flux.unit)

    if unit_type in expected_units:
        return True
    else:
        msg = f"flux units are not expected: {spectrum.flux.unit}. Expecting {expected_units}."
        if raise_error:
            logger.error(msg)
            raise AstroDBError(msg)
        else:
            logger.warning(msg)
            return False


def _plot_spectrum(spectrum):
    if "matplotlib" in sys.modules:
        plt.plot(spectrum.spectral_axis, spectrum.flux)
        plt.xlabel(f"Dispersion ({spectrum.spectral_axis.unit})")
        plt.ylabel(f"Flux ({spectrum.flux.unit})")
        plt.show()
    else:
        msg = "To display the spectrum, matplotlib most be installed."
        logger.warning(msg)


def ingest_spectrum(
    db: Database,
    *,
    source: str = None,
    spectrum: str = None,
    regime: str = None,
    telescope: str = None,
    instrument: str = None,
    mode: str = None,
    obs_date: str | datetime.datetime = None,
    reference: str = None,
    original_spectrum: Optional[str] = None,
    comments: Optional[str] = None,
    other_references: Optional[str] = None,
    local_spectrum: Optional[str] = None,
    raise_error: bool = True,
    format: Optional[str] = None,
):
    """
    Parameters
    ----------
    db: astrodbkit.astrodb.Database
        Database object created by astrodbkit
    source: str
        source name
    spectrum: str
        URL or path to spectrum file
    regime: str
        Regime of spectrum (optical, infrared, radio, etc.)
        controlled by Regimes table
    telescope: str
        Telescope used to obtain spectrum.
        Required to be in Telescopes table.
    instrument: str
        Instrument used to obtain spectrum.
        Instrument-Mode pair needs to be in Instruments table.
    mode: str
        Instrument mode used to obtain spectrum.
        Instrument-Mode pair needs to be in Instruments table.
    obs_date: str
        Observation date of spectrum.
    reference: str
        Reference for spectrum.
        Required to be in Publications table.
    original_spectrum: str
        Path to original spectrum file if different from spectrum.
    comments: str
        Comments about spectrum.
    other_references: str
        Other references for spectrum.
    local_spectrum: str
        Path to local spectrum file.
    raise_error: bool
        If True, raise an error if the spectrum cannot be added.
        If False, continue without raising an error.
    format: str
        Format of the spectrum file used by specutils to load the file.
        If not provided, the format will be determined by specutils.
        Options: "tabular-fits",

    Returns
    -------
    flags: dict
        Status response with the following keys:
             - "added": True if it's added and False if it's skipped.
             - "content": the data that was attempted to add
             - "message": string which includes information about why skipped

    Raises
    ------
    AstroDBError
    """
    # Compile fields into a dictionary

    flags = {"added": False, "content": {}, "message": ""}

    # Make sure reference is provided and is in the Publications table
    if reference is None:
        msg = "Reference is required."
        flags["message"] = msg
        exit_function(msg, raise_error=raise_error, return_value=flags)
        return flags
    else:
        reference_db = get_db_publication(db, reference, raise_error=raise_error)
        if reference_db is None:
            flags["message"] = f"Reference not found in database: {reference}."
            return flags

    # If a date is provided as a string, convert it to datetime
    logger.debug(f"Parsing obs_date: {obs_date}")
    if obs_date is not None and isinstance(obs_date, str):
        parsed_date = check_obs_date(obs_date, raise_error=raise_error)
    elif isinstance(obs_date, datetime.datetime):
        parsed_date = obs_date

    if obs_date is None or (parsed_date is None and raise_error is False):
        msg = f"Observation date is not valid: {obs_date}"
        flags["message"] = msg
        if raise_error:
            raise AstroDBError(msg)
        else:
            logger.warning(msg)
            return flags

    # Get source name as it appears in the database
    db_name = find_source_in_db(db, source)
    logger.debug(f"Found db_name: {db_name} for source: {source}")
    if len(db_name) == 1:
        db_name = db_name[0]
    else:
        msg = f"Invalid source name. No unique source match for {source} in the database. Found {db_name}."
        flags["message"] = msg
        if raise_error:
            raise AstroDBError(msg)
        else:
            logger.warning(msg)
            return flags

    # Check if regime is provided and is in the Regimes table
    regime = get_db_regime(db, regime, raise_error=raise_error)
    if regime is None:
        msg = f"Regime not found in database: {regime}."
        flags["message"] = msg
        if raise_error:
            raise AstroDBError(msg)
        else:
            logger.warning(msg)
            return flags

    # Find the right instrument-mode-telescope in the database
    if instrument is None:
        msg = "Instrument is required."
        flags["message"] = msg
        if raise_error:
            raise AstroDBError(msg)
        else:
            logger.warning(msg)
            return flags
    instrument, mode, telescope = get_db_instrument(
        db,
        instrument=instrument,
        mode=mode,
        telescope=telescope,
    )

    # Check if spectrum is a duplicate
    matches = find_spectra(
        db,
        db_name,
        reference=reference,
        obs_date=parsed_date,
        telescope=telescope,
        instrument=instrument,
        mode=mode,
    )
    if len(matches) > 0:
        msg = f"Skipping suspected duplicate measurement: {source}"
        msg2 = f"{matches} {instrument, mode, parsed_date, reference, spectrum}"
        logger.debug(msg2)
        flags["message"] = msg
        # exit_function(msg, raise_error=raise_error)
        if raise_error:
            raise AstroDBError(msg)
        else:
            logger.warning(msg)
            return flags


    # Check if spectrum file(s) are accessible
    check_spectrum_accessible(spectrum)
    if original_spectrum is not None:
        check_spectrum_accessible(original_spectrum)

    # Check if spectrum is plottable
    flags["plottable"] = check_spectrum_plottable(spectrum)

    # If it's a FITS file, verify the header
    if os.path.splitext(spectrum)[1] == ".fits":
        with fits.open(spectrum) as hdul:
            hdul.verify("warn")

    row_data = {
        "source": db_name,
        "access_url": spectrum,
        "original_spectrum": original_spectrum,
        "local_spectrum": local_spectrum,
        "regime": regime,
        "telescope": telescope,
        "instrument": instrument,
        "mode": mode,
        "observation_date": parsed_date,
        "reference": reference_db,
        "comments": comments,
        "other_references": other_references,
    }
    logger.debug(f"Trying to ingest: {row_data}")
    flags["content"] = row_data

    try:
        # Attempt to add spectrum to database
        with db.engine.connect() as conn:
            conn.execute(db.Spectra.insert().values(row_data))
            conn.commit()

        flags["added"] = True
        logger.info(
            f"Added spectrum for {source}: {telescope}-{instrument}-{mode} from {reference} "
            f"on {parsed_date.strftime('%d %b %Y')}"
        )
    except (sqlite3.IntegrityError, sqlalchemy.exc.IntegrityError) as e:
        msg = f"Integrity Error: {source} \n {e}"
        flags["message"] = msg
        if raise_error:
            raise AstroDBError(msg)
        else:
            logger.error(msg)
            return flags
    except Exception as e:
        msg = f"Spectrum for {source} could not be added to the database for unexpected reason: {e}"
        flags["message"] = msg
        if raise_error:
            raise AstroDBError(msg)
        else:
            logger.warning(msg)
            return flags

    return flags


def find_spectra(
    db: Database,
    source: str,
    *,
    reference: str = None,
    obs_date: str = None,
    telescope: str = None,
    instrument: str = None,
    mode: str = None,
):
    """
    Find what spectra already exists in database for this source
    Finds matches based on parameter provided.
    E.g., if only source is provided, all spectra for that source are returned.
        If Source and telescope are provided,
        only spectra for that source and telescope are provided.

    Parameters
    ----------
    db: astrodbkit.astrodb.Database
        Database object created by astrodbkit
    source: str
        source name

    Returns
    -------
    source_spec_data: astropy.table.Table
        Table of spectra for source
    """

    source_spec_data = db.query(db.Spectra)  # entire Spectra table

    filter_list = [db.Spectra.c.source == source]
    if reference is not None:
        filter_list.append(db.Spectra.c.reference == reference)

    if telescope is not None:
        filter_list.append(db.Spectra.c.telescope == telescope)

    if obs_date is not None:
        filter_list.append(db.Spectra.c.observation_date == obs_date)

    if instrument is not None:
        filter_list.append(db.Spectra.c.instrument == instrument)

    if mode is not None:
        filter_list.append(db.Spectra.c.mode == mode)

    # Actually perform the query
    if len(filter_list) > 0:
        source_spec_data = source_spec_data.filter(and_(*filter_list))
    else:
        source_spec_data = source_spec_data.filter(filter_list[0])
    source_spec_data = source_spec_data.table()

    if len(source_spec_data) > 0:
        logger.debug(f"Found {len(source_spec_data)} spectra for source: {source}")
        logger.debug(f"Spectra data: {source_spec_data}")

    return source_spec_data


def check_spectrum_accessible(spectrum: str) -> bool:
    """
    Check if the spectrum is accessible
    Parameters
    ----------
    spectrum: str
        URL or path to spectrum file

    Returns
    -------
    bool
        True if the spectrum is accessible, False otherwise
    """
    logger.debug(f"Checking spectrum: {spectrum}")
    internet = internet_connection()
    if internet:
        request_response = requests.head(spectrum)
        status_code = request_response.status_code  # The website is up if the status code is 200
        if status_code != 200:
            msg = (
                "The spectrum URL does not appear to be accessible: \n"
                f"spectrum: {spectrum} \n"
                f"status code: {status_code}"
            )
            logger.error(msg)
            return False
        else:
            msg = "The URL for the spectrum is accessible (status code = 200)."
            logger.debug(msg)
            return True
    else:
        msg = "No internet connection. Internet is needed to check spectrum URLs."
        raise AstroDBError(msg)
