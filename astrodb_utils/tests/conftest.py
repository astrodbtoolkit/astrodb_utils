import logging
import os
import sys

import pytest

sys.path.append("./tests/astrodb-template-db/")
from schema.schema_template import REFERENCE_TABLES

from astrodb_utils import load_astrodb

logger = logging.getLogger("AstroDB")

DB_NAME = "tests/test-template-db.sqlite"
DB_PATH = "tests/astrodb-template-db/data"
SCHEMA_PATH = "tests/astrodb-template-db/schema/schema.yaml"
CONNECTION_STRING = "sqlite:///" + DB_NAME

# load the template database for use by the tests
@pytest.fixture(scope="session", autouse=True)
def db():
    db = load_astrodb(
        DB_NAME, data_path=DB_PATH, recreatedb=True, reference_tables=REFERENCE_TABLES, felis_schema=SCHEMA_PATH
    )

    # Confirm file was created
    assert os.path.exists(DB_NAME)

    logger.info("Loaded SIMPLE database using db function in conftest")

    return db