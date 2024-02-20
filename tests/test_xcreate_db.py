import pytest
import os
import sys
from astrodbkit2.astrodb import create_database, Database

sys.path.append("./tests/astrodb-template-db/")
from schema.schema_template import *  # import the schema of the template database

DB_NAME = "tests/testdb.sqlite"
DB_PATH = "tests/astrodb-template-db/data"


# Load the database for use in tests
@pytest.fixture(scope="module")
def db():
    # Create a fresh temporary database and assert it exists
    if os.path.exists(DB_NAME):
        os.remove(DB_NAME)
        print(f"Removed existing database at {DB_NAME}")
    connection_string = "sqlite:///" + DB_NAME
    create_database(connection_string)
    print(f"Created new database at {DB_NAME}")
    assert os.path.exists(DB_NAME)

    # Connect to the new database and confirm it has the Sources table
    db = Database(connection_string)
    assert db
    assert "source" in [c.name for c in db.Sources.columns]

    return db


@pytest.mark.order(1)
def test_setup_db(db):
    # Add some data to the database
    ref_data = [
        {
            "reference": "Ref 1",
            "doi": "10.1093/mnras/staa1522",
            "bibcode": "2020MNRAS.496.1922B",
        },
        {"reference": "Ref 2", "doi": "Doi2", "bibcode": "2012yCat.2311....0C"},
        {"reference": "Burn08", "doi": "Doi3", "bibcode": "2008MNRAS.391..320B"},
    ]

    source_data = [
        {
            "source": "Fake 1",
            "ra_deg": 9.0673755,
            "dec_deg": 18.352889,
            "reference": "Ref 1",
        },
        {
            "source": "Fake 2",
            "ra_deg": 9.0673755,
            "dec_deg": 18.352889,
            "reference": "Ref 1",
        },
        {
            "source": "Fake 3",
            "ra_deg": 9.0673755,
            "dec_deg": 18.352889,
            "reference": "Ref 2",
        },
    ]

    with db.engine.connect() as conn:
        conn.execute(db.Publications.insert().values(ref_data))
        conn.execute(db.Sources.insert().values(source_data))
        conn.commit()
