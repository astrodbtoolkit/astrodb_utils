"""Utils functions for use in ingests."""

import logging
import os
import socket
from pathlib import Path

import requests
import sqlalchemy.exc
from astrodbkit.astrodb import Database, create_database
from sqlalchemy import and_

__all__ = [
    "AstroDBError",
    "load_astrodb",
    "internet_connection",
    "ingest_instrument",
    "exit_function",
]

logger = logging.getLogger('astrodb_utils')

class AstroDBError(Exception):
    """Custom error for AstroDB"""


def load_astrodb(
    db_file,
    data_path="data/",
    recreatedb=True,
    reference_tables=[
        "Publications",
        "Telescopes",
        "Instruments",
        "Versions",
        "PhotometryFilters",
        "Regimes"
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
        db.load_database(data_path)
    else:
        # if database already exists, connects to it
        db = Database(db_connection_string, reference_tables=reference_tables)

    return db


def internet_connection():
    """Test internet connection - not clear if that's actually what's happening here"""

    # get current IP address of system
    ipaddress = socket.gethostbyname(socket.gethostname())

    # checking system IP is the same as "127.0.0.1" or not.
    if ipaddress == "127.0.0.1":  # no internet
        return False, ipaddress
    else:
        return True, ipaddress


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


def ingest_instrument(db, *, telescope=None, instrument=None, mode=None):
    """
    Script to ingest instrumentation
    TODO: Add option to ingest references for the telescope and instruments

    Parameters
    ----------
    db: astrodbkit.astrodb.Database
        Database object created by astrodbkit
    telescope: str
    instrument: str
    mode: str

    Returns
    -------

    None

    """

    # Make sure enough inputs are provided
    if telescope is None and (instrument is None or mode is None):
        msg = "Telescope, Instrument, and Mode must be provided"
        logger.error(msg)
        raise AstroDBError(msg)

    msg_search = f"Searching for {telescope}, {instrument}, {mode} in database"
    logger.info(msg_search)

    # Search for the inputs in the database
    telescope_db = (
        db.query(db.Telescopes).filter(db.Telescopes.c.telescope == telescope).table()
    )
    mode_db = (
        db.query(db.Instruments)
        .filter(
            and_(
                db.Instruments.c.mode == mode,
                db.Instruments.c.instrument == instrument,
                db.Instruments.c.telescope == telescope,
            )
        )
        .table()
    )

    if len(telescope_db) == 1 and len(mode_db) == 1:
        msg_found = (
            f"{telescope}, {instrument}, and {mode} are already in the database."
        )
        logger.info(msg_found)
        return

    # Ingest telescope entry if not already present
    if telescope is not None and len(telescope_db) == 0:
        telescope_add = [{"telescope": telescope}]
        try:
            with db.engine.connect() as conn:
                conn.execute(db.Telescopes.insert().values(telescope_add))
                conn.commit()
            msg_telescope = f"{telescope} was successfully ingested in the database"
            logger.info(msg_telescope)
        except sqlalchemy.exc.IntegrityError as e:  # pylint: disable=invalid-name
            msg = "Telescope could not be ingested"
            logger.error(msg)
            raise AstroDBError(msg) from e

    # Ingest instrument+mode (requires telescope) if not already present
    if (
        telescope is not None
        and instrument is not None
        and mode is not None
        and len(mode_db) == 0
    ):
        instrument_add = [
            {"instrument": instrument, "mode": mode, "telescope": telescope}
        ]
        try:
            with db.engine.connect() as conn:
                conn.execute(db.Instruments.insert().values(instrument_add))
                conn.commit()
            msg_instrument = f"{instrument} was successfully ingested in the database."
            logger.info(msg_instrument)
        except sqlalchemy.exc.IntegrityError as e:  # pylint: disable=invalid-name
            msg = "Instrument/Mode could not be ingested"
            logger.error(msg)
            raise AstroDBError(msg) from e

    return


def exit_function(msg, raise_error=True):
    """
    Exit function to handle errors and exceptions

    Parameters
    ----------
    msg: str
        Message to be logged
    raise_error: bool
        Flag to raise an error

    Returns
    -------

    """
    if raise_error:
        raise AstroDBError(msg)
    else:
        logger.warning(msg)
        return