import logging
import os
import sys

import pytest

sys.path.append("./tests/astrodb-template-db/")
import sqlalchemy as sa
import yaml
from astrodbkit.astrodb import Database
from felis.datamodel import Schema
from felis.metadata import MetaDataBuilder
from schema.schema_template import *  # import the schema of the template database
from schema.schema_template import REFERENCE_TABLES
from sqlalchemy import create_engine

from astrodb_utils import load_astrodb

logger = logging.getLogger("AstroDB")

DB_NAME = "tests/test-template-db.sqlite"
DB_PATH = "tests/astrodb-template-db/data"


# load the template database for use by the tests
# @pytest.fixture(scope="session", autouse=True)
# def db():
#     db = load_astrodb(
#         DB_NAME, data_path=DB_PATH, recreatedb=True, reference_tables=REFERENCE_TABLES
#     )
#     # Use the default reference tables until astrodb-template-db PR #39 is merged

#     logger.info("Loaded SIMPLE database using db function in conftest")

#     return db

@pytest.fixture(scope="session", autouse=True)
def db():
    # Build test database with felis schema
    SCHEMA_NAME = "astrodb"
    CONNECTION_STRING = "sqlite:///" + DB_NAME

    data = yaml.safe_load(open("tests/astrodb-template-db/schema/schema.yaml", "r"))
    schema = Schema.model_validate(data)

    # Remove any existing copy of the test database
    if os.path.exists(DB_NAME):
        os.remove(DB_NAME)

    # Using test file for sqlite; in-memory does not preseve inserts
    engine = create_engine(CONNECTION_STRING)

    # Workaround for SQLite since it doesn't support schema
    with engine.begin() as conn:
        conn.execute(sa.text(f"ATTACH '{DB_NAME}' AS {SCHEMA_NAME}"))

    # Create database from Felis schema
    metadata = MetaDataBuilder(schema).build()
    metadata.create_all(bind=engine)

    # Use AstroDB Database object
    db = Database(CONNECTION_STRING, reference_tables=REFERENCE_TABLES)

    # Load database
    db.load_database(DB_PATH)

    # Confirm DB has been created
    assert os.path.exists(DB_NAME)

    return db