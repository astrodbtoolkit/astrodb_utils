"""Utils functions for use in ingests."""

import datetime
import logging
import os
import socket
import time
from pathlib import Path

import requests
from astrodbkit.astrodb import Database, create_database
from astroquery.simbad import Simbad
from astroquery.simbad import conf as simbad_conf
from sqlalchemy import func

__all__ = [
    "load_astrodb",
    "internet_connection",
    "exit_function",
    "set_simbad_mirror",
    "select_simbad_mirror",
    "simbad_available",
    "get_db_regime",
    "check_obs_date",
]

class AstroDBError(Exception):
    """Custom error for AstroDB"""

logger = logging.getLogger(__name__)
msg = f"logger.parent.name: {logger.parent.name}, logger.parent.level: {logger.parent.level}"
logger.debug(msg)


def set_simbad_mirror(server: str):
    """
    Choose which SIMBAD mirror astroquery (and therefore astrodb_utils and astrodbkit) queries.

    The shared ``astroquery.simbad.Simbad`` object is used by all SIMBAD lookups, so this
    affects every call made afterwards in the current Python session.

    Parameters
    ----------
    server : str
        Host name of the mirror, without ``https://`` or a path, e.g.
        ``"simbad.cds.unistra.fr"`` (default, Strasbourg), ``"simbad.harvard.edu"`` (CfA)
        or ``"simbad.idia.ac.za"`` (IDIA, South Africa).

    """
    server = server.replace("https://", "").replace("http://", "").strip("/")
    # astroquery only knows about some mirrors by default; register others so the setter accepts them
    if server not in simbad_conf.servers_list:
        simbad_conf.servers_list = [*simbad_conf.servers_list, server]
    Simbad.server = server
    logger.info(f"Using SIMBAD mirror: {server}")


SIMBAD_MIRRORS = ("simbad.cds.unistra.fr", "simbad.harvard.edu", "simbad.idia.ac.za")

# Result of the last mirror check: (a mirror host name or None, time.monotonic() of the check)
_simbad_status = None
# After a failed check, wait this many seconds before probing the mirrors again
SIMBAD_RECHECK_SECONDS = 60


def select_simbad_mirror(mirrors=SIMBAD_MIRRORS, timeout: float = 5):
    """
    Use the first SIMBAD mirror that responds, trying them in order.

    Parameters
    ----------
    mirrors : sequence of str
        Host names to try, in order of preference. Default: Strasbourg (CDS), then Harvard (CfA), then IDIA (South Africa).
    timeout : float
        Seconds to wait for each mirror.

    Returns
    -------
    str or None
        The mirror now in use, or None if none responded (the current setting is left unchanged).
    """
    global _simbad_status
    for server in mirrors:
        try:
            ok = requests.get(f"https://{server}/simbad/sim-tap/capabilities", timeout=timeout).ok
        except requests.exceptions.RequestException:
            ok = False
        if ok:
            set_simbad_mirror(server)
            _simbad_status = (server, time.monotonic())
            return server
        logger.warning(f"SIMBAD mirror {server} is not responding")
    logger.warning("No SIMBAD mirror responded")
    _simbad_status = (None, time.monotonic())
    return None


def simbad_available() -> bool:
    """
    Check (lazily) whether SIMBAD can be used, switching to a working mirror if needed.

    The first call probes the mirrors with `select_simbad_mirror`. After a success the answer is
    remembered for the rest of the session. After a failure it is remembered for
    `SIMBAD_RECHECK_SECONDS`, so a long session notices when SIMBAD comes back without
    probing on every call.

    Returns
    -------
    bool
        True if a SIMBAD mirror is reachable.
    """
    if _simbad_status is not None:
        mirror, checked = _simbad_status
        if mirror is not None or time.monotonic() - checked < SIMBAD_RECHECK_SECONDS:
            return mirror is not None
    return select_simbad_mirror() is not None


