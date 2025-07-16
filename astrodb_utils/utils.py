"""Utils functions for use in ingests."""

import datetime
import importlib
import logging
import os
import socket

import requests
from astrodbkit.astrodb import Database, create_database
from sqlalchemy import func

__all__ = [
    "load_astrodb",
    "internet_connection",
    "exit_function",
    "get_db_regime",
    "AstroDBError",
    "check_obs_date",
]


class AstroDBError(Exception):
    """Custom error for AstroDB"""


logger = logging.getLogger(__name__)
msg = f"logger.parent.name: {logger.parent.name}, logger.parent.level: {logger.parent.level}"
logger.debug(msg)


def load_astrodb(
    db_path,
    data_path="data/",
    recreatedb=True,
    reference_tables=None,
    felis_schema=None
):
    """Utility function to load the database

    Parameters
    ----------
    db_path : str
        Path to the directory containing the __init__.py and schema.yaml file for the database
        This name is used to name the database file, e.g. 'stars' will create 'stars.sqlite'
    data_path : str
        Path to data directory; default 'data/'
    recreatedb : bool
        Flag whether or not the database file should be recreated
    reference_tables : list
        List of tables to consider as reference tables.
        Default: Publications, Telescopes, Instruments, Versions, PhotometryFilters
        Looks in <db_name>/__init__.py for the list of tables.
    felis_schema : str
        Path to Felis schema; default None
        Looks in db_name/schema.yaml for the schema path.

    Returns
    -------
    db : Astrodbkit Database object

    Also creates the database file if it does not exist.
    If recreatedb is True, it removes the existing database file before creating a new one.
    """

    # Load the reference tables from the db_name module if not provided
    if reference_tables is None:
        try:
            db_name = os.path.basename(db_path)
            init_path = os.path.join(db_path, "__init__.py")
            spec = importlib.util.spec_from_file_location(db_name, init_path)
            db_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(db_module)
            REFERENCE_TABLES = db_module.REFERENCE_TABLES
        except ImportError:
            logger.warning(f"Could not import reference tables from {db_path}, using default set.")
            REFERENCE_TABLES = [
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
            ]

    # Load the Felis schema if provided
    if felis_schema is None:
        try:
            felis_path = os.path.join(db_path, "schema.yaml")
            os.path.exists(felis_path)  # Check if the schema file exists
        except Exception as e:
            logger.warning(f"Could not load Felis schema from {felis_path}: {e}")
    else:
        felis_path = felis_schema

    db_file = db_name + ".sqlite"
    db_connection_string = "sqlite:///" + db_file
    logger.debug(f"Database connection string: {db_connection_string}")

    # removes the current .db file if one already exists
    if recreatedb and os.path.exists(db_file):
        os.remove(db_file)

    if not os.path.exists(db_file):
        # Create database, using Felis if provided
        create_database(db_connection_string, felis_schema=felis_path)
        # Connect and load the database
        db = Database(db_connection_string, reference_tables=REFERENCE_TABLES)

        # check the data_path
        if not os.path.exists(data_path):
            logger.debug(f"Data path {data_path} does not exist. Looking for it.")
            try:
                data_path = os.path.join(os.path.dirname(db_path), "data")
                os.path.exists(data_path)  # Check if the data path exists
                logger.debug(f"Using data path: {data_path}")
            except Exception as e:
                msg = f"Data path {data_path} does not exist. Please provide a valid data path."
                logger.error(msg)
                raise AstroDBError(msg)

        if logger.parent.level <= 10:
            db.load_database(data_path, verbose=True)
        else:
            db.load_database(data_path)
    else:
        # if database already exists, connects to it
        db = Database(db_connection_string, reference_tables=REFERENCE_TABLES)

    return db


def internet_connection():
    try:
        socket.getaddrinfo('google.com',80)
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
    if status_code != 200:  # The website is up if the status code is 200
        status = "skipped"  # instead of incrememnting n_skipped, just skip this one
        msg = (
            "The spectrum location does not appear to be valid: \n"
            f"spectrum: {url} \n"
            f"status code: {status_code}"
        )
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


def get_db_regime(db, regime:str, raise_error=True):
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
    regime_table = (
        db.query(db.RegimeList).filter(db.RegimeList.c.regime.ilike(regime)).table()
    )

    if len(regime_table) == 1:
        # Warn if the regime found in the database was not exactly the same as the one requested
        if regime_table["regime"][0] != regime:
            msg = (
                f"Regime {regime} matched to {regime_table['regime'][0]}. "
            )
            logger.warning(msg)

        return regime_table["regime"][0]

    # try to match the regime hyphens removed
    if len(regime_table) == 0:
        regime = regime.replace("-", "")
        regime_match = (db.query(db.RegimeList).
            filter(func.replace(func.lower(db.RegimeList.c.regime),"-","") == regime.lower())
            .table())

        if len(regime_match) == 1:
            msg = (
                f"Regime {regime} matched to {regime_match['regime'][0]}. "
            )
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
        logger.debug(
            f"Observation date {date} is parseable: {parsed_date.strftime('%d %b %Y')}"
        )
        return parsed_date
    except ValueError as e:
        msg = f"Observation date {date} is not parseable as ISO format: {e}"
        result = None
        if raise_error:
            raise AstroDBError(msg)
        else:
            logger.warning(msg)
            return result

