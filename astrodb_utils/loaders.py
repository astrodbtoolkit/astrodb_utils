import logging
import os
import tomllib
from dataclasses import dataclass

from astrodbkit.astrodb import Database, create_database

from astrodb_utils.utils import AstroDBError

__all__ = [
    "build_db_from_json",
    "read_db_from_file",
    "DatabaseSettings",
]

logger = logging.getLogger(__name__)


@dataclass
class DatabaseSettings:
    settings_file: str = "database.toml"
    base_path: str = "."
    db_name: str = None
    felis_path: str = None
    data_path: str = None
    lookup_tables: list = None

    def __post_init__(self):
        # Use a base_path if provided, otherwise default to the current directory
        if self.base_path is None:
            self.base_path = "."
        self.settings_file = os.path.join(self.base_path, self.settings_file)
        self.settings_file = self._check_path(self.settings_file)

        # Read the settings file
        self.settings = self._read_settings()

        # Prepare and check the Felis path
        if self.felis_path is not None:
            self.felis_path = os.path.join(self.base_path, "schema.yaml")
        else:
            self.felis_path = os.path.join(self.base_path, self.settings["felis_path"])
        self.felis_path = self._check_path(self.felis_path)

        # Prepare and check the data path
        if self.data_path is not None:
            self.data_path = os.path.join(self.base_path, "data")
        else:
            self.data_path = os.path.join(self.base_path, self.settings["data_path"])
        self.data_path = self._check_path(self.data_path)

        # Prepare and check the lookup tables
        if self.lookup_tables is not None:
            self.lookup_tables = [
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
        else:
            self.lookup_tables = self.settings["lookup_tables"]

        # Prepare and check the database name
        if self.db_name is None:
            self.db_name = self.settings["db_name"]

    def _check_path(self, path):
        if not os.path.exists(path):
            raise AstroDBError(f"{path} does not exist.")
        return path

    def _read_settings(self):
        with open(self.settings_file, "rb") as f:
            settings = tomllib.load(f)
        return settings


def build_db_from_json(  # noqa: PLR0913
    settings_file: str = "database.toml",
    *,
    base_path: str = ".",
    db_name: str = None,
    felis_path: str = None,
    data_path: str = None,
    lookup_tables: list = None,
):
    """Build an SQLite database from JSON files.

    Default is to get the database settings from a TOML settings file.
    Creates the database .sqlite file in the current directory.
    If a database file with the same name already exists, it is removed.
    This creates a .sqlite database file.

    Inputs
    ------
    settings_file : str
        Name of the TOML file containing the database settings
        Default: database.toml
    base_path : str
        Path to the directory containing the TOML file
        Default: None, assumes TOML file is in current directory
    db_name : str
        Name of the database file (without .sqlite extension)
        Default: None, reads from TOML file
    felis_path : str
        Path to the Felis schema file
        Default: None, reads from TOML file
    data_path : str
        Path to the data directory containing the JSON files
        Default: None, reads from TOML file
    lookup_tables : list
        List of tables to consider as lookup tables.
        Default: None, reads from TOML file


    Returns
    -------
    db : astrodbkit.astrodb.Database
        Astrodbkit Database object
    """

    # Read and validate the database settings
    db_settings = DatabaseSettings(
        settings_file=settings_file,
        base_path=base_path,
        db_name=db_name,
        felis_path=felis_path,
        data_path=data_path,
        lookup_tables=lookup_tables,
    )

    db_file = db_settings.db_name + ".sqlite"

    if os.path.exists(db_file):
        os.remove(db_file)
        msg = f"Removed old database file {db_file}."
        logger.info(msg)

    logger.info(f"Creating new database file: {db_file}")
    db_connection_string = "sqlite:///" + db_file

    # Create database
    create_database(db_connection_string, felis_schema=db_settings.felis_path)

    # Connect and load the database
    db = Database(db_connection_string, reference_tables=db_settings.lookup_tables)

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
    db : astrodbkit.astrodb.Database
        Astrodbkit Database object
    """
    if db_path is not None:
        db_file = os.path.join(db_path, db_name + ".sqlite")
    else:
        db_file = db_name + ".sqlite"

    db_connection_string = "sqlite:///" + db_file
    logger.debug(f"Database connection string: {db_connection_string}")

    db = Database(db_connection_string)
    return db
