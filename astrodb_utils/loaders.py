
import logging
import os
import tomllib

from astrodbkit.astrodb import Database, create_database

from astrodb_utils.utils import AstroDBError

__all__ = [
    "build_db_from_json",
    "check_database_settings",
    "read_database_settings",
    "read_db_from_file"
]

logger = logging.getLogger(__name__)


def build_db_from_json(  # noqa: PLR0913
    toml_file: str = "database.toml",
    *,
    db_path: str = None,
    db_name: str = None,
    felis_path: str = None,
    data_path: str = None,
    lookup_tables: list = None,
):
    """Build an SQLite database from JSON files.

    Default is to get the database settings from a toml file.
    Creates the database .sqlite file in the current directory.
    If a database file with the same name already exists, it is removed.

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

    Yields
    ------
    .sqlite database file in the current directory

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
    db_path : str, optional
        Path to the directory containing the database .sqlite file
        Default: None, assumes database file is in current directory

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

