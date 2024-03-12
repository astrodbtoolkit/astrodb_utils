"""
Utils functions for use in ingests
"""
import logging
import os
import sys
import re
import warnings
from pathlib import Path
import requests
from astrodbkit2.astrodb import create_database, Database
import numpy.ma as ma
import ads
from astropy.coordinates import SkyCoord
import astropy.units as u
from astropy.table import Table
from sqlalchemy import or_, and_
import sqlalchemy.exc
from astroquery.simbad import Simbad
import socket
# from scripts import REFERENCE_TABLES

__all__ = [
    "AstroDBError",
    "load_astrodb",
    "find_source_in_db",
    "find_publication",
    "ingest_publication",
    "check_internet_connection",
    "ingest_names",
    "ingest_source",
    "ingest_sources",
    "ingest_instrument",
]

warnings.filterwarnings("ignore", module="astroquery.simbad")
logger = logging.getLogger("AstroDB")

# Logger setup
# This will stream all logger messages to the standard output and
# apply formatting for that
logger.propagate = False  # prevents duplicated logging messages
LOGFORMAT = logging.Formatter(
    "%(asctime)s %(levelname)s: %(message)s", datefmt="%m/%d/%Y %I:%M:%S%p"
)
ch = logging.StreamHandler(stream=sys.stdout)
ch.setFormatter(LOGFORMAT)
# To prevent duplicate handlers, only add if they haven't been set previously
if not len(logger.handlers):
    logger.addHandler(ch)
logger.setLevel(logging.INFO)


class AstroDBError(Exception):
    pass


# TODO: commented out as not using with the new custom error
# @contextmanager
# def disable_exception_traceback():
#     """
#     All traceback information is suppressed and only the exception type and value
#       are printed
#     """
#     default_value = getattr(sys, "tracebacklimit", 1000)  # `1000` is a Python's
#                                                             default value
#     sys.tracebacklimit = 0
#     yield
#     sys.tracebacklimit = default_value  # revert changes

#TODO:  Where should these live? 
REFERENCE_TABLES = [
    "Publications",
    "Telescopes",
    "Instruments",
    "Modes",
    "PhotometryFilters",
    "Versions",
    "Parameters",
]


def load_astrodb(db_file, recreatedb=True, reference_tables=REFERENCE_TABLES):
    # Utility function to load the database

    db_file_path = Path(db_file)
    db_connection_string = "sqlite:///" + db_file

    if recreatedb and db_file_path.exists():
        os.remove(db_file)  # removes the current .db file if one already exists

    if not db_file_path.exists():
        try:  # Use fancy in-memory database, if supported by astrodbkit2
            db = Database(
                "sqlite://", reference_tables=REFERENCE_TABLES
            )  # creates and connects to a temporary in-memory database
            db.load_database(
                "data/"
            )  # loads the data from the data files into the database
            db.dump_sqlite(db_file)  # dump in-memory database to file
            db = Database(
                db_connection_string, reference_tables=REFERENCE_TABLES
            )  # replace database object with new file version
        except RuntimeError:
            # use in-file database
            create_database(
                db_connection_string
            )  # creates empty database based on the simple schema
            db = Database(
                db_connection_string, reference_tables=REFERENCE_TABLES
            )  # connects to the empty database
            db.load_database(
                "data/"
            )  # loads the data from the data files into the database
    else:
        db = Database(
            db_connection_string, reference_tables=REFERENCE_TABLES
        )  # if database already exists, connects to .db file

    return db


