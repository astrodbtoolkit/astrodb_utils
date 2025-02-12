import pytest

from astrodb_utils import AstroDBError
from astrodb_utils.publications import find_publication, ingest_publication


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

