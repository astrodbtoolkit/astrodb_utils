"""Photometry functions"""

import logging
from io import BytesIO
from typing import Optional

import astropy.units as u
import numpy as np
import requests
import sqlalchemy.exc
from astropy.io.votable import parse

from astrodb_utils import (
    AstroDBError,
    ingest_instrument,
    internet_connection,
)
from astrodb_utils.publications import find_publication
from astrodb_utils.sources import find_source_in_db

logger = logging.getLogger(__name__)

__all__ = ["ingest_photometry", "ingest_photometry_filter", "fetch_svo", "assign_ucd"]


def ingest_photometry(
    db,
    *,
    source: str = None,
    band: str = None,
    regime: str = None,
    magnitude: float = None,
    magnitude_error: float = None,
    reference: str = None,
    telescope: Optional[str] = None,
    epoch: Optional[float] = None,
    comments: Optional[str] = None,
    raise_error: bool = True,
):
    """
    Add a photometry measurement to the database

    Parameters
    ----------
    db: astrodbkit.astrodb.Database
    source: str
    band: str
    regime: str
    magnitude: float
    magnitude_error: float
    reference: str
    telescope: str, optional
    epoch: float, optional
    comments: str, optional
    raise_error: bool, optional
        True (default): Raise an error if a source cannot be ingested
        False: Logs a warning but does not raise an error

    Returns
    -------
    flags: dict
        added: bool
            True if the measurement was added to the database
            False if the measurement was not added to the database

    """
    flags = {"added": False}

    # Make sure required fields are provided
    if source is None or band is None or magnitude is None or reference is None:
        msg = (
            "source, band, magnitude, and reference are required. \n"
            f"Provided: source={source}, band={band}, "
            f"magnitude={magnitude}, "
            f"reference={reference}"
        )
        if raise_error:
            logger.error(msg)
            raise AstroDBError(msg)
        else:
            logger.warning(msg)
            return flags

    # Make sure source exists in the database
    db_name = find_source_in_db(db, source)
    if len(db_name) != 1:
        msg = f"No unique source match for {source} in the database"
        if raise_error:
            logger.error(msg)
            raise AstroDBError(msg)
        else:
            logger.warning(msg)
            return flags
    else:
        db_name = db_name[0]

    # Make sure the reference exists in the Publications table
    pub_check = find_publication(db, reference=reference)
    if pub_check[0]:
        msg = f"Reference found: {pub_check[1]}."
        logger.info(msg)
    if not pub_check[0]:
        msg = f"Reference {reference} not found in Publications table."
        if raise_error:
            logger.error(msg)
            raise AstroDBError(msg)
        else:
            logger.warning(msg)
            return flags

    # TODO: Make sure band exists in the PhotometryFilters table
    band_match = (
        db.query(db.PhotometryFilters)
        .filter(db.PhotometryFilters.c.band == band)
        .table()
    )
    if len(band_match) == 0:
        msg = f"Band {band} not found in PhotometryFilters table."
        if raise_error:
            logger.error(msg)
            raise AstroDBError(msg)
        else:
            logger.warning(msg)
            return flags

    # If telescope is provided, make sure it exists in the Telescopes table
    if telescope is not None:
        telescope_match = (
            db.query(db.Telescopes)
            .filter(db.Telescopes.c.telescope == telescope)
            .table()
        )
        if len(telescope_match) == 0:
            msg = f"Telescope {telescope} not found in Telescopes table."
            if raise_error:
                logger.error(msg)
                raise AstroDBError(msg)
            else:
                logger.warning(msg)
                return flags

    # if the uncertainty is masked, set it to None,
    #        otherwise convert to a string
    if isinstance(magnitude_error, np.ma.core.MaskedConstant):
        mag_error = None
    elif magnitude_error is None:
        mag_error = None
    else:
        mag_error = str(magnitude_error)

    # Construct data to be added
    photometry_data = [
        {
            "source": db_name,
            "band": band,
            "regime": regime,
            "magnitude": str(
                magnitude
            ),  # Convert to string to maintain significant digits
            "magnitude_error": mag_error,
            "telescope": telescope,
            "epoch": epoch,
            "comments": comments,
            "reference": reference,
        }
    ]
    logger.debug(f"Photometry data: {photometry_data}")

    try:
        with db.engine.connect() as conn:
            conn.execute(db.Photometry.insert().values(photometry_data))
            conn.commit()
        flags["added"] = True
        logger.info(f"Photometry measurement added: \n" f"{photometry_data}")
    except sqlalchemy.exc.IntegrityError as e:
        if "UNIQUE constraint failed:" in str(e):
            msg = "The measurement may be a duplicate."
            if raise_error:
                logger.error(msg)
                raise AstroDBError(msg)
            else:
                logger.warning(msg)
        else:
            msg = (
                "The source may not exist in Sources table.\n"
                "The band may not exist in the PhotometryFilters table.\n"
                "The reference may not exist in the Publications table. "
                "Add it with add_publication function."
            )
            if raise_error:
                logger.error(msg+str(e))
                raise AstroDBError(msg+str(e))
            else:
                logger.warning(f"{msg}/n{str(e)}")

    return flags


