import pytest
import math
from astropy.table import Table
from sqlalchemy import and_
from astrodb_utils import (
    AstroDBError,
    find_publication,
    find_source_in_db,
    ingest_publication,
    ingest_source,
    ingest_sources,
    ingest_instrument,
)


def test_ingest_publications(db):
    # add a made up publication and make sure it's there
    ingest_publication(
        db,
        reference="Refr20",
        bibcode="2020MNRAS.496.1922B",
        doi="10.1093/mnras/staa1522",
        ignore_ads=True,
    )
    assert (
        db.query(db.Publications)
        .filter(db.Publications.c.reference == "Refr20")
        .count()
        == 1
    )


@pytest.mark.filterwarnings(
    "ignore::UserWarning"
)  # suppress astroquery SIMBAD warnings
def test_ingest_sources(db):
    # TODO: Test adding an alt name
    source_data1 = Table(
        [
            {
                "source": "Apple",
                "ra": 10.0673755,
                "dec": 17.352889,
                "reference": "Refr20",
            },
            {
                "source": "Orange",
                "ra": 12.0673755,
                "dec": -15.352889,
                "reference": "Refr20",
            },
            {
                "source": "Banana",
                "ra": 119.0673755,
                "dec": -28.352889,
                "reference": "Refr20",
            },
        ]
    )

    ingest_sources(
        db,
        source_data1["source"],
        ras=source_data1["ra"],
        decs=source_data1["dec"],
        references=source_data1["reference"],
        raise_error=True,
    )
    assert db.query(db.Sources).filter(db.Sources.c.source == "Apple").count() == 1
    assert db.query(db.Sources).filter(db.Sources.c.source == "Orange").count() == 1
    assert db.query(db.Sources).filter(db.Sources.c.source == "Banana").count() == 1


def test_find_source_in_db(db):
    search_result = find_source_in_db(
        db,
        "Apple",
        ra=10.0673755,
        dec=17.352889,
        ra_col_name="ra_deg",
        dec_col_name="dec_deg",
    )
    assert len(search_result) == 1
    assert search_result[0] == "Apple"

    search_result = find_source_in_db(
        db,
        "Pear",
        ra=100,
        dec=17,
        ra_col_name="ra_deg",
        dec_col_name="dec_deg",
    )
    assert len(search_result) == 0

    with pytest.raises(KeyError) as error_message:
        find_source_in_db(
            db,
            "Pear",
            ra=100,
            dec=17,
            ra_col_name="bad_column_name",
            dec_col_name="bad_column_name",
        )
    assert "bad_column_name" in str(error_message)


@pytest.mark.filterwarnings(
    "ignore::UserWarning"
)  # suppress astroquery SIMBAD warnings
def test_ingest_source(db):
    ingest_source(db, "Barnard Star", reference="Refr20", raise_error=True)

    Barnard_star = (
        db.query(db.Sources).filter(db.Sources.c.source == "Barnard Star").astropy()
    )
    assert len(Barnard_star) == 1
    assert math.isclose(Barnard_star["ra_deg"][0], 269.452, abs_tol=0.001)
    assert math.isclose(Barnard_star["dec_deg"][0], 4.6933, abs_tol=0.001)

    source_data8 = {
        "source": "Fake 8",
        "ra": 9.06799,
        "dec": 18.352889,
        "reference": "Ref 4",
    }
    with pytest.raises(AstroDBError) as error_message:
        ingest_source(
            db,
            source_data8["source"],
            ra=source_data8["ra"],
            dec=source_data8["dec"],
            reference=source_data8["reference"],
            raise_error=True,
        )
        assert "not in Publications table" in str(error_message.value)

    source_data5 = {
        "source": "Fake 5",
        "ra": 9.06799,
        "dec": 18.352889,
        "reference": "",
    }
    with pytest.raises(AstroDBError) as error_message:
        ingest_source(
            db,
            source_data5["source"],
            ra=source_data5["ra"],
            dec=source_data5["dec"],
            reference=source_data5["reference"],
            raise_error=True,
        )
        assert "blank" in str(error_message.value)

    with pytest.raises(AstroDBError) as error_message:
        ingest_source(db, "NotinSimbad", reference="Ref 1", raise_error=True)
        assert "Coordinates are needed" in str(error_message.value)

    with pytest.raises(AstroDBError) as error_message:
        ingest_source(
            db,
            "Fake 1",
            ra=11.0673755,
            dec=18.352889,
            reference="Ref 1",
            raise_error=True,
        )
        assert "already exists" in str(error_message.value)


def test_find_publication(db):
    assert not find_publication(db)[0]  # False
    assert find_publication(db, reference="Refr20")[0]  # True
    assert find_publication(db, reference="Refr20", doi="10.1093/mnras/staa1522")[
        0
    ]  # True
    doi_search = find_publication(db, doi="10.1093/mnras/staa1522")
    assert doi_search[0]  # True
    assert doi_search[1] == "Refr20"
    bibcode_search = find_publication(db, bibcode="2020MNRAS.496.1922B")
    assert bibcode_search[0]  # True
    assert bibcode_search[1] == "Refr20"

    # Fuzzy matching working!
    assert find_publication(db, reference="Wright_2010") == (1, "Wrig10")


@pytest.mark.skip(reason="Fuzzy matching not perfect yet. #27")
# TODO: find publication only finds one of the Gaia publications
def test_find_publication_fuzzy(db):
    multiple_matches = find_publication(db, reference="Gaia")
    print(multiple_matches)
    assert not multiple_matches[0]  # False, multiple matches
    assert multiple_matches[1] == 2  # multiple matches


def test_ingest_publication_errors(db):
    # should fail if trying to add a duplicate record
    with pytest.raises(AstroDBError) as error_message:
        ingest_publication(db, reference="Refr20", bibcode="2020MNRAS.496.1922B")
    assert " similar publication already exists" in str(error_message.value)
    # TODO - Mock environment  where ADS_TOKEN is not set. #117


def test_ingest_instrument(db):
    #  TESTS WHICH SHOULD WORK

    #  test adding just telescope
    ingest_instrument(db, telescope="test")
    telescope_db = (
        db.query(db.Telescopes).filter(db.Telescopes.c.telescope == "test").table()
    )
    assert len(telescope_db) == 1
    assert telescope_db["telescope"][0] == "test"

    # No longer supported just adding an instrument without a mode
    #  test adding telescope and instrument
    # tel_test = 'test2'
    # inst_test = 'test3'
    # ingest_instrument(db, telescope=tel_test, instrument=inst_test)
    # telescope_db = db.query(db.Telescopes).
    #   filter(db.Telescopes.c.telescope == tel_test).table()
    # instrument_db = db.query(db.Instruments).
    #   filter(db.Instruments.c.instrument == inst_test).table()
    # assert len(telescope_db) == 1
    # assert telescope_db['telescope'][0] == tel_test
    # assert len(instrument_db) == 1
    # assert instrument_db['instrument'][0] == inst_test

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
