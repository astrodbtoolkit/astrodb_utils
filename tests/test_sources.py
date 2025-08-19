import math
import re

import astropy.units as u
import pytest

from astrodb_utils import (
    AstroDBError,
)
from astrodb_utils.sources import (
    coords_from_simbad,
    find_source_in_db,
    ingest_name,
    ingest_source,
    strip_unicode_dashes,
    simbad_name_resolvable
)


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
             {
                "source": "LHS 2924", # needed for test_find_source_in_db
                "ra": None,
                "dec": None,
                "reference": "Prob83",
                "raise_error": False,
            }
            
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

    search_result = find_source_in_db(db, "LHS 2924")
    assert search_result[0] == "LHS 2924"

    search_result = find_source_in_db(db, "LHS 292", fuzzy=False)
    assert len(search_result) == 0

    search_result = find_source_in_db(db, "LHS 292", fuzzy=True)
    assert (
        search_result[0] == "LHS 2924"
    )  # This is wrong and a result of fuzzy matching


def test_find_source_in_db_with_coords(db):
    ingest_source(
        db,
        "2MASS J04470652-1946392",
        reference="Cutr03",
    )

    source = "2MASS J04470652-1946392"
    ra_wrong = 68.8966272
    dec_wrong = 21.2552596

    search_result = find_source_in_db(
        db,
        source,
        ra=ra_wrong,
        dec=dec_wrong,
    )
    assert len(search_result) == 0

    search_result = find_source_in_db(
        db,
        source,
        ra=71.8, 
        dec=-19.8 
    )
    assert len(search_result) == 0  # coords not within 60 arcsec

    search_result = find_source_in_db(
        db,
        source,
        ra=71.8, 
        dec=-19.8,
        search_radius=83*u.arcsec,
    )
    assert len(search_result) == 1  # coords are within 83 arcsec


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

    with pytest.raises(AstroDBError) as error_message:
        find_source_in_db(
            db,
            "sirius",
            ra_col_name="bad_column_name",
            dec_col_name="bad_column_name",
        )
    assert "column names used in the Sources table" in str(error_message)


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


def test_ingest_name(db):
    result = ingest_name(db, "TWA 26", "WISE J113951.07-315921.6")
    assert result == "WISE J113951.07-315921.6"

    # try to ingest names that are already in the database
    result = ingest_name(db, "Gl 229b", "HD 42581b", raise_error=False)
    assert result is None

    with pytest.raises(AstroDBError) as error_message:
        ingest_name(db, "Gl 229b", "HD 42581b", raise_error=True)
        assert "Other name is already present." in str(error_message.value)


@pytest.mark.parametrize('input,expected', [
    ('CWISE J221706.28–145437.6', 'CWISE J221706.28-145437.6'), #en dash 2013
    ('2MASS J20115649—6201127', '2MASS J20115649-6201127'), # em dash 2014
    ('1234−5678', '1234-5678'),  # minus sign 2212
    ('9W34‒aou', '9W34-aou'), # figure dash 2012
    ('should-work', 'should-work'), # no unicode dashes➖➖
])
def test_strip_unicode_dashes(input, expected):
    result = strip_unicode_dashes(input)
    assert result == expected

@pytest.mark.parametrize('input,ra, dec, expected, expected_names', [
    #2 cases whose names are NOT in the database
    ("Apple", 144.395292,29.528028, False, 
     ["2MASSI J0937347+293142", "WISE J093742.35+293220.7"]),

    ("Banana", 3.9888,4.2511, False, 
     ["HD 1160", "HD 1160B", "HD 1160C", "TYC 5-669-1"]),

    #2 cases whose names are in the database
    ("2MASS J07222760-0540384",110.6149995,-5.677333, True, 
     ["2MASS J07222760-0540384", 
    "[BGM2011b] J072227.56-054034.4",
    "[BGM2011b] J072227.79-054034.7",
    "[BGM2011b] J072227.64-054033.0",
    "WISE J072227.27-054029.9",
    "[BGM2011b] J072227.02-054039.2",
    "[BGM2011b] J072227.28-054030.0",
    "[BGM2011b] J072227.34-054026.8",
    "[BGM2011b] J072226.97-054029.4",
    "UCAC3 169-73338",
    "TYC 4829-156-1"]),

    ("ULAS J000734.90+011247.1", 1.8957, 1.2132, True, 
     ["ULAS J000734.90+011247.1", 
      "2MASS J00073939+0113049", 
      "SDSS J000741.43+011209.4", 
     "SDSS J000729.23+011346.4", 
     "2MASS J00073597+0110548"])
])

def test_simbad_resolvable_names(input,ra,dec,expected, expected_names):
    result = simbad_name_resolvable(input, ra, dec)
    
    #SIMBAD returns actual names with weird white spaces... so remove all white spaces from both lists of names
    # Remove all spaces from actual names
    actual_names_list = set([re.sub(r'\s+', '', str(name)) for name in result[1]])

    # Remove all spaces from expected names  
    expected_names_list = set([re.sub(r'\s+', '', name) for name in expected_names])

    assert result[0] == expected
    assert actual_names_list == expected_names_list

