import logging

import sqlalchemy.exc
from sqlalchemy import and_

from astrodb_utils import AstroDBError, exit_function

__all__ = [
    "ingest_instrument",
    "get_db_instrument"
]

logger = logging.getLogger(__name__)


def ingest_instrument(db, *, telescope=None, instrument=None, mode=None, raise_error=True):
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
    logger.debug(msg_search)

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
            f"{telescope}-{instrument}-{mode} is already in the database. Nothing added."
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
            msg =f"Telescope could not be ingested: {telescope}"
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
            msg_instrument = f"{telescope}-{instrument}-{mode} was successfully ingested in the database."
            logger.info(msg_instrument)
        except sqlalchemy.exc.IntegrityError as e:  # pylint: disable=invalid-name
            msg = "Instrument/Mode could not be ingested: {telescope}-{instrument}-{mode} "
            logger.error(msg)
            raise AstroDBError(msg) from e

    return


def get_db_instrument(db, instrument=None, mode=None, telescope=None):
    instrument_table = (
        db.query(db.Instruments)
        .filter(
            and_(
                db.Instruments.c.instrument.contains(instrument),
                db.Instruments.c.telescope.contains(telescope),
            )
        )
        .table()
    )

    if len(instrument_table) > 1: # constrain query with instrument mode
        instrument_table = (
            db.query(db.Instruments)
            .filter(
                and_(
                    db.Instruments.c.instrument.contains(instrument),
                    db.Instruments.c.mode.ilike(mode),
                    db.Instruments.c.telescope.contains(telescope),
                )
            )
            .table()
        )

    if len(instrument_table) == 1:
        if (
            instrument_table["instrument"][0] != instrument
            or instrument_table["mode"][0] != mode
            or instrument_table["telescope"][0] != telescope
        ):
            msg = (
                f"Instrument {instrument} with mode {mode} and telescope {telescope} "
                f"matched to {instrument_table['instrument'][0]}-{instrument_table['mode'][0]}-{instrument_table['telescope'][0]}. "
            )
            logger.warning(msg) 

        return (
            instrument_table["instrument"][0],
            instrument_table["mode"][0],
            instrument_table["telescope"][0],
        )

    if len(instrument_table) == 0:
        msg = f"{telescope}-{instrument}-{mode}, not found in database. Please add it to the Instruments table."
    else:
        msg = f"Multiple matches found for {telescope}-{instrument}-{mode}. Please check the Instruments table."

    exit_function(msg, raise_error=True, return_value=None)
