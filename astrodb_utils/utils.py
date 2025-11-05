"""Utils functions for use in ingests."""

import datetime
import logging
import os
import socket
import tomllib
from pathlib import Path

import requests
from astrodbkit.astrodb import Database, create_database
from sqlalchemy import func

__all__ = [
    "load_astrodb",
    "build_db_from_json",
    "check_database_settings",
    "read_database_settings",
    "read_db_from_file",
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
        db = Database(db_connection_string, reference_tables=reference_tables)
        if logger.parent.level <= 10:
            db.load_database(data_path, verbose=True)
        else:
            db.load_database(data_path)
    else:
        # if database already exists, connects to it
        db = Database(db_connection_string, reference_tables=reference_tables)


    logger.warning(
        "load_astrodb is deprecated and will be removed in future versions."
        "Please use build_db_from_json or read_db_from_file instead."
        )

    return db


def check_database_settings(toml_file: str = "database.toml", db_path: str = None) -> bool:
    if db_path is not None:
        toml_path = os.path.join(db_path, toml_file)
    else:
        toml_path = toml_file

    settings = read_database_settings(toml_path)
    if db_path is not None:
        settings["db_path"] = db_path
    else:
        settings["db_path"] = "./"

    _check_felis_path(settings)
    _check_data_path(settings)
    _load_lookup_tables(settings)

    return True


def read_database_settings(toml_file: str = "database.toml", db_path: str = None) -> dict:
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


def build_db_from_json(  # noqa: PLR0913
    toml_file: str = "database.toml",
    *,
    db_path: str = None,
    db_name: str = None,
    felis_path: str = None,
    data_path: str = None,
    lookup_tables: list = None,
):
    """Build an SQLite database from the schema and JSON files.
        Creates the database file if it does not exist.
        If the database file already exists, it removes the existing database file before creating a new one

    Inputs
    ------
    toml_file : str
        Name of the toml file containing the database settings
        Default: database.toml
    db_path : str
        Path to the directory containing the toml file
        Default: None, assumes toml file is in current directory
    db_name : str
        Name of the database file (without .sqlite extension)
        Default: None, reads from toml file
    felis_path : str
        Path to the Felis schema file
        Default: None, reads from toml file
    data_path : str
        Path to the data directory containing the JSON files
        Default: None, reads from toml file
    lookup_tables : list
        List of tables to consider as lookup tables.
        Default: None, reads from toml file 


    Returns
    -------
    db : Astrodbkit Database object
    """

    db_name, felis_path, data_path, lookup_tables = _validate_db_settings(
        toml_file, db_path, db_name, felis_path, data_path, lookup_tables
    )

    db_file = db_name + ".sqlite"

    if os.path.exists(db_file):
        os.remove(db_file)
        msg = f"Removed old database file {db_file}."
        logger.info(msg)

    logger.info(f"Creating new database file: {db_file}")
    db_connection_string = "sqlite:///" + db_file

    # Create database
    create_database(db_connection_string, felis_schema=felis_path)

    # Connect and load the database
    db = Database(db_connection_string, reference_tables=lookup_tables)

    if logger.parent.level <= 10:  # noqa: PLR2004
        db.load_database(data_path, verbose=True)
    else:
        db.load_database(data_path)

    return db


def read_db_from_file(db_name: str, db_path: str = None):
    """Read an SQLite database from a file.

    Parameters
    ----------
    db_name : str
        Name of the database file (without .sqlite extension)
    db_path : str (optional)
        Path to the directory containing the database .sqlite file

    Returns
    -------
    db : Astrodbkit Database object
    """
    if db_path is not None:
        db_file = os.path.join(db_path, db_name + ".sqlite")
    else:
        db_file = db_name + ".sqlite"

    db_connection_string = "sqlite:///" + db_file
    logger.debug(f"Database connection string: {db_connection_string}")

    db = Database(db_connection_string)
    return db


def _validate_db_settings(toml_file, db_path, db_name, felis_path, data_path, lookup_tables):  # noqa: PLR0913
    if db_path is not None:
        toml_path = os.path.join(db_path, toml_file)
    else:
        toml_path = toml_file

    try:
        settings = read_database_settings(toml_path)
    except AstroDBError as e:
        raise e

    if db_path is not None:
        settings["db_path"] = db_path
        if not os.path.exists(db_path):
            raise AstroDBError(f"Database path {db_path} does not exist.")
    else:
        settings["db_path"] = "./"

    if db_name is None:
        db_name = settings["db_name"]

    # Check the Felis schema path
    if felis_path is None:
        felis_path = settings["felis_path"]
    felis_path = _check_felis_path(settings)

    # Check the lookup tables
    if lookup_tables is None:
        lookup_tables = _load_lookup_tables(settings)

    # check the data_path
    if data_path is None:
        data_path = settings["data_path"]
    data_path = _check_data_path(settings)

    return db_name, felis_path, data_path, lookup_tables


def _check_felis_path(settings):
    try:
        felis_path = os.path.join(settings["db_path"], settings["felis_path"])
    except KeyError:
        felis_path = "schema.yaml"
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
        data_path = os.path.join(settings["db_path"], settings["data_path"])
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
