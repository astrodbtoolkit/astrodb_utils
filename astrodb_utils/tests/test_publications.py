import pytest

from astrodb_utils import AstroDBError
from astrodb_utils.publications import (
    find_dates_in_reference,
    find_pub_using_arxiv_id,
    find_publication,
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

    #find_publication(db,bibcode="2022arXiv220800211G" )

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


@pytest.mark.skip(reason="Need to set up mock environment for ADS_TOKEN")
def test_ingest_publication(db):
    ingest_publication(db, bibcode="2023arXiv230812107B")
    assert find_publication(db, reference="Burg24")[0]  # True


@pytest.mark.skip(reason="Need to set up mock environment for ADS_TOKEN")
def test_find_pub_using_arxix_id(db):
    name_add, bibcode_add, doi_add, description = find_pub_using_arxiv_id(
        "2023arXiv230812107B", reference=None, doi=None, ignore_ads=False
    )

    assert name_add == "Burg24"
    assert bibcode_add == "2024ApJ...962..177B"
    assert doi_add == "10.3847/1538-4357/ad206f"
    assert description == "UNCOVER: JWST Spectroscopy of Three Cold Brown Dwarfs at Kiloparsec-scale Distances"

    results = find_pub_using_arxiv_id("2022arXiv220800211G", reference=None, doi=None, ignore_ads=False)
    print(results)
    assert results[0] == "Gaia23"
    assert results[1] == "2023A&A...674A...1G"


def test_find_dates_in_reference():
    assert find_dates_in_reference("Wright_2010") == "10"
    assert find_dates_in_reference("Refr20") == "20"
