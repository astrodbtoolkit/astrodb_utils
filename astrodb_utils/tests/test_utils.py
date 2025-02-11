import pytest
from sqlalchemy import and_

from astrodb_utils import (
    AstroDBError,
    ingest_instrument,
)


def test_ingest_instrument(db):
    #  TESTS WHICH SHOULD WORK

    #  test adding just telescope
    ingest_instrument(db, telescope="test")
    telescope_db = (
        db.query(db.Telescopes).filter(db.Telescopes.c.telescope == "test").table()
    )
    assert len(telescope_db) == 1
    assert telescope_db["telescope"][0] == "test"

    #  test adding new telescope, instrument, and mode
    tel_test = "test4"
    inst_test = "test5"
    mode_test = "test6"
    ingest_instrument(db, telescope=tel_test, instrument=inst_test, mode=mode_test)
    telescope_db = (
        db.query(db.Telescopes).filter(db.Telescopes.c.telescope == tel_test).table()
    )
    instrument_db = (
        db.query(db.Instruments)
        .filter(
            and_(
                db.Instruments.c.mode == mode_test,
                db.Instruments.c.instrument == inst_test,
                db.Instruments.c.telescope == tel_test,
            )
        )
        .table()
    )
    assert len(telescope_db) == 1, "Missing telescope insert"
    assert telescope_db["telescope"][0] == tel_test
    assert len(instrument_db) == 1
    assert instrument_db["instrument"][0] == inst_test
    assert instrument_db["mode"][0] == mode_test

    #  test adding common mode name for new telescope, instrument
    tel_test = "test4"
    inst_test = "test5"
    mode_test = "Prism"
    print(db.query(db.Telescopes).table())
    print(db.query(db.Instruments).table())
    ingest_instrument(db, telescope=tel_test, instrument=inst_test, mode=mode_test)
    mode_db = (
        db.query(db.Instruments)
        .filter(
            and_(
                db.Instruments.c.mode == mode_test,
                db.Instruments.c.instrument == inst_test,
                db.Instruments.c.telescope == tel_test,
            )
        )
        .table()
    )
    assert len(mode_db) == 1
    assert mode_db["mode"][0] == mode_test

    #  TESTS WHICH SHOULD FAIL
    #  test with no variables provided
    with pytest.raises(AstroDBError) as error_message:
        ingest_instrument(db)
    assert "Telescope, Instrument, and Mode must be provided" in str(
        error_message.value
    )

    #  test with mode but no instrument or telescope
    with pytest.raises(AstroDBError) as error_message:
        ingest_instrument(db, mode="test")
    assert "Telescope, Instrument, and Mode must be provided" in str(
        error_message.value
    )
