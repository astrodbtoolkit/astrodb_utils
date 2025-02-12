import math

import pytest

from astrodb_utils import (
    AstroDBError,
)
from astrodb_utils.sources import (
    coords_from_simbad,
    find_source_in_db,
    ingest_source,
)

# TODO: Ingest publication just for these tests so they can be run independent of test_publications.py


@pytest.mark.parametrize(
    "source_data",
    [
        (
            {
                "source": "Apple",
                "ra": 10.0673755,
                "dec": 17.352889,
                "reference": "Refr20",
                "raise_error": True,
            }
        ),
        (
            {
                "source": "Orange",
                "ra": 12.0673755,
                "dec": -15.352889,
                "reference": "Refr20",
                "raise_error": True,
            }
        ),
        (
            {
                "source": "Banana",
                "ra": 119.0673755,
                "dec": -28.352889,
                "reference": "Refr20",
                "raise_error": True,
            }
        ),
        (
            {
                "source": "Plantain",  # should be an alt name for Banana
                "ra": 119.0673755,
                "dec": -28.352889,
                "reference": "Refr20",
                "raise_error": False,
            }
        ),
    ],
)
@pytest.mark.filterwarnings(
    "ignore::UserWarning"
)  # suppress astroquery SIMBAD warnings
def test_ingest_sources(db, source_data):
    ingest_source(
        db,
        source_data["source"],
        ra=source_data["ra"],
        dec=source_data["dec"],
        reference=source_data["reference"],
        raise_error=source_data["raise_error"],
    )

    in_database = find_source_in_db(db, source_data["source"])
    assert len(in_database) == 1


def test_find_source_in_db(db):
    search_result = find_source_in_db(
        db,
        "Apple",
        ra=10.0673755,
        dec=17.352889,
    )
    assert len(search_result) == 1
    assert search_result[0] == "Apple"

    search_result = find_source_in_db(
        db,
        "Pear",
        ra=100,
        dec=17,
    )
    assert len(search_result) == 0


def test_find_source_in_db_errors(db):
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
    ingest_source(
        db,
        "Barnard Star",
        reference="Refr20",
        raise_error=True,
        ra_col_name="ra_deg",
        dec_col_name="dec_deg",
    )

    Barnard_star = (
        db.query(db.Sources).filter(db.Sources.c.source == "Barnard Star").astropy()
    )
    assert len(Barnard_star) == 1
    assert math.isclose(Barnard_star["ra_deg"][0], 269.452, abs_tol=0.001)
    assert math.isclose(Barnard_star["dec_deg"][0], 4.6933, abs_tol=0.001)


def test_ingest_source_errors(db):
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


def test_coords_from_simbad():
    coords = coords_from_simbad("Barnard Star")
    assert math.isclose(coords.ra.deg, 269.452, abs_tol=0.001)
    assert math.isclose(coords.dec.deg, 4.6933, abs_tol=0.001)
