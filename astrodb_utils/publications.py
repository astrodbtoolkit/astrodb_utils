import logging
import os
import re
from typing import Literal

import ads
import sqlalchemy.exc
from astropy.table import Table
from sqlalchemy import or_

from astrodb_utils import AstroDBError, exit_function

__all__ = [
    "find_publication",
    "ingest_publication",
    "check_ads_token",
    "get_db_publication",
]

logger = logging.getLogger(__name__)
msg = f"logger.parent.name: {logger.parent.name}, logger.parent.level: {logger.parent.level}"
logger.info(msg)

# ruff: noqa: C901 (function complexity check)
def find_publication(
    db, *, reference: str = None, doi: str = None, bibcode: str = None
):
    """
    Find publications in the database by matching
    on the publication name,  doi, or bibcode

    Parameters
    ----------
    db
        Variable referencing the database to search
    reference: str
        Name of publication to search
    doi: str
        DOI of publication to search
    bibcode: str
        ADS Bibcode of publication to search

    Returns
    -------
    # TODO:  Return three things: Boolean, n_pubs_found, string result
    True, str: if only one match
    False, 0: No matches
    False, N_matches: Multiple matches

    Examples
    -------
    >>> test = search_publication(db, reference='Cruz')
    Found 8 matching publications for Cruz or None or None

    >>> test = search_publication(db, reference='Kirk19')
    Found 1 matching publications for Kirk19 or None or None
     name        bibcode                 doi
    ------ ------------------- ------------------------
    Kirk19 2019ApJS..240...19K 10.3847/1538-4365/aaf6af
                            description
    -----------------------------------------------------------------------------
    Preliminary Trigonometric Parallaxes of 184 Late-T and Y Dwarfs and an
    Analysis of the Field Substellar Mass Function into the Planetary Mass Regime

    >>> test = search_publication(db, reference='Smith')
    No matching publications for Smith, Trying Smit
    No matching publications for Smit
    Use add_publication() to add it to the database.

    See Also
    --------
    ingest_publication: Function to add publications in the database

    """

    # Make sure a search term is provided
    if reference is None and doi is None and bibcode is None:
        logger.error("Name, Bibcode, or DOI must be provided")
        return False, 0

    use_ads = check_ads_token()

    not_null_pub_filters = []
    if reference:
        # fuzzy_query_name = '%' + name + '%'
        not_null_pub_filters.append(db.Publications.c.reference.ilike(reference))
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
        logger.debug(
            f"Found {n_pubs_found} matching publications for "
            f"{reference} or {doi} or {bibcode}: {pub_search_table['reference'].data}"
        )
        if logger.parent.level <= 10:  # debug
            pub_search_table.pprint_all()
        return True, pub_search_table["reference"].data[0]

    if n_pubs_found > 1:
        logger.warning(
            f"Found {n_pubs_found} matching publications for {reference} or {doi} or {bibcode}"
        )
        if logger.parent.level <= 30:  # warning
            pub_search_table.pprint_all()
        return False, n_pubs_found

    logger.debug(f"n_pubs_found: {n_pubs_found}. Using {reference} or {doi} or {bibcode}.")
    logger.debug(f"bibcode: {bibcode}")
    logger.debug(f"use_ads: {use_ads}")

    # If no matches found, search using first four characters of input name
    if n_pubs_found == 0 and reference:
        shorter_name = reference[:4]
        logger.debug(
            f"No matching publications for {reference}, Trying {shorter_name}."
        )
        fuzzy_query_shorter_name = "%" + shorter_name + "%"
        pub_search_table = (
            db.query(db.Publications)
            .filter(db.Publications.c.reference.ilike(fuzzy_query_shorter_name))
            .table()
        )
        n_pubs_found_short = len(pub_search_table)
        if n_pubs_found_short == 0:
            logger.warning(
                f"No matching publications for {reference} or {shorter_name}"
            )
            logger.warning("Use add_publication() to add it to the database.")
            return False, 0

        if n_pubs_found_short > 0:
            logger.debug(
                f"Found {n_pubs_found_short} matching publications for {shorter_name}"
            )
            if logger.parent.level == 10:  # debug
                pub_search_table.pprint_all()

            two_digit_date = _find_dates_in_reference(reference)

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
                        f"{reference} using {shorter_name} and {two_digit_date}"
                    )
                    logger.debug(f"{pubs_found_short_date}")
                    return True, pubs_found_short_date[0]
                else:
                    logger.warning(
                        f"Found {n_pubs_found_short_date} matching publications for "
                        f"{reference} using {shorter_name} and {two_digit_date}"
                    )
                    logger.warning(f"{pubs_found_short_date}")
                    return False, n_pubs_found_short_date
            else:
                return False, n_pubs_found_short

    if n_pubs_found == 0 and bibcode and "arXiv" in bibcode and use_ads:
        logger.debug(f"Using ADS to find alt name for {bibcode}")
        results = _search_ads(bibcode, query_type="arxiv")

        if results is not None:
            bibcode_alt = results[1]
            not_null_pub_filters = []
            not_null_pub_filters.append(db.Publications.c.bibcode.ilike(bibcode_alt))
            pub_search_table = Table()
            pub_search_table = (
                db.query(db.Publications).filter(or_(*not_null_pub_filters)).table()
            )
            if len(pub_search_table) == 1:
                logger.debug(
                    f"Found {len(pub_search_table)} matching publications for "
                    f"{reference} or {doi} or {bibcode}: {pub_search_table['reference'].data}"
                )
                if logger.parent.level <= 10:  # debug
                    pub_search_table.pprint_all()

                return True, pub_search_table["reference"].data[0]
            else:
                return False, len(pub_search_table)
        else:
            return False, 0  # No matches found using arxiv in bibcode

    else:
        return False, n_pubs_found

    return


