import pytest

from astrodb_utils import AstroDBError
from astrodb_utils.publications import (
    _find_dates_in_reference,
    _search_ads,
    check_ads_token,
    find_publication,
    get_db_publication,
    ingest_publication,
)


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

    assert find_publication(db, reference=None) == (False, 0)

    # Test with a non-existent arxiv ID
    assert find_publication(db, bibcode="2023arXiv2308121074B") == (False, 0)

    # find_publication(db,bibcode="2022arXiv220800211G" )


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

    ingest_publication(db, bibcode="2024ApJ...962..177B", ignore_ads=True)


def test_ingest_publication(db):
    ingest_publication(
        db, reference="test05", bibcode="2024ApJ...962..177B", ignore_ads=True
    )
    assert find_publication(db, reference="test05")[0]  # True

    ingest_publication(db, reference="test10", doi="10.1086/513700", ignore_ads=True)
    assert find_publication(db, reference="test10")[0]  # True


@pytest.mark.skipif(check_ads_token() is False, reason="ADS_TOKEN not set")
def test_search_ads_using_arxix_id(db):
    name_add, bibcode_add, doi_add, description = _search_ads(
        "2023arXiv230812107B",
        query_type="arxiv",
        reference=None,
    )

    assert name_add == "Burg24"
    assert bibcode_add == "2024ApJ...962..177B"
    assert doi_add == "10.3847/1538-4357/ad206f"
    assert (
        description
        == "UNCOVER: JWST Spectroscopy of Three Cold Brown Dwarfs at Kiloparsec-scale Distances"
    )

    results = _search_ads(
        "2022arXiv220800211G",
        query_type="arxiv",
        reference=None,
    )
    assert results[0] == "Gaia23"
    assert results[1] == "2023A&A...674A...1G"


@pytest.mark.skipif(check_ads_token() is False, reason="ADS_TOKEN not set")
def test_search_ads_using_doi():
    results = _search_ads("10.1093/mnras/staa1522", query_type="doi", reference=None)
    assert results[0] == "Belo20"
    assert results[1] == "2020MNRAS.496.1922B"
    assert results[2] == "10.1093/mnras/staa1522"
    assert results[3] == "Unresolved stellar companions with Gaia DR2 astrometry"

    results = _search_ads(
        "10.3847/1538-4357/ad206f", query_type="doi", reference="test03"
    )
    assert results[0] == "test03"
    assert results[1] == "2024ApJ...962..177B"
    assert results[2] == "10.3847/1538-4357/ad206f"
    assert (
        results[3]
        == "UNCOVER: JWST Spectroscopy of Three Cold Brown Dwarfs at Kiloparsec-scale Distances"
    )


@pytest.mark.skipif(check_ads_token() is False, reason="ADS_TOKEN not set")
def test_search_ads_using_bibcode():
    results = _search_ads(
        "2020MNRAS.496.1922B", query_type="bibcode", reference="Blah98"
    )
    assert results[0] == "Blah98"
    assert results[1] == "2020MNRAS.496.1922B"
    assert results[2] == "10.1093/mnras/staa1522"
    assert results[3] == "Unresolved stellar companions with Gaia DR2 astrometry"


def test_find_dates_in_reference():
    assert _find_dates_in_reference("Wright_2010") == "10"
    assert _find_dates_in_reference("Refr20") == "20"

@pytest.mark.parametrize(
    "input, db_ref",
    [
       ("Cutr03","Cutr03"),
       ("CUTR03","Cutr03"),
       ("cutr03","Cutr03"),
       ("GAIA23","Gaia23"),
    ],
)
def test_get_db_publication(db, input, db_ref):
    # Test with a valid reference
    result = get_db_publication(db, reference=input)
    assert result == db_ref

def test_get_db_publication_invalid(db):
    with pytest.raises(AstroDBError) as error_message:
        get_db_publication(db, reference="Cruz25")
        
    assert "Reference not found" in str(error_message.value)
    
    result = get_db_publication(db, reference="Cruz25", raise_error=False)
    assert result is None