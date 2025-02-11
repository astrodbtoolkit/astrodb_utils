"""Utils functions for use in ingests."""

import logging
import os
import socket
from pathlib import Path

import astropy.units as u
import requests
import sqlalchemy.exc
from astrodbkit.astrodb import Database, create_database
from astropy.coordinates import SkyCoord
from astropy.table import Table
from astroquery.simbad import Simbad
from numpy import ma
from sqlalchemy import and_

from .publications import find_publication

__all__ = [
    "AstroDBError",
    "load_astrodb",
    "find_source_in_db",
    "internet_connection",
    "ingest_names",
    "ingest_source",
    "ingest_instrument",
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


def find_source_in_db(
    db,
    source,
    *,
    ra=None,
    dec=None,
    search_radius=60.0,
    ra_col_name="ra_deg",
    dec_col_name="dec_deg",
    use_simbad=True,
):
    """
    Find a source in the database given a source name and optional coordinates.

    Parameters
    ----------
    db
    source: str
        Source name
    ra: float
        Right ascensions of sources. Decimal degrees.
    dec: float
        Declinations of sources. Decimal degrees.
    search_radius
        radius in arcseconds to use for source matching
    ra_col_name: str
        Name of the column in the database table that contains the right ascension
    dec_col_name: str
        Name of the column in the database table that contains the declination
    use_simbad: bool
        Use Simbad to resolve the source name if it is not found in the database. Default is True. 
        Set to False if no internet connection.

    Returns
    -------
    List of strings.

    one match: Single element list with one database source name
    multiple matches: List of possible database names
    no matches: Empty list

    """

    source = source.strip()

    logger.debug(f"{source}: Searching for match in database. Use Simbad: {use_simbad}")
    db_name_matches = db.search_object(
        source, output_table="Sources", fuzzy_search=False, verbose=False, resolve_simbad=use_simbad
    )

    # NO MATCHES
    # If no matches, try fuzzy search
    if len(db_name_matches) == 0:
        logger.debug(f"{source}: No name matches, trying fuzzy search")
        db_name_matches = db.search_object(
            source, output_table="Sources", fuzzy_search=True, verbose=False, resolve_simbad=use_simbad
        )

    # If still no matches, try to resolve the name with Simbad
    if len(db_name_matches) == 0 and use_simbad:
        logger.debug(f"{source}: No name matches, trying Simbad search. use_simbad: {use_simbad}")
        db_name_matches = db.search_object(
            source, resolve_simbad=True, fuzzy_search=False, verbose=False
        )

    # if still no matches, try spatial search using coordinates, if provided
    if len(db_name_matches) == 0 and ra and dec:
        location = SkyCoord(ra, dec, frame="icrs", unit="deg")
        radius = u.Quantity(search_radius, unit="arcsec")
        logger.debug(
            f"{source}: Trying coord in database search around "
            f"{location.ra.degree}, {location.dec}"
        )
        db_name_matches = db.query_region(
            location, radius=radius, ra_col=ra_col_name, dec_col=dec_col_name
        )

    # If still no matches, try to get the coords from SIMBAD using source name
    if len(db_name_matches) == 0 and use_simbad:
        simbad_skycoord = coords_from_simbad(source)
        # Search database around that coordinate
        if simbad_skycoord is not None:
            radius = u.Quantity(search_radius, unit="arcsec")
            msg2 = (
                f"Finding sources around {simbad_skycoord} with radius {radius} "
                f"using ra_col_name: {ra_col_name}, dec_col_name: {dec_col_name}"
            )
            logger.debug(msg2)
            db_name_matches = db.query_region(
                simbad_skycoord, radius=radius, ra_col=ra_col_name, dec_col=dec_col_name
            )

    if len(db_name_matches) == 1:
        db_names = db_name_matches["source"].tolist()
        logger.debug(f"One match found for {source}: {db_names[0]}")
    elif len(db_name_matches) > 1:
        db_names = db_name_matches["source"].tolist()
        logger.debug(f"More than one match found for {source}: {db_names}")
        # TODO: Find way for user to choose correct match
    elif len(db_name_matches) == 0:
        db_names = []
        logger.debug(f" {source}: No match found")
    else:
        raise AstroDBError(f"Unexpected condition searching for {source}")

    return db_names


def coords_from_simbad(source):
    """
    Get coordinates from SIMBAD using a source name

    Parameters
    ----------
    source: str
        Name of the source

    Returns
    ------- 
    SkyCoord object

    """
    simbad_result_table = Simbad.query_object(source)   
    if simbad_result_table is None:
        logger.debug(f"SIMBAD returned no results for {source}")
        simbad_skycoord = None
    elif len(simbad_result_table) == 1:
        logger.debug(f"simbad colnames: {simbad_result_table.colnames} \n simbad results \n {simbad_result_table}")
        if 'RA' in simbad_result_table.colnames: # for astroquery<0.4.7
            ra_col_name_simbad = 'RA'
            dec_col_name_simbad = 'DEC'
        elif 'ra' in simbad_result_table.colnames: # for astroquery >=0.4.8
            ra_col_name_simbad = 'ra'
            dec_col_name_simbad = 'dec'
        simbad_coords = f"{simbad_result_table[ra_col_name_simbad][0]} {simbad_result_table[dec_col_name_simbad][0]}"
        logger.debug(f"SIMBAD coord string: {simbad_coords}")
        simbad_skycoord = SkyCoord(simbad_coords, unit=(u.hourangle, u.deg))
        ra = simbad_skycoord.to_string(style="decimal").split()[0]
        dec = simbad_skycoord.to_string(style="decimal").split()[1]
        msg = f"Coordinates retrieved from SIMBAD {ra}, {dec}"
        logger.debug(msg)
    else:
        simbad_skycoord = None
        msg = f"More than one match found in SIMBAD for {source}"
        logger.warning(msg)
    
    return simbad_skycoord



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


# NAMES
def ingest_names(
    db, source: str = None, other_name: str = None, raise_error: bool = None
):
    """
    This function ingests an other name into the Names table

    Parameters
    ----------
    db: astrodbkit.astrodb.Database
        Database object created by astrodbkit
    source: str
        Name of source as it appears in sources table
    other_name: str
        Name of the source different than that found in source table
    raise_error: bool
        Raise an error if name was not ingested

    Returns
    -------
    None
    """
    names_data = [{"source": source, "other_name": other_name}]
    try:
        with db.engine.connect() as conn:
            conn.execute(db.Names.insert().values(names_data))
            conn.commit()
        logger.info(f"Name added to database: {names_data}\n")
    except sqlalchemy.exc.IntegrityError as e:
        msg = f"Could not add {names_data} to Names."
        if "UNIQUE constraint failed:" in str(e):
            msg += " Other name is already present."
        if raise_error:
            raise AstroDBError(msg) from e
        else:
            logger.warning(msg)


# SOURCES
def ingest_source(
    db,
    source,
    *,
    reference: str = None,
    ra: float = None,
    dec: float = None,
    epoch: str = None,
    equinox: str = None,
    other_reference: str = None,
    comment: str = None,
    raise_error: bool = True,
    search_db: bool = True,
    ra_col_name: str = "ra_deg",
    dec_col_name: str = "dec_deg",
    epoch_col_name: str = "epoch_year",
    use_simbad: bool = True,
):
    """
    Parameters
    ----------
    db: astrodbkit.astrodb.Database
        Database object created by astrodbkit
    source: str
        Names of sources
    reference: str
        Discovery references of sources
    ra: float, optional
        Right ascensions of sources. Decimal degrees.
    dec: float, optional
        Declinations of sources. Decimal degrees.
    comment: string, optional
        Comments
    epoch: str, optional
        Epochs of coordinates
    equinoxe: str, optional
        Equinoxes of coordinates
    other_references: str
    raise_error: bool, optional
        True (default): Raise an error if a source cannot be ingested
        False: Log a warning but skip sources which cannot be ingested
    search_db: bool, optional
        True (default): Search database to see if source is already ingested
        False: Ingest source without searching the database
    ra_col_name: str
        Name of the column in the database table that contains the right ascension
    dec_col_name: str
        Name of the column in the database table that contains the declination
    use_simbad: bool
        True (default): Use Simbad to resolve the source name if it is not found in the database
        False: Do not use Simbad to resolve the source name.

    Returns
    -------

    None

    """

    # Find out if source is already in database or not
    if search_db:
        logger.debug(f"Checking database for: {source} at ra: {ra}, dec: {dec}")
        logger.debug(f" colnames: {ra_col_name}, {dec_col_name}")
        name_matches = find_source_in_db(
            db,
            source,
            ra=ra,
            dec=dec,
            ra_col_name=ra_col_name,
            dec_col_name=dec_col_name,
            use_simbad=use_simbad,
        )
    else:
        name_matches = []

    logger.debug(f"Source matches in database: {name_matches}")

    # Source is already in database
    # Checking out alternate names
    if len(name_matches) == 1 and search_db:
        # Figure out if source name provided is an alternate name
        db_source_matches = db.search_object(
            source, output_table="Sources", resolve_simbad=use_simbad, fuzzy_search=False, 
        )

        # Try to add alternate source name to Names table
        if len(db_source_matches) == 0:
            alt_names_data = [{"source": name_matches[0], "other_name": source}]
            try:
                with db.engine.connect() as conn:
                    conn.execute(db.Names.insert().values(alt_names_data))
                    conn.commit()
                logger.info(f"   Name added to database: {alt_names_data}\n")
            except sqlalchemy.exc.IntegrityError as e:
                msg = f"   Could not add {alt_names_data} to database"
                logger.warning(msg)
                if raise_error:
                    raise AstroDBError(msg) from e
                else:
                    return

        msg = f"Not ingesting {source}. Already in database as {name_matches[0]}. \n "
        if raise_error:
            raise AstroDBError(msg)
        else:
            logger.info(msg)
            return  # Source is already in database, nothing new to ingest

    # Multiple source matches in the database so unable to ingest source
    elif len(name_matches) > 1 and search_db:
        msg1 = f"   Not ingesting {source}."
        msg = f"   More than one match for {source}\n {name_matches}\n"
        logger.warning(msg1 + msg)
        if raise_error:
            raise AstroDBError(msg)
        else:
            return

    #  No match in the database, INGEST!
    elif len(name_matches) == 0 or not search_db:
        # Make sure reference is provided and in References table
        if reference is None or ma.is_masked(reference):
            msg = f"Not ingesting {source}. Discovery reference is blank. \n"
            logger.warning(msg)
            if raise_error:
                raise AstroDBError(msg)
            else:
                return

        ref_check = find_publication(db, reference=reference)
        logger.debug(f"ref_check: {ref_check}")

        if ref_check[0] is False:
            msg = (
                f"Skipping: {source}. Discovery reference {reference} "
                "is not in Publications table. \n"
                f"(Add it with ingest_publication function.)"
            )
            logger.warning(msg)
            if raise_error:
                raise AstroDBError(msg)
            else:
                return

        # Try to get coordinates from SIMBAD if they were not provided
        if (ra is None or dec is None) and use_simbad:
            # Try to get coordinates from SIMBAD
            simbad_skycoord = coords_from_simbad(source)

            if simbad_skycoord is None:
                msg = f"Not ingesting {source}. Coordinates are needed and could not be retrieved from SIMBAD. \n"
                logger.warning(msg)
                if raise_error:
                    raise AstroDBError(msg)
                else:
                    return
            # One SIMBAD match! Using those coordinates for source.
            else:
                ra = simbad_skycoord.to_string(style="decimal").split()[0]
                dec = simbad_skycoord.to_string(style="decimal").split()[1]
                epoch = "2000"  # Default coordinates from SIMBAD are epoch 2000.
                equinox = "J2000"  # Default frame from SIMBAD is IRCS and J2000.
                msg = f"Coordinates retrieved from SIMBAD {ra}, {dec}"
                logger.debug(msg)
            
    # Just in case other conditionals not met
    else:
        msg = f"Unexpected condition encountered ingesting {source}"
        logger.error(msg)
        raise AstroDBError(msg)

    logger.debug(f"   Ingesting {source}.")

    # Construct data to be added
    source_data = [
        {
            "source": source,
            ra_col_name: ra,
            dec_col_name: dec,
            "reference": reference,
            epoch_col_name: epoch,
            "equinox": equinox,
            "other_references": other_reference,
            "comments": comment,
        }
    ]
    logger.debug(f"   Data: {source_data}.")
    names_data = [{"source": source, "other_name": source}]

    # Try to add the source to the database
    try:
        with db.engine.connect() as conn:
            conn.execute(db.Sources.insert().values(source_data))
            conn.commit()
        msg = f"Added {source_data}"
        logger.info(f"Added {source}")
        logger.debug(msg)
    except sqlalchemy.exc.IntegrityError as e:
        msg = (
            f"Not ingesting {source}. Not sure why. \n"
            "The reference may not exist in Publications table. \n"
            "Add it with ingest_publication function. \n"
        )
        msg2 = f"   {source_data} "
        logger.warning(msg)
        logger.debug(msg2)
        if raise_error:
            raise AstroDBError(msg + msg2) from e
        else:
            return

    # Try to add the source name to the Names table
    try:
        with db.engine.connect() as conn:
            conn.execute(db.Names.insert().values(names_data))
            conn.commit()
        logger.debug(f"    Name added to database: {names_data}\n")
    except sqlalchemy.exc.IntegrityError as e:
        msg = f"   Could not add {names_data} to database"
        logger.warning(msg)
        if raise_error:
            raise AstroDBError(msg) from e
        else:
            return

    return


# SURVEY DATA
def find_survey_name_in_simbad(sources, desig_prefix, source_id_index=None):
    """
    Function to extract source designations from SIMBAD

    Parameters
    ----------
    sources: astropy.table.Table
        Sources names to search for in SIMBAD
    desig_prefix
        prefix to search for in list of identifiers
    source_id_index
        After a designation is split, this index indicates source id suffix.
        For example, source_id_index = 2 to extract suffix from "Gaia DR2" designations.
        source_id_index = 1 to exctract suffix from "2MASS" designations.
    Returns
    -------
    Astropy table
    """

    n_sources = len(sources)

    Simbad.reset_votable_fields()
    Simbad.add_votable_fields("typed_id")  # keep search term in result table
    Simbad.add_votable_fields("ids")  # add all SIMBAD identifiers as an output column

    logger.info("simbad query started")
    result_table = Simbad.query_objects(sources["source"])
    logger.info("simbad query ended")

    ind = result_table["SCRIPT_NUMBER_ID"] > 0  # find indexes which contain results
    simbad_ids = result_table["TYPED_ID", "IDS"][ind]

    db_names = []
    simbad_designations = []
    source_ids = []

    for row in simbad_ids:
        db_name = row["TYPED_ID"]
        ids = row["IDS"].split("|")
        designation = [i for i in ids if desig_prefix in i]

        if designation:
            logger.debug(f"{db_name}, {designation[0]}")
            db_names.append(db_name)
            if len(designation) == 1:
                simbad_designations.append(designation[0])
            else:
                simbad_designations.append(designation[0])
                logger.warning(f"more than one designation matched, {designation}")

            if source_id_index is not None:
                source_id = designation[0].split()[source_id_index]
                source_ids.append(int(source_id))  # convert to int since long in Gaia

    n_matches = len(db_names)
    logger.info(
        f"Found, {n_matches}, {desig_prefix}, sources for, {n_sources}, sources"
    )

    if source_id_index is not None:
        result_table = Table(
            [db_names, simbad_designations, source_ids],
            names=("db_names", "designation", "source_id"),
        )
    else:
        result_table = Table(
            [db_names, simbad_designations], names=("db_names", "designation")
        )

    return result_table


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
