import os
import sys

import pytest

from astrodb_utils import load_astrodb, logger
from astrodb_utils.publications import ingest_publication
from astrodb_utils.sources import ingest_source

logger.setLevel("DEBUG")

sys.path.append("./tests/astrodb-template-db/")

DB_NAME = "tests/test-template-db.sqlite"
DB_PATH = "tests/astrodb-template-db/data"
SCHEMA_PATH = "tests/astrodb-template-db/schema/schema.yaml"
CONNECTION_STRING = "sqlite:///" + DB_NAME

# load the template database for use by the tests
@pytest.fixture(scope="session", autouse=True)
def db():
    db = load_astrodb(
        DB_NAME, data_path=DB_PATH, recreatedb=True, felis_schema=SCHEMA_PATH
    )

    # Confirm file was created
    assert os.path.exists(DB_NAME)

    logger.info("Loaded AstroDB Template database using load_astrodb function in conftest.py")

    ingest_publication(db, doi="10.1086/161442") # Prob83

    ingest_publication(
        db,
        reference="Refr20",
        bibcode="2020MNRAS.496.1922B",
        doi="10.1093/mnras/staa1522",
        ignore_ads=True,
    )

    ingest_source(db, "LHS 2924", reference="Prob83")

    return db