def ingest_publication(
    db,
    *,
    doi: str = None,
    bibcode: str = None,
    reference: str = None,
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
        two digit year (e.g., Smit21).
        For last names which are less than four letters, use '_' or first name initial(s).
        (e.g, Xu__21 or LiYB21).
    description: str, optional
        Description of the paper, typically the title of the papre [optional]
    ignore_ads: bool (default=False)
        If True, do not use ADS to search for the publication [optional]
        If False, an ADS_TOKEN environment variable must be set.

    See Also
    --------
    find_publication: Function to find publications in the database

    """

    logger.debug(f"Adding publication to database using {reference}, {doi}, {bibcode}")

    if not (reference or doi or bibcode):
        logger.error("Publication, DOI, or Bibcode is required input")
        return

    if reference and not bibcode and not doi:
        name_add = reference
        using = f"ref: {reference} user input. No bibcode or DOI provided."

    if ignore_ads is False and check_ads_token() is False:
        ignore_ads = True
        if not reference and (not doi or not bibcode):
            logger.error(
                "An ADS_TOKEN environment variable must be set"
                "in order to auto-populate the fields.\n"
                "Without an ADS_TOKEN, name and bibcode or DOI must be set explicity."
            )
            return
    logger.debug(f"ignore_ads set to {ignore_ads}")

    if ignore_ads is True and reference is None:
        logger.error("A reference must be provided if ignore_ads is set to True")
        return

    name_add, bibcode_add, doi_add = "", "", ""
    using = f"ref: {name_add}, bibcode: {bibcode_add}, DOI: {doi_add}"

    if ignore_ads is False:
        # Figure out how to search ADS
        if doi:  # Search ADS using a provided DOI
            query_type = "doi"
            value = doi
        elif bibcode:
            if "arXiv" in bibcode:
                query_type = "arxiv"  # Search ADS using an arXiv ID
            else:
                query_type = "bibcode"  # Search ADS using a provided bibcode
            value = bibcode
        else:
            logger.error("Unexpected error. No doi or bibcode provided")
            return

        logger.debug(
            f"Searching ADS using {query_type}: {value}, reference: {reference}"
        )
        name_add, bibcode_add, doi_add, description = _search_ads(
            value, query_type=query_type, reference=reference
        )
    else:
        name_add = reference
        bibcode_add = bibcode
        doi_add = doi

    using = f"ref: {name_add}, bibcode: {bibcode_add}, DOI: {doi_add}"

    new_ref = [
        {
            "reference": name_add,
            "bibcode": bibcode_add,
            "doi": doi_add,
            "description": description,
        }
    ]
    logger.debug(f"Adding {new_ref} to Publications table using {using}")

    try:
        with db.engine.connect() as conn:
            conn.execute(db.Publications.insert().values(new_ref))
            conn.commit()
        logger.info(f"Added {name_add} to Publications table using {using}")

        return name_add
    except sqlalchemy.exc.IntegrityError as error:
        msg = (
            f"Not able to add {new_ref} to the database. "
            "It's possible that a similar publication already exists in database\n"
            "Use find_publication function before adding a new record"
        )
        logger.error(msg)
        raise AstroDBError(msg) from error

    return


def check_ads_token():
    """Check if an ADS token is set"""

    ads.config.token = os.getenv("ADS_TOKEN")

    if ads.config.token:
        use_ads = True
    else:
        logger.warning(
            "An ADS_TOKEN environment variable is not set.\nsetting ignore_ads=True/use_ads=False"
        )
        use_ads = False

    return use_ads


def _search_ads(
    value: str, query_type: Literal["arxiv", "bibcode", "doi"], reference=None
):
    """
    Search ADS for a publication using the provided string and query type.
    The query type indicates if the string provided is an arXiv ID, bibcode, or DOI.
    The function will return the name, bibcode, doi, and description of the publication
    if found.

    It will return None if no match or multiple matches are found.

    Parameters
    ----------
    value: str
        The value to search for in ADS.
    query_type: str
        The type of query to perform. Can be one of the following:
        - arxiv
        - bibcode
        - doi
    reference: str
        The reference name to use if the publication is found.
        If not provided, it will be generated from the first author and year.

    Returns
    -------
    If no match or multiple matches are found, it returns None.

    If one match is found, it returns a tuple with the following elements:
    name_add: str
        The name of the publication.
    bibcode_add: str
        The bibcode of the publication.
    doi_add: str
        The DOI of the publication.
    description: str
        The description of the publication (usually the title).

    """
    if check_ads_token() is False:
        logger.error("An ADS_TOKEN environment variable must be set")
        return

    if query_type == "arxiv":
        ads_matches = ads.SearchQuery(
            q=value, fl=["id", "bibcode", "title", "first_author", "year", "doi"]
        )
    elif query_type == "bibcode":
        ads_matches = ads.SearchQuery(
            bibcode=value,
            fl=["id", "bibcode", "title", "first_author", "year", "doi"],
        )
    elif query_type == "doi":
        ads_matches = ads.SearchQuery(
            doi=value, fl=["id", "bibcode", "title", "first_author", "year", "doi"]
        )
    else:
        logger.error(
            f"Invalid query type: {query_type}. Valid types are 'arxiv', 'bibcode', or 'doi'"
        )
        return

    ads_matches_list = list(ads_matches)

    if len(ads_matches_list) == 0:
        msg = f"No ADS matches for {query_type}: {value}"
        logger.warning(msg)
        return

    if len(ads_matches_list) > 1:
        logger.warning(f"More than one matching ADS record for {query_type}: {value}")
        return

    if len(ads_matches_list) == 1:
        logger.info(f"Publication found in ADS for {query_type}: {value}")
        article = ads_matches_list[0]
        logger.debug(
            f"{article.first_author}, {article.year}, {article.bibcode}, {article.doi}, {article.title}"
        )
        if not reference:  # generate the name if it was not provided
            name_stub = article.first_author.replace(",", "").replace(" ", "")
            name_add = name_stub[0:4] + article.year[-2:]
        else:
            name_add = reference

        description = article.title[0]
        bibcode_add = article.bibcode
        doi_add = article.doi[0]

        return name_add, bibcode_add, doi_add, description


def _find_dates_in_reference(reference):
    #  Try to find numbers in the reference which might be a date
    dates = re.findall(r"\d+", reference)
    # try to find a two digit date
    if len(dates) == 0:
        logger.debug(f"Could not find a date in {reference}")
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

    return two_digit_date


def get_db_publication(db, reference: str, raise_error: bool = True):
    """
    Check if a publication is in the database using ilike matching.
    This minimizes problems with case sensitivity.

    If it is not found or there are multiple matches, raise an error or return None.
    If it is found, return the reference as a string.

    Returns
    -------
    str: The reference of the publication in the database.
    None: If the publication is not found or there are multiple matches.
    """
    pubs_table = (
        db.query(db.Publications)
        .filter(db.Publications.c.reference.ilike(reference))
        .table()
    )

    if len(pubs_table) == 1:
        logger.warning(f"Matched {reference} in database to {pubs_table['reference'][0]}")
        return pubs_table["reference"][0]

    if len(pubs_table) == 0:
        msg = (
            f"Reference not found in database:  {reference}  "
            "Add it to the Publications table."
        )
    elif len(pubs_table) > 1:
        msg = (
            f"Multiple entries for reference {reference} found in database. "
            "Check the Publications table. \n  "
            f"Matches: \n {pubs_table}"
        )
    else:
        msg = f"Unexpected condition while searching for reference: {reference}"

    result = exit_function(msg, raise_error=raise_error, return_value=None)
    return result