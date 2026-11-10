import logging
import os

import pytest

import astrodb_utils
from astrodb_utils import build_db_from_json
from astrodb_utils.publications import ingest_publication
from astrodb_utils.utils import select_simbad_mirror

logger = logging.getLogger(__name__)

# Make sure the astrodb-template-db repository is cloned and updated
# Use `git clone https://github.com/astrodbtoolkit/astrodb-template-db.git` in the tests directory
template_schema_path = os.path.join("tests", "astrodb-template-db")


def pytest_collection_modifyitems(config, items):
    """Pick a working SIMBAD mirror (Strasbourg, Harvard, IDIA); skip `simbad` tests if none respond."""
    simbad_items = [item for item in items if item.get_closest_marker("simbad")]
    if simbad_items and select_simbad_mirror() is None:  # pragma: no cover (only when all mirrors are down)
        for item in simbad_items:
            item.add_marker(pytest.mark.skip(reason="No SIMBAD mirror is reachable"))


# load the template database for use by the tests
@pytest.fixture(scope="session", autouse=True)
def db():
    logger.info(f"Using version {astrodb_utils.__version__} of astrodb_utils")

    db = build_db_from_json(
        settings_file="database.toml",
        base_path=template_schema_path,
        db_name="tests/astrodb-template-tests",
    )

    # Confirm file was created
    assert os.path.exists("tests/astrodb-template-tests.sqlite"), (
        "Database file 'tests/astrodb-template-tests.sqlite' was not created."
    )

    logger.info("Loaded AstroDB Template database using build_db_from_json function in conftest.py")

    ingest_publication(
        db,
        reference="Refr20",
        bibcode="2020MNRAS.496.1922B",
        doi="10.1093/mnras/staa1522",
        ignore_ads=True,
    )

    ingest_publication(db, doi="10.1086/161442", reference="Prob83", ignore_ads=True)

    return db
