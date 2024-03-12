import pytest
import os
import sys
import logging
from astrodbkit2.astrodb import create_database, Database

sys.path.append("./tests/astrodb-template-db/")
from schema.schema_template import *  # import the schema of the template database

logger = logging.getLogger("AstroDB")


# load the template database for use by the tests
@pytest.fixture(scope="session", autouse=True)
def db():
    DB_NAME = "tests/test-template-db.sqlite"
    DB_PATH = "tests/astrodb-template-db/data"

    # Create a fresh temporary database and assert it exists
    if os.path.exists(DB_NAME):
        os.remove(DB_NAME)
    connection_string = "sqlite:///" + DB_NAME
    create_database(connection_string)

    # Connect to the new database instance
    db = Database(connection_string)
    # Load data into an in-memory sqlite database first, for performance
    db = Database("sqlite://")  # creates and connects to a temporary in-memory database
    db.load_database(
        DB_PATH, verbose=False
    )  # loads the data from the data files into the database
    db.dump_sqlite(DB_NAME)  # dump in-memory database to file
    db = Database(
        "sqlite:///" + DB_NAME
    )  # replace database object with new file version
    logger.info("Loaded SIMPLE database using db function in conftest")

    return db