def ingest_photometry_filter(
    db, *, telescope=None, instrument=None, filter_name=None, ucd=None
):
    """
    Add a new photometry filter to the database
    """
    # Fetch existing telescopes, add if missing
    existing = (
        db.query(db.Telescopes).filter(db.Telescopes.c.telescope == telescope).table()
    )
    if len(existing) == 0:
        with db.engine.connect() as conn:
            conn.execute(db.Telescopes.insert().values({"telescope": telescope}))
            conn.commit()
        logger.info(f"Added telescope {telescope}.")
    else:
        logger.info(f"Telescope {telescope} already exists.")

    # Fetch existing instruments, add if missing
    existing = (
        db.query(db.Instruments)
        .filter(db.Instruments.c.instrument == instrument)
        .table()
    )
    if len(existing) == 0:
        ingest_instrument(
            db, telescope=telescope, instrument=instrument, mode="Imaging"
        )
        logger.info(f"Added instrument {instrument}.")
    else:
        logger.info(f"Instrument {instrument} already exists.")

    # Get data from SVO
    filter_id, wave_eff, fwhm, width_effective = fetch_svo(
        telescope, instrument, filter_name
    )
    logger.info(
        f"From SVO: Filter {filter_id} has effective wavelength {wave_eff} "
        f"and FWHM {fwhm} and width_effective {width_effective}."
    )

    if ucd is None:
        ucd = assign_ucd(wave_eff)
    logger.info(f"UCD for filter {filter_id} is {ucd}")

    # Add the filter
    try:
        with db.engine.connect() as conn:
            conn.execute(
                db.PhotometryFilters.insert().values(
                    {
                        "band": filter_id,
                        "ucd": ucd,
                        "effective_wavelength_angstroms": wave_eff.to(u.Angstrom).value,
                        "width_angstroms": width_effective.to(u.Angstrom).value,
                    }
                )
            )
            conn.commit()
        logger.info(
            f"Added filter {filter_id} with effective wavelength {wave_eff}, "
            f"width {width_effective}, and UCD {ucd}."
        )
    except sqlalchemy.exc.IntegrityError as e:
        if "UNIQUE constraint failed:" in str(e):
            msg = str(e) + f"Filter {filter_id} already exists in the database."
            raise AstroDBError(msg)
        else:
            msg = str(e) + f"Error adding filter {filter_id}."
            raise AstroDBError(msg)
    except Exception as e:
        msg = str(e)
        raise AstroDBError(msg)