def find_source_in_db(db, source, ra=None, dec=None, search_radius=60.0):
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

    Returns
    -------
    List of strings.

    one match: Single element list with one database source name
    multiple matches: List of possible database names
    no matches: Empty list

    """

    # TODO: In astrodbkit2, convert verbose to using logger

    if ra and dec:
        coords = True
    else:
        coords = False

    source = source.strip()

    logger.debug(f"{source}: Searching for match in database.")

    db_name_matches = db.search_object(
        source, output_table="Sources", fuzzy_search=False, verbose=False
    )

    # NO MATCHES
    # If no matches, try fuzzy search
    if len(db_name_matches) == 0:
        logger.debug(f"{source}: No name matches, trying fuzzy search")
        db_name_matches = db.search_object(
            source, output_table="Sources", fuzzy_search=True, verbose=False
        )

    # If still no matches, try to resolve the name with Simbad
    if len(db_name_matches) == 0:
        logger.debug(f"{source}: No name matches, trying Simbad search")
        db_name_matches = db.search_object(
            source, resolve_simbad=True, fuzzy_search=False, verbose=False
        )

    # if still no matches, try spatial search using coordinates, if provided
    if len(db_name_matches) == 0 and coords:
        location = SkyCoord(ra, dec, frame="icrs", unit="deg")
        radius = u.Quantity(search_radius, unit="arcsec")
        logger.info(
            f"{source}: No Simbad match, trying coord search around"
            f"{location.ra.degree}, {location.dec}"
        )
        db_name_matches = db.query_region(location, radius=radius, ra_col='ra_deg', dec_col='dec_deg')

    # If still no matches, try to get the coords from SIMBAD
    if len(db_name_matches) == 0:
        simbad_result_table = Simbad.query_object(source)
        if simbad_result_table is not None and len(simbad_result_table) == 1:
            simbad_coords = (
                simbad_result_table["RA"][0] + " " + simbad_result_table["DEC"][0]
            )
            simbad_skycoord = SkyCoord(simbad_coords, unit=(u.hourangle, u.deg))
            ra = simbad_skycoord.to_string(style="decimal").split()[0]
            dec = simbad_skycoord.to_string(style="decimal").split()[1]
            msg = f"Coordinates retrieved from SIMBAD {ra}, {dec}"
            logger.debug(msg)
            # Search database around that coordinate
            radius = u.Quantity(search_radius, unit="arcsec")
            msg2 = (
                f"Finding SIMBAD matches around {simbad_skycoord} with radius {radius}"
            )
            logger.debug(msg2)
            db_name_matches = db.query_region(simbad_skycoord, radius=radius,ra_col="ra_deg", dec_col="dec_deg")

    if len(db_name_matches) == 1:
        db_names = db_name_matches["source"].tolist()
        logger.debug(f"One match found for {source}: {db_names[0]}")
    elif len(db_name_matches) > 1:
        db_names = db_name_matches["source"].tolist()
        logger.debug(f"More than match found for {source}: {db_names}")
        # TODO: Find way for user to choose correct match
    elif len(db_name_matches) == 0:
        db_names = []
        logger.debug(f" {source}: No match found")
    else:
        raise AstroDBError(f"Unexpected condition searching for {source}")

    return db_names


def find_publication(db, name: str = None, doi: str = None, bibcode: str = None):
    """
    Find publications in the database by matching
    on the publication name,  doi, or bibcode

    Parameters
    ----------
    db
        Variable referencing the database to search
    name: str
        Name of publication to search
    doi: str
        DOI of publication to search
    bibcode: str
        ADS Bibcode of publication to search

    Returns
    -------
    True, str: if only one match
    False, 0: No matches
    False, N_matches: Multiple matches

    Examples
    -------
    >>> test = search_publication(db, name='Cruz')
    Found 8 matching publications for Cruz or None or None

    >>> test = search_publication(db, name='Kirk19')
    Found 1 matching publications for Kirk19 or None or None
     name        bibcode                 doi
    ------ ------------------- ------------------------
    Kirk19 2019ApJS..240...19K 10.3847/1538-4365/aaf6af
                            description
    -----------------------------------------------------------------------------
    Preliminary Trigonometric Parallaxes of 184 Late-T and Y Dwarfs and an
    Analysis of the Field Substellar Mass Function into the Planetary Mass Regime

    >>> test = search_publication(db, name='Smith')
    No matching publications for Smith, Trying Smit
    No matching publications for Smit
    Use add_publication() to add it to the database.

    See Also
    --------
    add_publication: Function to add publications in the database

    """

    # Make sure a search term is provided
    if name is None and doi is None and bibcode is None:
        logger.error("Name, Bibcode, or DOI must be provided")
        return False, 0

    not_null_pub_filters = []
    if name:
        # fuzzy_query_name = '%' + name + '%'
        not_null_pub_filters.append(db.Publications.c.reference.ilike(name))
    if doi:
        not_null_pub_filters.append(db.Publications.c.doi.ilike(doi))
    if bibcode:
        not_null_pub_filters.append(db.Publications.c.bibcode.ilike(bibcode))
    pub_search_table = Table()
    if len(not_null_pub_filters) > 0:
        pub_search_table = (
            db.query(db.Publications).filter(or_(*not_null_pub_filters)).table()
        )

    n_pubs_found = len(pub_search_table)

    if n_pubs_found == 1:
        logger.info(
            f"Found {n_pubs_found} matching publications for "
            f"{name} or {doi} or {bibcode}: {pub_search_table['reference'].data}"
        )
        if logger.level <= 10:  # debug
            pub_search_table.pprint_all()
        return True, pub_search_table["reference"].data[0]

    if n_pubs_found > 1:
        logger.warning(
            f"Found {n_pubs_found} matching publications for {name} or {doi} or {bibcode}"
        )
        if logger.level <= 30:  # warning
            pub_search_table.pprint_all()
        return False, n_pubs_found

    # If no matches found, search using first four characters of input name
    if n_pubs_found == 0 and name:
        shorter_name = name[:4]
        logger.debug(f"No matching publications for {name}, Trying {shorter_name}.")
        fuzzy_query_shorter_name = "%" + shorter_name + "%"
        pub_search_table = (
            db.query(db.Publications)
            .filter(db.Publications.c.reference.ilike(fuzzy_query_shorter_name))
            .table()
        )
        n_pubs_found_short = len(pub_search_table)
        if n_pubs_found_short == 0:
            logger.warning(f"No matching publications for {name} or {shorter_name}")
            logger.warning("Use add_publication() to add it to the database.")
            return False, 0

        if n_pubs_found_short > 0:
            logger.debug(
                f"Found {n_pubs_found_short} matching publications for {shorter_name}"
            )
            if logger.level == 10:  # debug
                pub_search_table.pprint_all()

            #  Try to find numbers in the reference which might be a date
            dates = re.findall(r"\d+", name)
            # try to find a two digit date
            if len(dates) == 0:
                logger.debug(f"Could not find a date in {name}")
                two_digit_date = None
            elif len(dates) == 1:
                if len(dates[0]) == 4:
                    two_digit_date = dates[0][2:]
                elif len(dates[0]) == 2:
                    two_digit_date = dates[0]
                else:
                    logger.debug(f"Could not find a two digit date using {dates}")
                    two_digit_date = None
            else:
                logger.debug(f"Could not find a two digit date using {dates}")
                two_digit_date = None

            if two_digit_date:
                logger.debug(f"Trying to limit using {two_digit_date}")
                n_pubs_found_short_date = 0
                pubs_found_short_date = []
                for pub in pub_search_table["reference"]:
                    if pub.find(two_digit_date) != -1:
                        n_pubs_found_short_date += 1
                        pubs_found_short_date.append(pub)
                if n_pubs_found_short_date == 1:
                    logger.debug(
                        f"Found {n_pubs_found_short_date} matching publications for "
                        f"{name} using {shorter_name} and {two_digit_date}"
                    )
                    logger.debug(f"{pubs_found_short_date}")
                    return True, pubs_found_short_date[0]
                else:
                    logger.warning(
                        f"Found {n_pubs_found_short_date} matching publications for "
                        f"{name} using {shorter_name} and {two_digit_date}"
                    )
                    logger.warning(f"{pubs_found_short_date}")
                    return False, n_pubs_found_short_date
            else:
                return False, n_pubs_found_short
    else:
        return False, n_pubs_found

    return


def ingest_publication(
    db,
    doi: str = None,
    bibcode: str = None,
    publication: str = None,
    description: str = None,
    ignore_ads: bool = False,
):
    """
    Adds publication to the database using DOI or ADS Bibcode,
    including metadata found with ADS.

    In order to auto-populate the fields, An $ADS_TOKEN environment variable must be set.
    See https://ui.adsabs.harvard.edu/user/settings/token

    Parameters
    ----------
    db
        Database object
    doi, bibcode: str
        The DOI or ADS Bibcode of the reference. One of these is required input.
    publication: str, optional
        The publication shortname, otherwise it will be generated [optional]
        Convention is the first four letters of first authors last name and
            two digit year (e.g., Smit21)
        For last names which are less than four letters, use '_' or first name initial(s).
            (e.g, Xu__21 or LiYB21)
    description: str, optional
        Description of the paper, typically the title of the papre [optional]
    ignore_ads: bool

    See Also
    --------
    search_publication: Function to find publications in the database

    """

    if not (publication or doi or bibcode):
        logger.error("Publication, DOI, or Bibcode is required input")
        return

    ads.config.token = os.getenv("ADS_TOKEN")

    if not ads.config.token and (not publication and (not doi or not bibcode)):
        logger.error(
            "An ADS_TOKEN environment variable must be set"
            "in order to auto-populate the fields.\n"
            "Without an ADS_TOKEN, name and bibcode or DOI must be set explicity."
        )
        return

    if ads.config.token and not ignore_ads:
        use_ads = True
    else:
        use_ads = False
    logger.debug(f"Use ADS set to {use_ads}")

    if bibcode:
        if "arXiv" in bibcode:
            arxiv_id = bibcode
            bibcode = None
        else:
            arxiv_id = None
    else:
        arxiv_id = None

    name_add, bibcode_add, doi_add = "", "", ""
    # Search ADS uing a provided arxiv id
    if arxiv_id and use_ads:
        arxiv_matches = ads.SearchQuery(
            q=arxiv_id, fl=["id", "bibcode", "title", "first_author", "year", "doi"]
        )
        arxiv_matches_list = list(arxiv_matches)
        if len(arxiv_matches_list) != 1:
            logger.error("should only be one matching arxiv id")
            return

        if len(arxiv_matches_list) == 1:
            logger.debug(f"Publication found in ADS using arxiv id: , {arxiv_id}")
            article = arxiv_matches_list[0]
            logger.debug(
                f"{article.first_author}, {article.year},"
                "{article.bibcode}, {article.title}"
            )
            if not publication:  # generate the name if it was not provided
                name_stub = article.first_author.replace(",", "").replace(" ", "")
                name_add = name_stub[0:4] + article.year[-2:]
            else:
                name_add = publication
            description = article.title[0]
            bibcode_add = article.bibcode
            doi_add = article.doi[0]

    elif arxiv_id:
        name_add = publication
        bibcode_add = arxiv_id
        doi_add = doi

    # Search ADS using a provided DOI
    if doi and use_ads:
        doi_matches = ads.SearchQuery(
            doi=doi, fl=["id", "bibcode", "title", "first_author", "year", "doi"]
        )
        doi_matches_list = list(doi_matches)
        if len(doi_matches_list) != 1:
            logger.error("should only be one matching DOI")
            return

        if len(doi_matches_list) == 1:
            logger.debug(f"Publication found in ADS using DOI: {doi}")
            using = doi
            article = doi_matches_list[0]
            logger.debug(
                f"{article.first_author}, {article.year},"
                "{article.bibcode}, {article.title}"
            )
            if not publication:  # generate the name if it was not provided
                name_stub = article.first_author.replace(",", "").replace(" ", "")
                name_add = name_stub[0:4] + article.year[-2:]
            else:
                name_add = publication
            description = article.title[0]
            bibcode_add = article.bibcode
            doi_add = article.doi[0]
    elif doi:
        name_add = publication
        bibcode_add = bibcode
        doi_add = doi

    if bibcode and use_ads:
        bibcode_matches = ads.SearchQuery(
            bibcode=bibcode,
            fl=["id", "bibcode", "title", "first_author", "year", "doi"],
        )
        bibcode_matches_list = list(bibcode_matches)
        if len(bibcode_matches_list) == 0:
            logger.error("not a valid bibcode:" + str(bibcode))
            logger.error("nothing added")
            raise

        elif len(bibcode_matches_list) > 1:
            logger.error("should only be one matching bibcode for:" + str(bibcode))
            logger.error("nothing added")
            raise

        elif len(bibcode_matches_list) == 1:
            logger.debug("Publication found in ADS using bibcode: " + str(bibcode))
            using = str(bibcode)
            article = bibcode_matches_list[0]
            logger.debug(
                f"{article.first_author}, {article.year}, "
                "{article.bibcode}, {article.doi}, {article.title}"
            )
            if not publication:  # generate the name if it was not provided
                name_stub = article.first_author.replace(",", "").replace(" ", "")
                name_add = name_stub[0:4] + article.year[-2:]
            else:
                name_add = publication
            description = article.title[0]
            bibcode_add = article.bibcode
            if article.doi is None:
                doi_add = None
            else:
                doi_add = article.doi[0]
    elif bibcode:
        name_add = publication
        bibcode_add = bibcode
        doi_add = doi

    if publication and not bibcode and not doi:
        name_add = publication
        using = "user input"

    new_ref = [
        {
            "reference": name_add,
            "bibcode": bibcode_add,
            "doi": doi_add,
            "description": description,
        }
    ]

    try:
        with db.engine.connect() as conn:
            conn.execute(db.Publications.insert().values(new_ref))
            conn.commit()
        logger.info(f"Added {name_add} to Publications table using {using}")
    except sqlalchemy.exc.IntegrityError as error:
        msg = (
            f"Not able to add {new_ref} to the database. "
            f"It's possible that a similar publication already exists in database\n"
            "Use find_publication function before adding a new record"
        )
        logger.error(msg)
        raise AstroDBError(msg + str(error))

    return


def check_internet_connection():
    # get current IP address of  system
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

    request_response = requests.head(url)
    status_code = request_response.status_code  # The website is up if the status code is 200
    if status_code != 200:
        status = 'skipped' # instead of incrememnting n_skipped, just skip this one
        msg = "The spectrum location does not appear to be valid: \n" \
              f'spectrum: {url} \n' \
              f'status code: {status_code}'
        logger.error(msg)
    else:
        msg = f"The spectrum location appears up: {url}"
        logger.debug(msg)
        status = 'added'
    return status


# NAMES
def ingest_names(db, source, other_name):
    """
    This function ingests an other name into the Names table

    Parameters
    ----------
    db: astrodbkit2.astrodb.Database
        Database object created by astrodbkit2
    source: str
        Name of source as it appears in sources table

    other_name: str
        Name of the source different than that found in source table

    Returns
    -------
    None
    """
    names_data = [{"source": source, "other_name": other_name}]
    try:
        with db.engine.connect() as conn:
            conn.execute(db.Names.insert().values(names_data))
            conn.commit()
        logger.info(f" Name added to database: {names_data}\n")
    except sqlalchemy.exc.IntegrityError as e:
        msg = f"Could not add {names_data} to database. Name is likely a duplicate."
        logger.warning(msg)
        raise AstroDBError(msg + "\n" + str(e) + "\n")


# SOURCES
def ingest_source(
    db,
    source,
    reference: str = None,
    ra: float = None,
    dec: float = None,
    epoch: str = None,
    equinox: str = None,
    other_reference: str = None,
    comment: str = None,
    raise_error: bool = True,
    search_db: bool = True,
):
    """
    Parameters
    ----------
    db: astrodbkit2.astrodb.Database
        Database object created by astrodbkit2
    sources: str
        Names of sources
    references: str
        Discovery references of sources
    ras: float, optional
        Right ascensions of sources. Decimal degrees.
    decs: float, optional
        Declinations of sources. Decimal degrees.
    comments: string, optional
        Comments
    epochs: str, optional
        Epochs of coordinates
    equinoxes: str, optional
        Equinoxes of coordinates
    other_references: str
    raise_error: bool, optional
        True (default): Raise an error if a source cannot be ingested
        False: Log a warning but skip sources which cannot be ingested
    search_db: bool, optional
        True (default): Search database to see if source is already ingested
        False: Ingest source without searching the database

    Returns
    -------

    None

    """

    if ra is None and dec is None:
        coords_provided = False
    else:
        coords_provided = True
        ra = ra
        dec = dec
        epoch = epoch
        equinox = equinox
    logger.debug(f"coords_provided:{coords_provided}")

    # Find out if source is already in database or not
    if coords_provided and search_db:
        logger.debug(f"Checking database for: {source} at ra: {ra}, dec: {dec}")
        name_matches = find_source_in_db(db, source, ra=ra, dec=dec)
    elif search_db:
        logger.debug(f"Checking database for: {source}")
        name_matches = find_source_in_db(db, source)
    elif not search_db:
        name_matches = []
    else:
        name_matches = None

    logger.debug(f"Source matches in database: {name_matches}")

    # Source is already in database
    # Checking out alternate names
    if len(name_matches) == 1 and search_db:
        # Figure out if source name provided is an alternate name
        db_source_matches = db.search_object(
            source, output_table="Sources", fuzzy_search=False
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
                    raise AstroDBError(msg + "\n" + str(e))
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

        ref_check = find_publication(db, name=reference)
        logger.debug(f"ref_check: {ref_check}")

        if ref_check is False:
            msg = (
                f"Skipping: {source}. Discovery reference {reference}"
                "is not in Publications table. \n"
                f"(Add it with ingest_publication function.)"
            )
            logger.warning(msg)
            if raise_error:
                raise AstroDBError(msg)
            else:
                return

        # Try to get coordinates from SIMBAD if they were not provided
        if not coords_provided:
            # Try to get coordinates from SIMBAD
            simbad_result_table = Simbad.query_object(source)

            if simbad_result_table is None:
                msg = f"Not ingesting {source}. "
                "Coordinates are needed and "
                "could not be retrieved from SIMBAD. \n"
                logger.warning(msg)
                if raise_error:
                    raise AstroDBError(msg)
                else:
                    return
            # One SIMBAD match! Using those coordinates for source.
            elif len(simbad_result_table) == 1:
                simbad_coords = (
                    simbad_result_table["RA"][0] + " " + simbad_result_table["DEC"][0]
                )
                simbad_skycoord = SkyCoord(simbad_coords, unit=(u.hourangle, u.deg))
                ra = simbad_skycoord.to_string(style="decimal").split()[0]
                dec = simbad_skycoord.to_string(style="decimal").split()[1]
                epoch = "2000"  # Default coordinates from SIMBAD are epoch 2000.
                equinox = "J2000"  # Default frame from SIMBAD is IRCS and J2000.
                msg = f"Coordinates retrieved from SIMBAD {ra}, {dec}"
                logger.debug(msg)
            else:
                msg = f"Not ingesting {source}. "
                "Coordinates are needed and "
                "could not be retrieved from SIMBAD. \n"
                logger.warning(msg)
                if raise_error:
                    raise AstroDBError(msg)
                else:
                    return

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
            "ra_deg": ra,
            "dec_deg": dec,
            "reference": reference,
            "epoch_year": epoch,
            "equinox": equinox,
            "other_references": other_reference,
            "comments": comment,
        }
    ]
    names_data = [{"source": source, "other_name": source}]

    # Try to add the source to the database
    try:
        with db.engine.connect() as conn:
            conn.execute(db.Sources.insert().values(source_data))
            conn.commit()
        msg = f"Added {str(source_data)}"
        logger.info(f"Added {source}")
        logger.debug(msg)
    except sqlalchemy.exc.IntegrityError:
        msg = (
            f"Not ingesting {source}. Not sure why. \n"
            "The reference may not exist in Publications table. \n"
            "Add it with ingest_publication function. \n"
        )
        msg2 = f"   {str(source_data)} "
        logger.warning(msg)
        logger.debug(msg2)
        if raise_error:
            raise AstroDBError(msg + msg2)
        else:
            return

    # Try to add the source name to the Names table
    try:
        with db.engine.connect() as conn:
            conn.execute(db.Names.insert().values(names_data))
            conn.commit()
        logger.debug(f"    Name added to database: {names_data}\n")
    except sqlalchemy.exc.IntegrityError:
        msg = f"   Could not add {names_data} to database"
        logger.warning(msg)
        if raise_error:
            raise AstroDBError(msg)
        else:
            return

    return


def ingest_sources(
    db,
    sources,
    references=None,
    ras=None,
    decs=None,
    comments=None,
    epochs=None,
    equinoxes=None,
    other_references=None,
    raise_error=True,
    search_db=True,
):
    """
    Script to ingest sources
    TODO: better support references=None
    Parameters
    ----------
    db: astrodbkit2.astrodb.Database
        Database object created by astrodbkit2
    sources: list[str]
        Names of sources
    references: str or list[strings]
        Discovery references of sources
    ras: list[floats], optional
        Right ascensions of sources. Decimal degrees.
    decs: list[floats], optional
        Declinations of sources. Decimal degrees.
    comments: list[strings], optional
        Comments
    epochs: str or list[str], optional
        Epochs of coordinates
    equinoxes: str or list[string], optional
        Equinoxes of coordinates
    other_references: str or list[strings]
    raise_error: bool, optional
        True (default): Raise an error if a source cannot be ingested
        False: Log a warning but skip sources which cannot be ingested
    search_db: bool, optional
        True (default): Search database to see if source is already ingested
        False: Ingest source without searching the database

    Returns
    -------

    None

    """
    # TODO: add example

    # SETUP INPUTS
    if ras is None and decs is None:
        coords_provided = False
    else:
        coords_provided = True

    if isinstance(sources, str):
        n_sources = 1
    else:
        n_sources = len(sources)

    # Convert single element input values into lists
    input_values = [
        sources,
        references,
        ras,
        decs,
        epochs,
        equinoxes,
        comments,
        other_references,
    ]
    for i, input_value in enumerate(input_values):
        if input_value is None:
            input_values[i] = [None] * n_sources
        elif isinstance(input_value, (str, float)):
            input_values[i] = [input_value] * n_sources
    (
        sources,
        references,
        ras,
        decs,
        epochs,
        equinoxes,
        comments,
        other_references,
    ) = input_values

    # TODO: figure out counting
    # n_added = 0
    # n_existing = 0
    # n_names = 0
    # n_alt_names = 0
    # n_skipped = 0
    # n_multiples = 0

    if n_sources > 1:
        logger.info(f"Trying to add {n_sources} sources")

    # Loop over each source and decide to ingest, skip, or add alt name
    for source_counter, source in enumerate(sources):
        logger.debug(f"{source_counter}: Trying to ingest {source}")

        reference = references[source_counter]
        other_reference = other_references[source_counter]
        comment = (
            None if ma.is_masked(comments[source_counter]) else comments[source_counter]
        )

        if coords_provided:
            ra = ras[source_counter]
            dec = decs[source_counter]
            epoch = (
                None if ma.is_masked(epochs[source_counter]) else epochs[source_counter]
            )
            equinox = (
                None
                if ma.is_masked(equinoxes[source_counter])
                else equinoxes[source_counter]
            )

            ingest_source(
                db,
                source,
                reference=reference,
                ra=ra,
                dec=dec,
                epoch=epoch,
                equinox=equinox,
                other_reference=other_reference,
                comment=comment,
                raise_error=raise_error,
                search_db=search_db,
            )
        else:
            ingest_source(
                db,
                source,
                reference=reference,
                other_reference=other_reference,
                comment=comment,
                raise_error=raise_error,
                search_db=search_db,
            )

    # if n_sources > 1:
    #     logger.info(f"Sources added to database: {n_added}")
    #     logger.info(f"Names added to database: {n_names} \n")
    #     logger.info(f"Sources already in database: {n_existing}")
    #     logger.info(f"Alt Names added to database: {n_alt_names}")
    #     logger.info(
    #         f"Sources NOT added to database because multiple matches: {n_multiples}"
    #     )
    #     logger.info(f"Sources NOT added to database: {n_skipped} \n")

    # if n_added != n_names:
    #     msg = f"Number added should equal names added."
    #     raise AstroDBError(msg)

    # if n_added + n_existing + n_multiples + n_skipped != n_sources:
    #     msg = f"Number added + Number skipped doesn't add up to total sources"
    #     raise AstroDBError(msg)

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


def ingest_instrument(db, telescope=None, instrument=None, mode=None):
    """
    Script to ingest instrumentation
    TODO: Add option to ingest references for the telescope and instruments

    Parameters
    ----------
    db: astrodbkit2.astrodb.Database
        Database object created by astrodbkit2
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
            raise AstroDBError(msg + "\n" + str(e))

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
            raise AstroDBError(msg + "\n" + str(e))

    return
