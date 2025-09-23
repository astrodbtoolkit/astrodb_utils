"""Utils functions for use in ingests."""

import datetime
import importlib
import logging
import os
import socket
import tomllib

import requests
from astrodbkit.astrodb import Database, create_database
from sqlalchemy import func

__all__ = [
    "load_astrodb",
    "build_db_from_json",
    "check_database_settings",
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

def check_database_settings(toml_file: str = "database.toml", db_path: str = None) -> bool:
    if db_path is not None:
        toml_path = os.path.join(db_path, toml_file)
    else:
        toml_path = toml_file

    settings = _read_database_settings(toml_path)
    if db_path is not None:
        settings['db_path'] = db_path
    else:
        settings['db_path'] = './'
    print(settings)

    _check_felis_path(settings)
    _check_data_path(settings)
    _load_lookup_tables(settings)

    return True


def _read_database_settings(toml_file: str = "database.toml", db_path: str = None) -> dict:
    """Read database settings from a toml file

    Parameters
    ----------
    toml_file : str
        Path to the toml file containing the database settings
        Default: database_settings.toml


    Returns
    -------
    dict
        Dictionary containing the database settings

    Raises
    ------
    AstroDBError
        If the toml file does not exist or cannot be read
    """

    if not os.path.exists(toml_file):
        msg = f"Could not find database settings file: {toml_file}"
        logger.error(msg)
        raise AstroDBError(msg)

    with open(toml_file, "rb") as f:
        try:
            settings = tomllib.load(f)
        except Exception as e:
            msg = f"Could not read database settings file: {toml_file}, error: {e}"
            logger.error(msg)
            raise AstroDBError(msg)

    return settings


def load_astrodb(
    toml_file: str = "database.toml",
    db_name: str = None,
    data_path: str = None,
    recreatedb=True,
    lookup_tables=None,
    felis_path=None
):
    """Utility function to load the database

    Parameters
    ----------
    db_name : str
        This name is used to name the database file, e.g. 'stars' will create 'stars.sqlite'
    data_path : str
        Path to data directory; default 'data/'
    recreatedb : bool
        Flag whether or not the database file should be recreated
    lookup_tables : list
        List of tables to consider as lookup tables.
        Default: Publications, Telescopes, Instruments, Versions, PhotometryFilters
        Looks in database.toml for the list of tables.
    felis_path : str
        Path to Felis schema; default None
        Looks in database.toml for the schema path.

    Returns
    -------
    db : Astrodbkit Database object

    Also creates the database file if it does not exist.
    If recreatedb is True, it removes the existing database file before creating a new one.
    """

    # Read the database settings from the toml file
    try:
        settings = _read_database_settings(toml_file)
    except AstroDBError as e:
        raise e

    if db_name is None:
        db_name = settings['db_name']

    db_file = db_name + ".sqlite"
    db_connection_string = "sqlite:///" + db_file
    logger.debug(f"Database connection string: {db_connection_string}")

    # Load the lookup tables from the db_name module if not provided
    if lookup_tables is None:
        lookup_tables = _load_lookup_tables(settings)

    # removes the current .db file if one already exists and Recreatedb is True
    if recreatedb and os.path.exists(db_file):
        os.remove(db_file)

    if not os.path.exists(db_file):
        db = build_db_from_json(db_name=db_name, felis_path=felis_path, data_path=data_path, lookup_tables=lookup_tables)
    else:
        # if database file already exists, just connect to it
        db = Database(db_connection_string, lookup_tables=lookup_tables)

    return db


def build_db_from_json(
    toml_file: str = "database.toml",
    db_path: str = None,
    db_name: str = None,
    felis_path: str = None,
    data_path: str = None,
    lookup_tables: list = None
):
    """Build the database from the schema and JSON files.
    Called by load_astrodb if the database file does not exist or recreatedb is True.

    Returns
    -------
    db : Astrodbkit Database object
    """

    if db_path is not None:
        toml_path = os.path.join(db_path, toml_file)
    else:
        toml_path = toml_file

    try:
        settings = _read_database_settings(toml_path)
    except AstroDBError as e:
        raise e

    if db_path is not None:
        settings['db_path'] = db_path
    else:
        settings['db_path'] = './'

    if db_name is None:
        db_name = settings['db_name']

    db_file = db_name + ".sqlite"

    if os.path.exists(db_file):
        os.remove(db_file)
        msg = f"Removed old database file {db_file}."
        logger.info(msg)

    logger.info(f"Creating new database file: {db_file}")
    db_connection_string = "sqlite:///" + db_file

    # Check the Felis schema path
    if felis_path is None:
        felis_path = settings['felis_path']
    felis_path = _check_felis_path(settings)

    # Create database
    create_database(db_connection_string, felis_schema=felis_path)

    # Check the lookup tables
    if lookup_tables is None:
        lookup_tables = _load_lookup_tables(settings)

    # Connect and load the database
    db = Database(db_connection_string, reference_tables=lookup_tables)

    # check the data_path
    if data_path is None:
        data_path = settings['data_path']
    data_path = _check_data_path(settings)

    if logger.parent.level <= 10:  # noqa: PLR2004
        db.load_database(data_path, verbose=True)
    else:
        db.load_database(data_path)

    return db


def _check_felis_path(settings):
    try:
        felis_path = os.path.join(settings['db_path'], settings['felis_path'])
    except KeyError:
        felis_path = "schema/schema.yaml"
    if not os.path.exists(felis_path):  # Check if the felis schema file exists
        msg = (
            f"Could not find Felis schema in {felis_path}. "
            "Please provide a valid path to the felis schema.yaml file "
            "in the felis_path key of the database settings toml file."
        )
        logger.error(msg)
        raise AstroDBError(msg)

    return felis_path


def _check_data_path(settings):
    try:
        data_path = os.path.join(settings['db_path'], settings['data_path'])
    except KeyError:
        data_path = "data/"
    if not os.path.exists(data_path):
        logger.debug(f"Data path {data_path} does not exist. Looking for it in data/.")
        data_path = "data/"
        if os.path.exists(data_path):
            logger.debug(f"Using data path: {data_path}")
        else:
            msg = f"Data path {data_path} does not exist. Please provide a valid data path."
            logger.error(msg)
            raise AstroDBError(msg)
    return data_path


def _load_lookup_tables(settings):
    try:
        lookup_tables = settings["lookup_tables"]
    except KeyError:
        lookup_tables = [
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

    return lookup_tables




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
    if status_code != 200:  # The website is up if the status code is 200  # noqa: PLR2004
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