def fetch_svo(telescope: str = None, instrument: str = None, filter_name: str = None):
    """
    Fetch photometry filter information from the SVO Filter Profile Service
    http://svo2.cab.inta-csic.es/theory/fps/

    Could use better error handling when instrument name or filter name is not found

    Parameters
    ----------
    telescope: str
        Telescope name
    instrument: str
        Instrument name
    filter_name: str
        Filter name

    Returns
    -------
    filter_id: str
        Filter ID
    wave_eff: Quantity
        Effective wavelength
    fwhm: Quantity
        Full width at half maximum (FWHM)
    width_effective: Quantity
        Effective width of the filter

    Raises
    ------
    AstroDBError
        If the SVO URL is not reachable or the filter information is not found
    KeyError
        If the filter information is not found in the VOTable
    """

    if internet_connection() is False:
        msg = (
            "No internet connection. "
            "Cannot fetch photometry filter information from the SVO website."
        )
        logger.error(msg)
        raise AstroDBError(msg)

    url = (
        f"http://svo2.cab.inta-csic.es/svo/theory/fps3/fps.php?ID="
        f"{telescope}/{instrument}.{filter_name}"
    )
    r = requests.get(url)

    if r.status_code != 200:
        msg = f"Error retrieving {url}. Status code: {r.status_code}"
        logger.error(msg)
        raise AstroDBError(msg)

    # Parse VOTable contents
    content = BytesIO(r.content)
    votable = parse(content)

    # Get Filter ID
    try:
        filter_id = votable.get_field_by_id("filterID").value
    except KeyError:
        msg = f"Filter {telescope}, {instrument}, {filter_name} not found in SVO."
        raise AstroDBError(msg)

    # Get effective wavelength and FWHM
    wave_eff = votable.get_field_by_id("WavelengthEff")
    fwhm = votable.get_field_by_id("FWHM")
    width_effective = votable.get_field_by_id("WidthEff")

    if wave_eff.unit == "AA" and fwhm.unit == "AA" and width_effective.unit == "AA":
        wave_eff = wave_eff.value * u.Angstrom
        fwhm = fwhm.value * u.Angstrom
        width_effective = width_effective.value * u.Angstrom
    else:
        msg = (
            f"Wavelengths from SVO may not be Angstroms as expected: {wave_eff.unit},"
            f"{fwhm.unit}, {width_effective.unit}."
        )
        raise AstroDBError(msg)

    logger.debug(
        f"Found in SVO: "
        f"Filter {filter_id} has effective wavelength {wave_eff} and "
        f"FWHM {fwhm} and effective width {width_effective}."
    )

    return filter_id, wave_eff, fwhm, width_effective


def assign_ucd(wave_eff_quantity: u.Quantity):
    """
    Assign a Unified Content Descriptors (UCD) to a photometry filter
    based on its effective wavelength
    UCDs are from the UCD1+ controlled vocabulary
    https://www.ivoa.net/documents/UCD1+/20200212/PEN-UCDlist-1.4-20200212.html#tth_sEcB

    Parameters
    ----------
    wave_eff: Quantity
        Effective wavelength

    Returns
    -------
    ucd: str
        UCD string

    """
    wave_eff_quantity.to(u.Angstrom)
    wave_eff = wave_eff_quantity.value

    ucd_dict = {
        (3000, 4000): "em.opt.U",
        (4000, 5000): "em.opt.B",
        (5000, 6000): "em.opt.V",
        (6000, 7500): "em.opt.R",
        (7500, 10000): "em.opt.I",
        (10000, 15000): "em.IR.J",
        (15000, 20000): "em.IR.H",
        (20000, 30000): "em.IR.K",
        (30000, 40000): "em.IR.3-4um",
        (40000, 80000): "em.IR.4-8um",
        (80000, 150000): "em.IR.8-15um",
        (150000, 300000): "em.IR.15-30um",
    }
    for key, value in ucd_dict.items():
        if key[0] < wave_eff <= key[1]:
            ucd = value
            break
    else:
        ucd = None

    return ucd
