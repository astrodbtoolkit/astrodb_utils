import logging
import os

import pytest
from git import Repo

import astrodb_utils
from astrodb_utils import load_astrodb
from astrodb_utils.publications import ingest_publication

logger = logging.getLogger(__name__)

# # TODO: Figure out how to import ReferenceTables
# REFERENCE_TABLES = [
#     "Publications",
#     "Telescopes",
#     "Instruments",
#     "PhotometryFilters",
#     "Versions",
#     "RegimeList",
#     "AssociationList",
#     "SourceTypeList",
#     "ParameterList",
#     "CompanionList",
# ]


#DB_NAME = "tests/test-template-db.sqlite"
#DB_PATH = "astrodb-template-db/data"
#SCHEMA_PATH = "astrodb-template-db/schema/schema.yaml"
#CONNECTION_STRING = "sqlite:///" + DB_NAME

# Make sure the astrodb-template-db repository is cloned and updated
template_schema_path = os.path.join("tests", "astrodb-template-db")
if os.path.exists(template_schema_path):
    template_repo = Repo(template_schema_path)
    try:
        template_repo.git.reset("--hard")
        template_repo.remotes.origin.pull()
    except Exception as e:
        print(f"Error updating template schema repository: {e}")
        print(f"Using existing local copy of the template schema: {template_schema_path}")
else:
    url = "https://github.com/astrodbtoolkit/astrodb-template-db.git"
    try:
        Repo.clone_from(url, template_schema_path, branch="main")
    except Exception as e:
        print(f"Error cloning template schema repository: {e}")
        print(f"Please ensure the repository exists and is accessible: {url}")


# load the template database for use by the tests
@pytest.fixture(scope="session", autouse=True)
def db():
    logger.info(f"Using version {astrodb_utils.__version__} of astrodb_utils")
    db_path = os.path.join(template_schema_path, "schema")

    db = load_astrodb(db_path)

    # Confirm file was created
    assert os.path.exists("schema.sqlite"), "Database file 'schema.sqlite' was not created."

    logger.info("Loaded AstroDB Template database using load_astrodb function in conftest.py")

    ingest_publication(
        db,
        reference="Refr20",
        bibcode="2020MNRAS.496.1922B",
        doi="10.1093/mnras/staa1522",
        ignore_ads=True,
    )

    ingest_publication(db, doi="10.1086/161442", reference="Prob83", ignore_ads=True)

    return db