def load_astrodb(  # noqa: PLR0913
    db_file,
    data_path="data/",
    recreatedb=True,
    reference_tables=[
        "Publications",
        "Telescopes",
        "Instruments",
        "Versions",
        "PhotometryFilters",
        "Regimes",
        "AssociationList",
        "ParameterList",
        "CompanionList",
        "SourceTypeList",
    ],
    felis_schema=None
):
    """Utility function to load the database

    .. note:: Deprecated in 2.0 and will be removed in future versions.
              `load_astrodb` is deprecated.
              It is replaced by :py:func:`loaders.build_db_from_json` and :py:func:`loaders.read_db_from_file`.

    Parameters
    ----------
    db_file : str
        Name of SQLite file to use
    data_path : str
        Path to data directory; default 'data/'
    recreatedb : bool
        Flag whether or not the database file should be recreated
    reference_tables : list
        List of tables to consider as reference tables.
        Default: Publications, Telescopes, Instruments, Versions, PhotometryFilters
    felis_schema : str
        Path to Felis schema; default None
    """

    db_file_path = Path(db_file)
    db_connection_string = "sqlite:///" + db_file

    # removes the current .db file if one already exists
    if recreatedb and db_file_path.exists():
        os.remove(db_file)

    if not db_file_path.exists():
        # Create database, using Felis if provided
        create_database(db_connection_string, felis_schema=felis_schema)
        # Connect and load the database
        db = Database(db_connection_string, lookup_tables=reference_tables)
        if logger.parent.level <= 10:  # noqa: PLR2004
            db.load_database(data_path, verbose=True)
        else:
            db.load_database(data_path)
    else:
        # if database already exists, connects to it
        db = Database(db_connection_string, lookup_tables=reference_tables)


    logger.warning(
        "load_astrodb is deprecated and will be removed in future versions."
        "Please use build_db_from_json or read_db_from_file instead."
        )

    return db


def internet_connection():
    try:
        socket.getaddrinfo("google.com", 80)
        return True
    except socket.gaierror:
        return False


def check_url_valid(url):
    """
    Check that the URLs in the spectra table are valid.

    :return:
    """

    request_response = requests.head(url, timeout=60)
    status_code = request_response.status_code
    if status_code != 200:  # The website is up if the status code is 200  # noqa: PLR2004
        status = "skipped"  # instead of incrememnting n_skipped, just skip this one
        msg = f"The spectrum location does not appear to be valid: \nspectrum: {url} \nstatus code: {status_code}"
        logger.error(msg)
    else:
        msg = f"The spectrum location appears up: {url}"
        logger.debug(msg)
        status = "added"
    return status


def exit_function(msg, raise_error=True, return_value=None):
    """
    Exit function to handle errors and exceptions

    Parameters
    ----------
    msg: str
        Message to be logged
    raise_error: bool
        Flag to raise an error
    return_value: any
        Value to be returned if raise_error is False

    Returns
    -------

    """
    if raise_error:
        logger.error(msg)
        raise AstroDBError(msg)
    else:
        logger.warning(msg)
        return return_value


def get_db_regime(db, regime: str, raise_error=True):
    """
    Check if a regime is in the Regimes table using ilike matching.
    This minimizes problems with case sensitivity.

    If it is not found or there are multiple matches, raise an error or return None.
    If it is found, return the reference as a string.

    Returns
    -------
    str: The regime found
    None: If the regime is not found or there are multiple matches.
    """
    regime_table = db.query(db.RegimeList).filter(db.RegimeList.c.regime.ilike(regime)).table()

    if len(regime_table) == 1:
        # Warn if the regime found in the database was not exactly the same as the one requested
        if regime_table["regime"][0] != regime:
            msg = f"Regime {regime} matched to {regime_table['regime'][0]}. "
            logger.warning(msg)

        return regime_table["regime"][0]

    # try to match the regime hyphens removed
    if len(regime_table) == 0:
        regime = regime.replace("-", "")
        regime_match = (
            db.query(db.RegimeList)
            .filter(func.replace(func.lower(db.RegimeList.c.regime), "-", "") == regime.lower())
            .table()
        )

        if len(regime_match) == 1:
            msg = f"Regime {regime} matched to {regime_match['regime'][0]}. "
            logger.warning(msg)
            return regime_match["regime"][0]

    if len(regime_table) == 0:
        msg = (
            f"Regime not found in database: {regime}. "
            f"Please add it to the RegimesList table or use an existing regime.\n"
            f"Available regimes:\n {db.query(db.RegimeList).table()}"
        )
    elif len(regime_table) > 1:
        msg = (
            f"Multiple entries for regime {regime} found in database. "
            f"Please check the Regimes table. Matches: {regime_table}"
        )
    else:
        msg = f"Unexpected condition while searching for regime {regime} in database."

    exit_function(msg, raise_error=raise_error, return_value=None)


def check_obs_date(date, raise_error=True):
    """
    Check if the observation date is in a parseable ISO format (YYYY-MM-DD).
    Parameters
    ----------
    date: str
        Observation date

    Returns
    -------
    bool
        True if the date is in parseable ISO format, False otherwise
    """
    try:
        parsed_date = datetime.date.fromisoformat(date)
        logger.debug(f"Observation date {date} is parseable: {parsed_date.strftime('%d %b %Y')}")
        return parsed_date
    except ValueError as e:
        msg = f"Observation date {date} is not parseable as ISO format: {e}"
        result = None
        if raise_error:
            raise AstroDBError(msg)
        else:
            logger.warning(msg)
            return result
