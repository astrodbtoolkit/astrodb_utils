import pytest
import sys
import logging

sys.path.append("./tests/astrodb-template-db/")
from schema.schema_template import REFERENCE_TABLES
from schema.schema_template import *  # import the schema of the template database
from astrodb_utils import load_astrodb

logger = logging.getLogger("AstroDB")


# load the template database for use by the tests
@pytest.fixture(scope="session", autouse=True)
def db():
    DB_NAME = "tests/test-template-db.sqlite"
    DB_PATH = "tests/astrodb-template-db/data"

    db = load_astrodb(
        DB_NAME, data_path=DB_PATH, recreatedb=True, reference_tables=REFERENCE_TABLES
    )
    # Use the default reference tables until astrodb-template-db PR #39 is merged

    logger.info("Loaded SIMPLE database using db function in conftest")

    return db
